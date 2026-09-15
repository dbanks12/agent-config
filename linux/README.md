# Codex sandbox on Ubuntu

## Failure

Codex commands fail before execution with:

```text
bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted
```

On the affected host, Ubuntu enables `kernel.apparmor_restrict_unprivileged_userns=1`.
The system Bubblewrap executable has no AppArmor profile that allows user namespaces.
AppArmor assigns `unprivileged_userns` and denies `setpcap` and `net_admin` within the new namespace.
Bubblewrap cannot configure loopback, so Codex cannot execute sandboxed commands.

This affects direct Codex launches and calls from Claude, including code reviews.
`--yolo` avoids the failing sandbox setup and also removes its protections.

## Install

Run this command as the normal Codex user:

```sh
./linux/install-codex-sandbox.sh
```

The script uses sudo to install and load `agent-config-bwrap` under `/etc/apparmor.d/`.
The profile permits `/usr/bin/bwrap` to create user namespaces.
This exception applies to all callers of that executable.
Codex still sets its filesystem and network limits through Bubblewrap.
The system-wide namespace restriction stays enabled.
AppArmor loads the installed profile on subsequent boots.

The script then tests read-only and workspace-write sandboxes as the normal user.
The tests require successful reads, correct write boundaries, and blocked access to a live host network listener.
They make no model API calls.

## Diagnose and verify

Run the sandbox directly:

```sh
codex sandbox -c 'sandbox_mode="read-only"' -- /bin/true
```

Read the corresponding kernel denials:

```sh
journalctl -k --since '5 minutes ago' --no-pager | rg 'apparmor=.*(userns_create|DENIED)'
```

Run the isolation tests:

```sh
python3 linux/test-codex-sandbox.py
```

This fix targets the system `/usr/bin/bwrap` path confirmed in the kernel audit log.
If another executable fails, inspect its audit entry before changing the profile.
Container seccomp restrictions and inherited parent sandboxes require separate diagnosis.

See [Ubuntu's AppArmor documentation](https://documentation.ubuntu.com/security/security-features/privilege-restriction/apparmor/#apparmor-unprivileged-user-namespace-restrictions).

## Remove

Unload the profile:

```sh
sudo apparmor_parser --remove /etc/apparmor.d/agent-config-bwrap
```

Remove the installed file:

```sh
sudo rm /etc/apparmor.d/agent-config-bwrap
```

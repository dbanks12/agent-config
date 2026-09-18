const $ = id => document.getElementById(id);
let state, current, index = 0, answers = Object.create(null), sending = false, revision = '';
const storageKey = `grill-me:${location.pathname}`;
let storageWarning = '';
function restore() {
  try { return JSON.parse(localStorage.getItem(storageKey) || '{}'); }
  catch { storageWarning = 'Browser draft storage is unavailable. Keep this tab open until you send the section.'; return {}; }
}
function save() {
  try { localStorage.setItem(storageKey, JSON.stringify({section: current.id, index, answers})); }
  catch { storageWarning = 'Browser draft storage is unavailable. Keep this tab open until you send the section.'; }
  $('connection').textContent = storageWarning;
}
async function api(path, body) {
  const response = await fetch(path, {
    cache: 'no-store',
    ...(body ? {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)} : {})
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'The request failed. Try again.');
  return data;
}
function node(tag, text, className) {
  const el = document.createElement(tag);
  el.textContent = text;
  if (className) el.className = className;
  return el;
}
function renderHistory() {
  const expanded = new Set([...$('history').children].filter(el => el.open).map(el => el.dataset.id));
  $('history').replaceChildren();
  for (const section of state.sections.filter(s => s.answers)) {
    const details = document.createElement('details');
    details.dataset.id = section.id;
    details.open = expanded.has(section.id);
    const summary = node('summary', `${section.title} · ${section.questions.length} decisions`);
    const shorthand = section.questions.map(q => {
      const a = section.answers[q.id];
      return `${q.title}: ${a.mode === 'accepted' ? (a.notes ? `accepted · ${a.notes.replace(/\s+/g, ' ').slice(0, 65)}` : 'accepted') : a.text.replace(/\s+/g, ' ').slice(0, 65)}`;
    }).join(' · ');
    summary.append(node('span', ` — ${shorthand.slice(0, 220)}${shorthand.length > 220 ? '…' : ''}`));
    details.append(summary);
    for (const q of section.questions) {
      const entry = node('div', '', 'past-answer');
      entry.append(node('strong', q.title), node('p', q.body, 'prose muted'),
        node('p', `Recommendation: ${q.recommendation}`, 'prose muted'),
        node('p', `${section.answers[q.id].mode === 'accepted' ? 'Accepted: ' : 'Your response: '}${section.answers[q.id].text}`, 'prose'));
      if (section.answers[q.id].notes) entry.append(node('p', `Your notes: ${section.answers[q.id].notes}`, 'prose'));
      details.append(entry);
    }
    $('history').append(details);
  }
}
function answered(q) { return Boolean(answers[q.id]?.text?.trim()); }
function renderProgress() {
  const done = current ? current.questions.filter(answered).length : 0;
  const total = current?.questions.length || 0;
  const remaining = state.remaining;
  $('progress').max = total || 1;
  $('progress').value = total ? done : 1;
  const estimate = remaining ? `About ${remaining.min}–${remaining.max} more questions after this section. Estimates change as decisions become clear.` : 'The agent will estimate the remaining questions.';
  $('estimate').textContent = state.finished ? 'All sections complete.' : `${total ? `${done} of ${total} answered in this section. ` : ''}${estimate}`;
  $('submit').disabled = sending || !current?.questions.every(answered);
  $('count').textContent = `${done} / ${total} answered`;
  if (!current) return;
  [...$('nav').children].forEach((button, i) => {
    button.classList.toggle('answered', answered(current.questions[i]));
    button.textContent = `${i + 1}${answered(current.questions[i]) ? ' ✓' : ''}`;
  });
}
function renderQuestion(focus = false) {
  const q = current.questions[index];
  $('question-number').textContent = `Question ${index + 1} of ${current.questions.length}`;
  $('question-title').textContent = q.title;
  $('question-body').textContent = q.body;
  $('recommendation').textContent = q.recommendation;
  $('response').value = answers[q.id]?.mode === 'custom' ? answers[q.id].text : answers[q.id]?.notes || '';
  renderAnswerStatus();
  $('previous').disabled = index === 0;
  $('next').hidden = index === current.questions.length - 1;
  $('submit').hidden = !$('next').hidden;
  [...$('nav').children].forEach((button, i) => {
    if (i === index) button.setAttribute('aria-current', 'step');
    else button.removeAttribute('aria-current');
  });
  renderProgress();
  if (focus) $('question-title').focus();
}
function renderAnswerStatus() {
  const a = answers[current.questions[index].id];
  const accepted = a?.mode === 'accepted';
  $('accept').textContent = accepted ? '✓ Recommendation accepted' : 'Accept recommendation';
  $('accept').setAttribute('aria-pressed', String(accepted));
  $('answer-status').textContent = accepted ? (a.notes?.trim() ? 'Recommendation accepted with your notes.' : 'Recommendation selected. Send the section when you are ready.') : a?.text?.trim() ? (storageWarning ? 'Response kept in this tab. Send the section when you are ready.' : 'Draft saved in this browser. Send the section when you are ready.') : 'Choose the recommendation or enter a response.';
}
function go(next) { index = next; save(); renderQuestion(true); }
function render(nextState) {
  state = nextState;
  try { localStorage.setItem(`${storageKey}:state`, JSON.stringify(state)); } catch {}
  const recovery = state.recovery;
  $('recovery').hidden = !recovery;
  if (recovery) {
    $('resume-command').textContent = recovery.resume_command;
    $('resume-prompt').textContent = recovery.prompt;
    $('restart-command').textContent = recovery.restart_command;
    $('transcript-path').textContent = recovery.transcript_path;
    $('answers-path').textContent = recovery.answers_path;
    $('picker-prompt').hidden = recovery.exact_session;
    $('resume-note').textContent = recovery.exact_session
      ? `This command resumes the original ${recovery.agent === 'codex' ? 'Codex' : 'Claude'} session and asks it to read your stored answers. If that session is still open, continue there.`
      : 'The session ID was unavailable. Select the original session in the picker, then paste the message below.';
  }
  $('title').textContent = state.title;
  $('phase').textContent = state.finished ? 'Complete' : state.sections.some(s => !s.answers) ? 'Your turn' : 'Agent’s turn';
  renderHistory();
  const next = state.sections.find(s => !s.answers);
  $('active').hidden = !next || state.finished;
  $('waiting').hidden = Boolean(next) || state.finished;
  $('completion').hidden = !state.finished;
  $('summary').textContent = state.summary || '';
  if (next) {
    if (current?.id !== next.id) {
      current = next;
      const draft = restore();
      answers = Object.assign(Object.create(null), draft.section === next.id ? draft.answers || {} : {});
      index = draft.section === next.id ? Math.max(0, Math.min(Number(draft.index) || 0, next.questions.length - 1)) : 0;
      $('section-title').textContent = next.title;
      $('nav').replaceChildren(...next.questions.map((q, i) => {
        const button = node('button', String(i + 1));
        button.type = 'button';
        button.setAttribute('aria-label', `Question ${i + 1}: ${q.title}`);
        button.onclick = () => go(i);
        return button;
      }));
      renderQuestion();
    }
  } else current = null;
  renderProgress();
}
$('copy-resume').onclick = async () => {
  try {
    await navigator.clipboard.writeText($('resume-command').textContent);
    $('copy-resume').textContent = 'Copied';
  } catch {
    $('error').textContent = 'Clipboard access is unavailable. Select and copy the command above.';
  }
};
function advanceAnswer() {
  if (!answered(current.questions[index])) return;
  if (index < current.questions.length - 1) go(index + 1);
  else {
    const unanswered = current.questions.findIndex(q => !answered(q));
    if (unanswered >= 0) go(unanswered);
    else $('submit').focus();
  }
}
$('accept').onclick = () => {
  const q = current.questions[index];
  if (answers[q.id]?.mode === 'accepted') {
    if (answers[q.id].notes?.trim()) answers[q.id] = {mode: 'custom', text: answers[q.id].notes};
    else delete answers[q.id];
    save(); renderAnswerStatus(); renderProgress();
    return;
  }
  answers[q.id] = {mode: 'accepted', text: q.recommendation};
  $('response').value = '';
  save(); renderAnswerStatus(); renderProgress();
  advanceAnswer();
};
$('accept-notes').onclick = () => {
  const notes = $('response').value;
  if (!notes.trim()) {
    $('answer-status').textContent = 'Type notes above, then select Accept with notes.';
    $('response').focus();
    return;
  }
  const q = current.questions[index];
  answers[q.id] = {mode: 'accepted', text: q.recommendation, notes};
  save(); renderAnswerStatus(); renderProgress();
  advanceAnswer();
};
$('response').oninput = () => {
  const q = current.questions[index];
  const a = answers[q.id];
  if (a?.mode === 'accepted' && typeof a.notes === 'string') a.notes = $('response').value;
  else answers[q.id] = {mode: 'custom', text: $('response').value};
  save(); renderAnswerStatus(); renderProgress();
};
$('response').onkeydown = event => {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    advanceAnswer();
  }
};
$('previous').onclick = () => go(index - 1);
$('next').onclick = () => go(index + 1);
$('submit').onclick = async () => {
  if (sending || !current.questions.every(answered)) return;
  sending = true; $('active').inert = true; renderProgress(); $('error').textContent = '';
  const section = current.id;
  try {
    const nextState = await api('answers', {section, answers});
    revision = JSON.stringify(nextState);
    render(nextState);
  } catch (error) { $('error').textContent = `Could not send this section: ${error.message} Your draft is still available.`; }
  finally { sending = false; $('active').inert = false; renderProgress(); }
};
async function poll() {
  try {
    const nextState = await api('state');
    $('connection').textContent = storageWarning;
    const nextRevision = JSON.stringify(nextState);
    if (revision !== nextRevision && !sending) { revision = nextRevision; render(nextState); }
  } catch {
    $('connection').textContent = 'Connection lost. Answers remain in this tab. Ask the launching session to restart the page server.';
  } finally { setTimeout(poll, 1500); }
}
try {
  const cached = JSON.parse(localStorage.getItem(`${storageKey}:state`) || 'null');
  if (cached) render(cached);
} catch {}
poll();

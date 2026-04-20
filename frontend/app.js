/* ============================================================
   AI VoiceBot — Frontend Logic
   Handles: mic recording, waveform, API calls, UI updates
   ============================================================ */

'use strict';

const API_BASE = '';   // same origin (FastAPI serves both)

// ─── DOM refs ────────────────────────────────────────────────
const btnRecord        = document.getElementById('btn-record');
const recLabel         = document.getElementById('rec-label');
const recTimer         = document.getElementById('rec-timer');
const waveformCanvas   = document.getElementById('waveform');
const textInput        = document.getElementById('text-input');
const btnSend          = document.getElementById('btn-send');
const spinner          = document.getElementById('spinner');
const spinnerLabel     = document.getElementById('spinner-label');
const statusPill       = document.getElementById('status-pill');
const statusText       = document.getElementById('status-text');
const micRings         = document.getElementById('mic-rings');

const transcriptionEl  = document.getElementById('transcription-text');
const intentBadge      = document.getElementById('intent-badge');
const intentLabel      = document.getElementById('intent-label');
const intentPlaceholder= document.getElementById('intent-placeholder');
const confWrap         = document.getElementById('conf-wrap');
const confFill         = document.getElementById('conf-fill');
const confPct          = document.getElementById('conf-pct');
const responseTextEl   = document.getElementById('response-text');
const audioWrap        = document.getElementById('audio-wrap');
const audioPlaceholder = document.getElementById('audio-placeholder');
const responseAudio    = document.getElementById('response-audio');
const toastContainer   = document.getElementById('toast-container');

// Pipeline steps
const pipelineSteps    = {
  asr:  document.getElementById('step-asr'),
  nlp:  document.getElementById('step-nlp'),
  resp: document.getElementById('step-resp'),
  tts:  document.getElementById('step-tts'),
};

// ─── State ───────────────────────────────────────────────────
let mediaRecorder   = null;
let audioChunks     = [];
let isRecording     = false;
let timerInterval   = null;
let elapsedSeconds  = 0;
let animFrameId     = null;
let analyser        = null;
let audioCtx        = null;

// ─── Canvas ctx ──────────────────────────────────────────────
const ctx2d = waveformCanvas.getContext('2d');

// ════════════════════════════════════════════════════════════
// Health check on load
// ════════════════════════════════════════════════════════════
async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (res.ok) {
      statusPill.className = 'status-pill online';
      statusText.textContent = 'API Online';
    } else {
      throw new Error('not ok');
    }
  } catch {
    statusPill.className = 'status-pill offline';
    statusText.textContent = 'API Offline';
  }
}

checkHealth();

// ════════════════════════════════════════════════════════════
// Toast notifications
// ════════════════════════════════════════════════════════════
function showToast(message, type = 'info', duration = 3500) {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('fade-out');
    toast.addEventListener('animationend', () => toast.remove());
  }, duration);
}

// ════════════════════════════════════════════════════════════
// Pipeline step UI
// ════════════════════════════════════════════════════════════
function resetPipeline() {
  Object.values(pipelineSteps).forEach(el => {
    el.classList.remove('active', 'done');
  });
}

function setStep(stepKey, state) {  // state: 'active' | 'done'
  const el = pipelineSteps[stepKey];
  if (!el) return;
  el.classList.remove('active', 'done');
  el.classList.add(state);
}

// ════════════════════════════════════════════════════════════
// Recording Timer
// ════════════════════════════════════════════════════════════
function startTimer() {
  elapsedSeconds = 0;
  recTimer.classList.add('visible');
  updateTimerDisplay();
  timerInterval = setInterval(() => {
    elapsedSeconds++;
    updateTimerDisplay();
  }, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
  timerInterval = null;
  recTimer.classList.remove('visible');
}

function updateTimerDisplay() {
  const mins = String(Math.floor(elapsedSeconds / 60)).padStart(2, '0');
  const secs = String(elapsedSeconds % 60).padStart(2, '0');
  recTimer.textContent = `${mins}:${secs}`;
}

// ════════════════════════════════════════════════════════════
// Waveform Visualizer
// ════════════════════════════════════════════════════════════
function startWaveform(stream) {
  audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const source = audioCtx.createMediaStreamSource(stream);
  analyser = audioCtx.createAnalyser();
  analyser.fftSize = 256;
  source.connect(analyser);

  waveformCanvas.classList.add('active');
  drawWave();
}

function drawWave() {
  if (!analyser) return;

  const bufLen = analyser.frequencyBinCount;
  const data   = new Uint8Array(bufLen);
  analyser.getByteTimeDomainData(data);

  const W = waveformCanvas.width;
  const H = waveformCanvas.height;

  ctx2d.clearRect(0, 0, W, H);

  // Background
  ctx2d.fillStyle = 'rgba(15, 15, 26, 0)';
  ctx2d.fillRect(0, 0, W, H);

  // Gradient line
  const gradient = ctx2d.createLinearGradient(0, 0, W, 0);
  gradient.addColorStop(0,   '#7c4dff');
  gradient.addColorStop(0.5, '#00e5ff');
  gradient.addColorStop(1,   '#7c4dff');

  ctx2d.lineWidth   = 2.5;
  ctx2d.strokeStyle = gradient;
  ctx2d.shadowBlur  = 8;
  ctx2d.shadowColor = 'rgba(124,77,255,0.6)';

  ctx2d.beginPath();
  const sliceW = W / bufLen;
  let x = 0;
  for (let i = 0; i < bufLen; i++) {
    const v = data[i] / 128.0;
    const y = (v * H) / 2;
    if (i === 0) ctx2d.moveTo(x, y);
    else          ctx2d.lineTo(x, y);
    x += sliceW;
  }
  ctx2d.lineTo(W, H / 2);
  ctx2d.stroke();

  animFrameId = requestAnimationFrame(drawWave);
}

function stopWaveform() {
  cancelAnimationFrame(animFrameId);
  animFrameId = null;
  analyser = null;
  if (audioCtx) { audioCtx.close(); audioCtx = null; }
  ctx2d.clearRect(0, 0, waveformCanvas.width, waveformCanvas.height);
  waveformCanvas.classList.remove('active');
}

// ════════════════════════════════════════════════════════════
// Recording
// ════════════════════════════════════════════════════════════
btnRecord.addEventListener('click', toggleRecording);

async function toggleRecording() {
  if (!isRecording) {
    await startRecording();
  } else {
    stopRecording();
  }
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks   = [];

    mediaRecorder.ondataavailable = e => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      await processAudioBlob(blob);
      // Stop all tracks
      stream.getTracks().forEach(t => t.stop());
    };

    mediaRecorder.start(100);
    isRecording = true;

    // UI
    btnRecord.classList.add('recording');
    btnRecord.setAttribute('aria-label', 'Stop recording');
    document.body.querySelector('.recorder-card').classList.add('is-recording');
    recLabel.textContent = 'Recording… click to stop';
    startTimer();
    startWaveform(stream);
    resetResults();
    resetPipeline();

  } catch (err) {
    showToast('Microphone access denied. Please allow microphone permissions.', 'error');
    console.error(err);
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }
  isRecording = false;

  // UI
  btnRecord.classList.remove('recording');
  btnRecord.setAttribute('aria-label', 'Start recording');
  document.body.querySelector('.recorder-card').classList.remove('is-recording');
  recLabel.textContent = 'Processing your audio…';
  stopTimer();
  stopWaveform();
}

// ════════════════════════════════════════════════════════════
// Process recorded audio → /voicebot
// ════════════════════════════════════════════════════════════
async function processAudioBlob(blob) {
  showSpinner('Transcribing audio…');
  resetResults();
  resetPipeline();
  setStep('asr', 'active');

  const formData = new FormData();
  formData.append('file', blob, 'recording.webm');

  try {
    const res = await fetch(`${API_BASE}/voicebot`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server error ${res.status}`);
    }

    const data = await res.json();
    setStep('asr',  'done');

    // Short delays to show pipeline progression visually
    await delay(200); setStep('nlp', 'done');
    await delay(200); setStep('resp', 'done');
    await delay(200); setStep('tts', 'done');

    displayResults(data);
    showToast('Response ready!', 'success');

  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
    console.error(err);
    recLabel.textContent = 'Something went wrong. Try again.';
  } finally {
    hideSpinner();
    recLabel.textContent = 'Click the mic to start recording';
  }
}

// ════════════════════════════════════════════════════════════
// Text input → /predict-intent + /generate-response
// ════════════════════════════════════════════════════════════
btnSend.addEventListener('click', sendTextQuery);
textInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendTextQuery(); }
});

async function sendTextQuery() {
  const text = textInput.value.trim();
  if (!text) { showToast('Please enter a query first', 'info'); return; }

  showSpinner('Analyzing intent…');
  btnSend.disabled = true;
  resetResults();
  resetPipeline();
  setStep('asr', 'done');   // skip ASR, text already provided
  setStep('nlp', 'active');

  try {
    // Show text as transcription
    updateTranscription(text);

    // 1. Intent
    const fd1 = new FormData();
    fd1.append('text', text);
    const intentRes = await fetch(`${API_BASE}/predict-intent`, { method: 'POST', body: fd1 });
    if (!intentRes.ok) throw new Error(`Intent API error ${intentRes.status}`);
    const intentData = await intentRes.json();
    setStep('nlp', 'done');
    setStep('resp', 'active');

    updateIntent(intentData.intent, intentData.confidence);

    // 2. Response
    const fd2 = new FormData();
    fd2.append('intent', intentData.intent);
    fd2.append('text', text);
    const respRes = await fetch(`${API_BASE}/generate-response`, { method: 'POST', body: fd2 });
    if (!respRes.ok) throw new Error(`Response API error ${respRes.status}`);
    const respData = await respRes.json();
    setStep('resp', 'done');

    updateResponse(respData.response);
    showToast('Analysis complete!', 'success');

  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
    console.error(err);
  } finally {
    hideSpinner();
    btnSend.disabled = false;
  }
}

// ════════════════════════════════════════════════════════════
// Display helpers
// ════════════════════════════════════════════════════════════
function displayResults(data) {
  updateTranscription(data.transcription || '');
  updateIntent(data.intent, data.confidence);
  updateResponse(data.response || '');
  if (data.audio_url) updateAudio(data.audio_url);
}

function updateTranscription(text) {
  if (text) {
    transcriptionEl.textContent = text;
    transcriptionEl.classList.remove('empty');
  } else {
    transcriptionEl.textContent = 'No transcription produced.';
    transcriptionEl.classList.add('empty');
  }
}

function updateIntent(intent, confidence) {
  if (!intent) return;

  const formatted = intent.replaceAll('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
  intentLabel.textContent = formatted;
  intentBadge.classList.remove('hidden');
  intentPlaceholder.classList.add('hidden');

  confWrap.classList.add('visible');
  const pct = Math.round((confidence || 0) * 100);
  confPct.textContent  = `${pct}%`;
  confFill.style.width = `${pct}%`;
}

function updateResponse(text) {
  if (text) {
    responseTextEl.textContent = text;
    responseTextEl.classList.remove('empty');
  }
}

function updateAudio(url) {
  responseAudio.src = url;
  audioWrap.classList.add('visible');
  audioPlaceholder.classList.add('hidden');
  responseAudio.play().catch(() => {});  // autoplay may be blocked, user can press play
}

function resetResults() {
  transcriptionEl.textContent = 'Your speech will appear here…';
  transcriptionEl.classList.add('empty');

  intentBadge.classList.add('hidden');
  intentPlaceholder.classList.remove('hidden');
  confWrap.classList.remove('visible');
  confFill.style.width = '0%';

  responseTextEl.textContent = 'The AI response will appear here…';
  responseTextEl.classList.add('empty');

  audioWrap.classList.remove('visible');
  audioPlaceholder.classList.remove('hidden');
  responseAudio.src = '';
}

// ════════════════════════════════════════════════════════════
// Spinner
// ════════════════════════════════════════════════════════════
function showSpinner(label = 'Processing…') {
  spinnerLabel.textContent = label;
  spinner.classList.add('visible');
}

function hideSpinner() {
  spinner.classList.remove('visible');
}

// ════════════════════════════════════════════════════════════
// Utility
// ════════════════════════════════════════════════════════════
function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

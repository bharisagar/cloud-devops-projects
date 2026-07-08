const SOURCE_SPEECH_LANGUAGE = "kn-IN";

const state = {
  pack: null,
  current: null,
  recognition: null,
  listening: false,
  exchanges: [],
  showAllPhrases: false,
};

const els = {
  safetyNotice: document.querySelector("#safetyNotice"),
  speechSupport: document.querySelector("#speechSupport"),
  micButton: document.querySelector("#micButton"),
  stopButton: document.querySelector("#stopButton"),
  clearButton: document.querySelector("#clearButton"),
  sourceText: document.querySelector("#sourceText"),
  matchLabel: document.querySelector("#matchLabel"),
  severityLabel: document.querySelector("#severityLabel"),
  confidenceLabel: document.querySelector("#confidenceLabel"),
  phraseButtons: document.querySelector("#phraseButtons"),
  shuffleButton: document.querySelector("#shuffleButton"),
  translationGrid: document.querySelector("#translationGrid"),
  clinicalNote: document.querySelector("#clinicalNote"),
  speakAllButton: document.querySelector("#speakAllButton"),
  saveExchangeButton: document.querySelector("#saveExchangeButton"),
  copyButton: document.querySelector("#copyButton"),
  exchangeCount: document.querySelector("#exchangeCount"),
  handoffLog: document.querySelector("#handoffLog"),
};

function normalizeText(value) {
  return (value || "")
    .toString()
    .trim()
    .replace(/[.,!?;:()\[\]{}"']/g, " ")
    .replace(/\s+/g, " ")
    .toLowerCase();
}

function scorePhrase(input, phrase) {
  const normalizedInput = normalizeText(input);
  const normalizedKannada = normalizeText(phrase.kannada);
  if (!normalizedInput) return { score: 0, reason: "empty" };
  if (normalizedInput === normalizedKannada) return { score: 100, reason: "exact" };
  if (normalizedInput.includes(normalizedKannada) || normalizedKannada.includes(normalizedInput)) {
    return { score: 86, reason: "phrase" };
  }

  const matchedKeywords = (phrase.keywords || []).filter((keyword) => normalizedInput.includes(normalizeText(keyword)));
  const score = matchedKeywords.length * 28;
  return { score, reason: matchedKeywords.length ? `keywords: ${matchedKeywords.join(", ")}` : "no match" };
}

function findBestMatch(input) {
  const scored = state.pack.phrases
    .map((phrase) => ({ phrase, ...scorePhrase(input, phrase) }))
    .sort((a, b) => b.score - a.score);
  const best = scored[0];
  if (!best || best.score < 28) {
    return {
      phrase: state.pack.fallback,
      score: 0,
      confidence: "needs human review",
      reason: "no safe phrase match",
      fallback: true,
    };
  }
  return {
    ...best,
    confidence: best.score >= 80 ? "high" : "medium",
    fallback: false,
  };
}

function severityClass(severity) {
  if (severity === "urgent") return "severity-urgent";
  if (severity === "routine") return "severity-routine";
  return "severity-review";
}

function clearNode(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}

function createText(parent, tag, text, className) {
  const element = document.createElement(tag);
  element.textContent = text;
  if (className) element.className = className;
  parent.appendChild(element);
  return element;
}

function renderTranslations(match) {
  clearNode(els.translationGrid);
  state.pack.targetLanguages.forEach((language) => {
    const card = document.createElement("article");
    card.className = "translation-card";

    const header = document.createElement("header");
    createText(header, "span", language.name);
    createText(header, "small", language.code);
    card.appendChild(header);

    createText(card, "p", match.phrase[language.key] || "Translation unavailable.");

    const button = document.createElement("button");
    button.type = "button";
    button.textContent = `Speak ${language.name}`;
    button.addEventListener("click", () => speak(language, match.phrase[language.key]));
    card.appendChild(button);

    els.translationGrid.appendChild(card);
  });
}

function renderMatch(input) {
  const match = findBestMatch(input);
  state.current = match;
  els.matchLabel.textContent = match.fallback ? "Human interpreter needed" : match.phrase.intent.replace(/_/g, " ");
  els.severityLabel.textContent = match.phrase.severity || "review";
  els.severityLabel.className = severityClass(match.phrase.severity);
  els.confidenceLabel.textContent = match.confidence;
  els.clinicalNote.textContent = match.phrase.clinicalNote || "Ask a clinician or qualified interpreter before clinical decisions.";
  renderTranslations(match);
}

function renderPhraseButtons() {
  clearNode(els.phraseButtons);
  const phrases = state.showAllPhrases ? state.pack.phrases : state.pack.phrases.slice(0, 8);
  phrases.forEach((phrase) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = phrase.kannada;
    button.addEventListener("click", () => {
      els.sourceText.value = phrase.kannada;
      renderMatch(phrase.kannada);
      els.sourceText.focus();
    });
    els.phraseButtons.appendChild(button);
  });
  els.shuffleButton.textContent = state.showAllPhrases ? "Show fewer" : "Show all";
}

function pickVoice(language) {
  const voices = window.speechSynthesis?.getVoices?.() || [];
  return voices.find((voice) => voice.lang === language.code)
    || voices.find((voice) => voice.lang.toLowerCase().startsWith(language.voiceHint))
    || null;
}

function speak(language, text) {
  if (!window.speechSynthesis || !text) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = language.code;
  const voice = pickVoice(language);
  if (voice) utterance.voice = voice;
  utterance.rate = 0.92;
  utterance.pitch = 1;
  window.speechSynthesis.speak(utterance);
}

function speakAll() {
  if (!state.current || !window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  state.pack.targetLanguages.forEach((language, index) => {
    const text = state.current.phrase[language.key];
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language.code;
    const voice = pickVoice(language);
    if (voice) utterance.voice = voice;
    utterance.rate = 0.92;
    window.setTimeout(() => window.speechSynthesis.speak(utterance), index * 900);
  });
}

function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    els.speechSupport.textContent = "Voice unavailable";
    els.micButton.disabled = true;
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = SOURCE_SPEECH_LANGUAGE;
  recognition.interimResults = true;
  recognition.continuous = true;

  recognition.addEventListener("start", () => {
    state.listening = true;
    els.speechSupport.textContent = "Listening in Kannada";
    els.micButton.disabled = true;
  });

  recognition.addEventListener("end", () => {
    state.listening = false;
    els.speechSupport.textContent = "Voice ready";
    els.micButton.disabled = false;
  });

  recognition.addEventListener("result", (event) => {
    let finalText = "";
    let interimText = "";
    for (let index = event.resultIndex; index < event.results.length; index += 1) {
      const transcript = event.results[index][0].transcript;
      if (event.results[index].isFinal) finalText += transcript;
      else interimText += transcript;
    }
    const nextValue = `${els.sourceText.value} ${finalText || interimText}`.trim();
    els.sourceText.value = nextValue;
    renderMatch(nextValue);
  });

  recognition.addEventListener("error", () => {
    els.speechSupport.textContent = "Voice needs browser permission";
    els.micButton.disabled = false;
  });

  state.recognition = recognition;
  els.speechSupport.textContent = "Voice ready";
}

function saveExchange() {
  if (!state.current) return;
  const input = els.sourceText.value.trim();
  if (!input) return;
  state.exchanges.unshift({
    time: new Date().toLocaleTimeString(),
    input,
    intent: state.current.phrase.intent,
    severity: state.current.phrase.severity,
    english: state.current.phrase.english,
    tamil: state.current.phrase.tamil,
    telugu: state.current.phrase.telugu,
  });
  renderHandoff();
}

function renderHandoff() {
  clearNode(els.handoffLog);
  els.exchangeCount.textContent = `${state.exchanges.length} saved`;
  if (!state.exchanges.length) {
    createText(els.handoffLog, "div", "No exchanges saved yet.", "empty-log");
    return;
  }
  state.exchanges.forEach((exchange) => {
    const item = document.createElement("article");
    item.className = "exchange";
    createText(item, "strong", `${exchange.time} - ${exchange.intent || "review"} - ${exchange.severity || "review"}`);
    createText(item, "p", `Kannada: ${exchange.input}`);
    createText(item, "p", `English: ${exchange.english}`);
    createText(item, "p", `Tamil: ${exchange.tamil}`);
    createText(item, "p", `Telugu: ${exchange.telugu}`);
    els.handoffLog.appendChild(item);
  });
}

async function copyHandoff() {
  const lines = state.exchanges.map((exchange) => [
    `${exchange.time} - ${exchange.intent} - ${exchange.severity}`,
    `Kannada: ${exchange.input}`,
    `English: ${exchange.english}`,
    `Tamil: ${exchange.tamil}`,
    `Telugu: ${exchange.telugu}`,
  ].join("
"));
  await navigator.clipboard.writeText(lines.join("

"));
  els.copyButton.textContent = "Copied";
  window.setTimeout(() => { els.copyButton.textContent = "Copy handoff"; }, 1200);
}

function bindEvents() {
  els.sourceText.addEventListener("input", () => renderMatch(els.sourceText.value));
  els.micButton.addEventListener("click", () => state.recognition?.start());
  els.stopButton.addEventListener("click", () => state.recognition?.stop());
  els.clearButton.addEventListener("click", () => {
    els.sourceText.value = "";
    renderMatch("");
    window.speechSynthesis?.cancel?.();
  });
  els.shuffleButton.addEventListener("click", () => {
    state.showAllPhrases = !state.showAllPhrases;
    renderPhraseButtons();
  });
  els.speakAllButton.addEventListener("click", speakAll);
  els.saveExchangeButton.addEventListener("click", saveExchange);
  els.copyButton.addEventListener("click", copyHandoff);
}

async function init() {
  const response = await fetch("translation-pack.json");
  state.pack = await response.json();
  els.safetyNotice.textContent = state.pack.safetyNotice.english;
  renderPhraseButtons();
  renderMatch("");
  renderHandoff();
  setupSpeechRecognition();
  bindEvents();
}

init().catch((error) => {
  els.safetyNotice.textContent = `App failed to load: ${error.message}`;
});
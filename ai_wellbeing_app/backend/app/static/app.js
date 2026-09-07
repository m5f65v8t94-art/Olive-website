/**
 * Olive — Youth Mental Wellbeing Support Web Application
 * Complete Client Application Engine
 */

(function () {
  'use strict';

  // ==========================================================================
  // 1. Application State
  // ==========================================================================
  const STATE = {
    currentMode: 'just_listen',
    currentTab: 'chat',
    sessionId: generateUUID(),
    authToken: localStorage.getItem('olive_auth_token') || null,
    currentUser: JSON.parse(localStorage.getItem('olive_user') || 'null'),
    isHistoryUnlocked: false,
    currentPinInput: '',
    pinAction: 'unlock', // 'unlock' or 'setup'
    selectedFeelings: [],
    activeExerciseKey: 'box_breathing',
    exerciseActive: false,
    exerciseTimer: null,
    exercisePhaseSecondsLeft: 0,
    exerciseCycle: 0,
    chimeSoundEnabled: true,
    activeJournalId: null,
    speechRecognition: null,
    isListeningMic: false,
    viewingSessionId: null,
    viewingSessionTitle: '',
    isSendingMessage: false
  };

  // Helper: UUID Generator
  function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  // Audio Chime Synth (Dual Harmonic Meditation Chime with Auto-Unlock & Node Cleanup)
  const AUDIO = {
    ctx: null,
    activeNodes: [],
    init() {
      try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!this.ctx && AudioCtx) {
          this.ctx = new AudioCtx();
        }
        if (this.ctx && this.ctx.state === 'suspended') {
          this.ctx.resume();
        }
      } catch (e) {
        console.warn('Web Audio API not supported', e);
      }
    },
    stopAll() {
      try {
        this.activeNodes.forEach(node => {
          try {
            if (node.stop) node.stop();
            if (node.disconnect) node.disconnect();
          } catch (_) {}
        });
        this.activeNodes = [];
      } catch (e) {}
    },
    playChime(freq = 432, duration = 1.4) {
      if (!STATE.chimeSoundEnabled) return;
      try {
        this.init();
        if (!this.ctx) return;
        if (this.ctx.state === 'suspended') {
          this.ctx.resume();
        }
        const now = this.ctx.currentTime;

        // Master Gain with smooth bell-like envelope
        const masterGain = this.ctx.createGain();
        masterGain.gain.setValueAtTime(0.0001, now);
        masterGain.gain.linearRampToValueAtTime(0.35, now + 0.04);
        masterGain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
        masterGain.connect(this.ctx.destination);

        // 1. Fundamental tone
        const osc1 = this.ctx.createOscillator();
        osc1.type = 'sine';
        osc1.frequency.setValueAtTime(freq, now);
        osc1.connect(masterGain);

        // 2. Harmonic overtone (Tibetan singing bowl resonance)
        const osc2 = this.ctx.createOscillator();
        osc2.type = 'sine';
        osc2.frequency.setValueAtTime(freq * 1.5, now);
        const gain2 = this.ctx.createGain();
        gain2.gain.setValueAtTime(0.12, now);
        osc2.connect(gain2);
        gain2.connect(masterGain);

        osc1.start(now);
        osc2.start(now);
        osc1.stop(now + duration);
        osc2.stop(now + duration);

        this.activeNodes.push(osc1, osc2, masterGain);
        setTimeout(() => {
          this.activeNodes = this.activeNodes.filter(n => n !== osc1 && n !== osc2 && n !== masterGain);
        }, duration * 1000 + 100);
      } catch (e) {
        console.warn('Chime playback error:', e);
      }
    }
  };

  // Helper: Fetch with Bearer Auth
  async function apiFetch(url, options = {}) {
    const headers = options.headers || {};
    if (STATE.authToken) {
      headers['Authorization'] = `Bearer ${STATE.authToken}`;
    }
    if (!headers['Content-Type'] && options.method && options.method !== 'GET') {
      headers['Content-Type'] = 'application/json';
    }
    return fetch(url, { ...options, headers });
  }

  // ==========================================================================
  // 2. DOM Elements Cache
  // ==========================================================================
  const DOM = {};

  function initDOM() {
    // Brand & Navigation
    DOM.brandHomeLink = document.getElementById('brand-home-link');
    DOM.navPills = document.querySelectorAll('.nav-pill-btn');
    DOM.sections = document.querySelectorAll('.app-section');

    // Header Actions
    DOM.btnQuickHide = document.getElementById('btn-quick-hide');
    DOM.btnThemeToggle = document.getElementById('btn-theme-toggle');
    DOM.themeIcon = document.getElementById('theme-icon');
    DOM.btnHeaderLock = document.getElementById('btn-header-lock');
    DOM.btnProfileTrigger = document.getElementById('btn-profile-trigger');
    DOM.userAvatarIcon = document.getElementById('user-avatar-icon');

    // Chat Elements
    DOM.modeCards = document.querySelectorAll('.mode-box');
    DOM.chatMessagesContainer = document.getElementById('chat-messages-container');
    DOM.typingIndicator = document.getElementById('typing-indicator');
    DOM.chatInput = document.getElementById('chat-input');
    DOM.btnChatMic = document.getElementById('btn-chat-mic');
    DOM.btnChatSend = document.getElementById('btn-chat-send');
    DOM.activeModeLabel = document.getElementById('active-mode-label');
    DOM.btnNewChat = document.getElementById('btn-new-chat');
    DOM.btnExportChat = document.getElementById('btn-export-chat');

    // Resources Section
    DOM.resourcesContainer = document.getElementById('resources-cards-container');

    // Feelings Check-in
    DOM.feelingsTagsContainer = document.getElementById('feelings-tags-container');
    DOM.feelingTagBtns = document.querySelectorAll('.feeling-tag-btn');
    DOM.feelingsCountBadge = document.getElementById('feelings-count-badge');
    DOM.energySlider = document.getElementById('energy-slider');
    DOM.pleasantSlider = document.getElementById('pleasant-slider');
    DOM.feelingNoteInput = document.getElementById('feeling-note-input');
    DOM.btnSaveFeeling = document.getElementById('btn-save-feeling');
    DOM.moodHistoryList = document.getElementById('mood-history-list');

    // Private Journal
    DOM.btnNewJournalEntry = document.getElementById('btn-new-journal-entry');
    DOM.journalSearchInput = document.getElementById('journal-search-input');
    DOM.journalEntriesList = document.getElementById('journal-entries-list');
    DOM.journalTitleInput = document.getElementById('journal-title-input');
    DOM.journalPromptSelect = document.getElementById('journal-prompt-select');
    DOM.journalContentInput = document.getElementById('journal-content-input');
    DOM.btnSaveJournalEntry = document.getElementById('btn-save-journal-entry');
    DOM.btnDeleteJournalEntry = document.getElementById('btn-delete-journal-entry');

    // Calming Exercises
    DOM.exerciseTabBtns = document.querySelectorAll('.exercise-tab-btn');
    DOM.exDisplayTitle = document.getElementById('ex-display-title');
    DOM.exDisplayDesc = document.getElementById('ex-display-desc');
    DOM.breathingContainer = document.getElementById('breathing-visualizer-container');
    DOM.breathingOrb = document.getElementById('breathing-orb');
    DOM.breathingPhaseText = document.getElementById('breathing-phase-text');
    DOM.breathingCycleCounter = document.getElementById('breathing-cycle-counter');
    DOM.exerciseStepsContainer = document.getElementById('exercise-steps-container');
    DOM.thoughtDefusionContainer = document.getElementById('thought-defusion-container');
    DOM.thoughtCanvas = document.getElementById('thought-canvas');
    DOM.thoughtInput = document.getElementById('thought-input');
    DOM.btnExerciseToggle = document.getElementById('btn-exercise-toggle');
    DOM.btnChimeToggle = document.getElementById('btn-chime-toggle');
    DOM.chimeStatusText = document.getElementById('chime-status-text');

    // Protected History & PIN
    DOM.historyLockedCard = document.getElementById('history-locked-card');
    DOM.historyUnlockedCard = document.getElementById('history-unlocked-card');
    DOM.historyLockedTitle = document.getElementById('history-locked-title');
    DOM.historyLockedDesc = document.getElementById('history-locked-desc');
    DOM.pinDots = [
      document.getElementById('pdot-1'),
      document.getElementById('pdot-2'),
      document.getElementById('pdot-3'),
      document.getElementById('pdot-4')
    ];
    DOM.pinErrorMsg = document.getElementById('pin-error-msg');
    DOM.pinKeys = document.querySelectorAll('.pin-key');
    DOM.btnPinClear = document.getElementById('btn-pin-clear');
    DOM.btnPinBackspace = document.getElementById('btn-pin-backspace');
    DOM.historySessionCount = document.getElementById('history-session-count');
    DOM.historySessionsContainer = document.getElementById('history-sessions-container');
    DOM.btnPurgeHistory = document.getElementById('btn-purge-history');

    // Modals
    DOM.modalProfile = document.getElementById('modal-profile');
    DOM.btnCloseProfile = document.getElementById('btn-close-profile');
    DOM.authLoggedInView = document.getElementById('auth-logged-in-view');
    DOM.authFormsView = document.getElementById('auth-forms-view');
    DOM.profileAvatarDisplay = document.getElementById('profile-avatar-display');
    DOM.profileNameDisplay = document.getElementById('profile-name-display');
    DOM.profileEmailDisplay = document.getElementById('profile-email-display');
    DOM.btnSignOut = document.getElementById('btn-sign-out');
    DOM.btnTabSignin = document.getElementById('btn-tab-signin');
    DOM.btnTabSignup = document.getElementById('btn-tab-signup');
    DOM.btnGoogleSignin = document.getElementById('btn-google-signin');
    DOM.formSignin = document.getElementById('form-signin');
    DOM.formSignup = document.getElementById('form-signup');
    DOM.authErrorMsg = document.getElementById('auth-error-msg');

    DOM.modalConversationViewer = document.getElementById('modal-conversation-viewer');
    DOM.btnCloseViewer = document.getElementById('btn-close-viewer');
    DOM.btnViewerCloseFooter = document.getElementById('btn-viewer-close-footer');
    DOM.btnViewerContinue = document.getElementById('btn-viewer-continue');
    DOM.viewerChatTitle = document.getElementById('viewer-chat-title');
    DOM.viewerChatMeta = document.getElementById('viewer-chat-meta');
    DOM.viewerMessagesContainer = document.getElementById('viewer-messages-container');

    // Privacy Hide
    DOM.privacyHideOverlay = document.getElementById('privacy-hide-overlay');
    DOM.btnReturnFromHide = document.getElementById('btn-return-from-hide');
    DOM.studySectionsContainer = document.getElementById('study-sections-container');
    DOM.studyNbTitle = document.getElementById('study-nb-title');
    DOM.studyBreadcrumbsDisplay = document.getElementById('study-breadcrumbs-display');
    DOM.studyLastSaved = document.getElementById('study-last-saved');
    DOM.studySidebarCourse = document.getElementById('study-sidebar-course');
    DOM.studySubjectTag = document.getElementById('study-subject-tag');
    DOM.studyMainHeading = document.getElementById('study-main-heading');
    DOM.studyEditTime = document.getElementById('study-edit-time');
    DOM.studySummaryText = document.getElementById('study-summary-text');
  }

  // ==========================================================================
  // 3. Navigation & Routing
  // ==========================================================================
  function switchTab(tabName) {
    if (!tabName) tabName = 'chat';
    STATE.currentTab = tabName;

    // Close any open modals
    if (DOM.modalConversationViewer) DOM.modalConversationViewer.classList.remove('active');
    if (DOM.modalProfile) DOM.modalProfile.classList.remove('active');

    // Smooth scroll to top of page
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // IMPORTANT: If leaving or entering Protected History, lock it again immediately!
    if (tabName !== 'history') {
      STATE.isHistoryUnlocked = false;
      STATE.currentPinInput = '';
      if (DOM.historyLockedCard && DOM.historyUnlockedCard) {
        DOM.historyLockedCard.style.display = 'block';
        DOM.historyUnlockedCard.style.display = 'none';
        updatePinDots();
      }
    }

    // Update Nav Button Styles
    if (DOM.navPills) {
      DOM.navPills.forEach(btn => {
        const t = btn.getAttribute('data-tab') || btn.dataset.tab;
        btn.classList.toggle('active', t === tabName);
      });
    }

    // Update Sections Visibility
    if (DOM.sections) {
      DOM.sections.forEach(sec => {
        const isTarget = sec.id === `section-${tabName}`;
        sec.classList.toggle('active', isTarget);
      });
    }

    // Trigger tab specific initializations
    if (tabName === 'history') {
      initHistoryTab();
    } else if (tabName === 'resources') {
      loadHelplineResources();
    } else if (tabName === 'feelings') {
      loadFeelingsHistory();
    } else if (tabName === 'journal') {
      loadJournalEntries();
    } else if (tabName === 'exercises') {
      loadExercise(STATE.activeExerciseKey);
    }
  }

  // ==========================================================================
  // 4. Mode Selection & Chat Implementation
  // ==========================================================================
  const MODE_INFO = {
    just_listen: { title: 'Just Listen', icon: '🎧', tag: '🎧 Just Listen' },
    give_me_advice: { title: 'Give Me Advice', icon: '💡', tag: '💡 Give Me Advice' },
    help_me_understand: { title: 'Help Me Understand', icon: '🔍', tag: '🔍 Help Me Understand' },
    help_me_tell_someone: { title: 'Help Me Tell Someone', icon: '💌', tag: '💌 Help Me Tell Someone' }
  };

  function setChatMode(mode) {
    if (!mode || !MODE_INFO[mode]) mode = 'just_listen';
    STATE.currentMode = mode;
    if (DOM.modeCards) {
      DOM.modeCards.forEach(card => {
        card.classList.toggle('active', card.dataset.mode === mode);
      });
    }

    const info = MODE_INFO[mode] || MODE_INFO.just_listen;
    if (DOM.activeModeLabel) {
      DOM.activeModeLabel.textContent = `${info.icon} ${info.title}`;
    }
  }

  function appendChatBubble(role, text, mode = STATE.currentMode) {
    if (!DOM.chatMessagesContainer) return;
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}`;

    const p = document.createElement('p');
    p.style.fontSize = '14.5px';
    p.style.lineHeight = '1.6';
    p.style.whiteSpace = 'pre-wrap';
    p.textContent = text;
    bubble.appendChild(p);

    const footer = document.createElement('div');
    footer.className = 'chat-bubble-footer';
    
    const roleSpan = document.createElement('span');
    roleSpan.textContent = role === 'assistant' ? 'Liv' : (STATE.currentUser ? STATE.currentUser.username : 'You');
    footer.appendChild(roleSpan);

    if (role === 'assistant') {
      const modeTag = document.createElement('span');
      modeTag.className = 'bubble-mode-tag';
      const info = MODE_INFO[mode] || MODE_INFO.just_listen;
      modeTag.textContent = info.tag;
      footer.appendChild(modeTag);
    }

    bubble.appendChild(footer);
    DOM.chatMessagesContainer.appendChild(bubble);
    DOM.chatMessagesContainer.scrollTop = DOM.chatMessagesContainer.scrollHeight;
  }

  async function handleSendMessage() {
    if (STATE.isSendingMessage) return;
    const text = DOM.chatInput.value.trim();
    if (!text) return;

    STATE.isSendingMessage = true;

    // Reset input
    DOM.chatInput.value = '';
    DOM.chatInput.style.height = 'auto';

    // Append exactly ONE user message
    appendChatBubble('user', text);

    // Show typing indicator
    DOM.typingIndicator.classList.add('active');
    DOM.chatMessagesContainer.scrollTop = DOM.chatMessagesContainer.scrollHeight;

    try {
      const res = await apiFetch('/api/chat/turn', {
        method: 'POST',
        body: JSON.stringify({
          session_id: STATE.sessionId,
          message: text,
          mode: STATE.currentMode
        })
      });

      if (!res.ok) {
        throw new Error('Failed to reach Liv server');
      }

      const data = await res.json();
      DOM.typingIndicator.classList.remove('active');

      // Append exactly ONE assistant response
      const assistantText = data.assistant_message.content;
      appendChatBubble('assistant', assistantText, data.current_mode);

    } catch (err) {
      DOM.typingIndicator.classList.remove('active');
      appendChatBubble('assistant', "I'm right here with you, but having a little trouble connecting to the network. Please try sending your message again in a moment.");
    } finally {
      STATE.isSendingMessage = false;
    }
  }

  function startNewConversation() {
    STATE.sessionId = generateUUID();
    if (DOM.chatMessagesContainer) {
      DOM.chatMessagesContainer.innerHTML = `
        <div class="chat-bubble assistant">
          <p style="font-size: 15px; font-weight: 500;">Hey, I'm Liv. What's on your mind?</p>
          <div class="chat-bubble-footer">
            <span>Liv • Ready</span>
            <span class="bubble-mode-tag">🎧 Just Listen</span>
          </div>
        </div>
      `;
    }
    setChatMode('just_listen');
  }

  function exportChatHistory() {
    const bubbles = DOM.chatMessagesContainer.querySelectorAll('.chat-bubble');
    if (!bubbles.length) return;

    let transcript = `Olive Conversation with Liv\nExported: ${new Date().toLocaleString()}\nSession: ${STATE.sessionId}\n\n========================================\n\n`;
    bubbles.forEach(b => {
      const isUser = b.classList.contains('user');
      const text = b.querySelector('p').textContent;
      transcript += `${isUser ? 'YOU' : 'LIV'}:\n${text}\n\n`;
    });

    const blob = new Blob([transcript], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `olive-chat-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  // Speech to text microphone handler
  function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      if (DOM.btnChatMic) DOM.btnChatMic.style.display = 'none';
      return;
    }

    try {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = 'en-US';

      rec.onstart = () => {
        STATE.isListeningMic = true;
        if (DOM.btnChatMic) DOM.btnChatMic.classList.add('recording');
        if (DOM.chatInput) DOM.chatInput.placeholder = 'Listening... Speak now';
      };

      rec.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        if (transcript && DOM.chatInput) {
          DOM.chatInput.value = DOM.chatInput.value ? `${DOM.chatInput.value} ${transcript}` : transcript;
        }
      };

      rec.onerror = (e) => {
        console.warn('Speech recognition error:', e.error);
        stopSpeechRecognition();
      };

      rec.onend = () => {
        stopSpeechRecognition();
      };

      STATE.speechRecognition = rec;
    } catch (err) {
      console.warn('Speech recognition init failed', err);
    }
  }

  function toggleSpeechRecognition() {
    if (!STATE.speechRecognition) {
      alert('Voice speech recognition is not supported in this browser.');
      return;
    }

    if (STATE.isListeningMic) {
      stopSpeechRecognition();
    } else {
      try {
        STATE.speechRecognition.start();
      } catch (e) {
        stopSpeechRecognition();
      }
    }
  }

  function stopSpeechRecognition() {
    STATE.isListeningMic = false;
    if (DOM.btnChatMic) DOM.btnChatMic.classList.remove('recording');
    if (DOM.chatInput) DOM.chatInput.placeholder = "Message Liv... (type whatever is on your mind)";
    if (STATE.speechRecognition) {
      try { STATE.speechRecognition.stop(); } catch (e) {}
    }
  }

  // ==========================================================================
  // 5. Calming Exercises Implementation (NO BLANK PAGES)
  // ==========================================================================
  const EXERCISE_CONFIGS = {
    box_breathing: {
      type: 'breathing',
      title: 'Box Breathing (4-4-4-4)',
      desc: 'Slow, balanced breathing technique used to down-regulate the nervous system and calm acute anxiety.',
      phases: [
        { label: 'Inhale through nose', duration: 4, action: 'inhale', freq: 432 },
        { label: 'Hold breath gently', duration: 4, action: 'hold', freq: 528 },
        { label: 'Exhale through mouth', duration: 4, action: 'exhale', freq: 396 },
        { label: 'Hold breath empty', duration: 4, action: 'hold', freq: 528 }
      ]
    },
    relaxing_breath_478: {
      type: 'breathing',
      title: '4-7-8 Relaxing Breath',
      desc: 'Natural tranquilizer for the nervous system, helpful for acute stress, racing thoughts, and sleep.',
      phases: [
        { label: 'Inhale quietly through nose', duration: 4, action: 'inhale', freq: 432 },
        { label: 'Hold breath gently', duration: 7, action: 'hold', freq: 528 },
        { label: 'Exhale completely with whoosh sound', duration: 8, action: 'exhale', freq: 396 }
      ]
    },
    coherent_breathing: {
      type: 'breathing',
      title: '5-5 Coherent Breathing',
      desc: 'Equalized 5-second rhythmic breathing to optimize heart-rate variability and calm mental chatter.',
      phases: [
        { label: 'Inhale smoothly', duration: 5, action: 'inhale', freq: 432 },
        { label: 'Exhale smoothly', duration: 5, action: 'exhale', freq: 396 }
      ]
    },
    sensory_grounding: {
      type: 'steps',
      title: '5-4-3-2-1 Sensory Grounding',
      desc: 'Anchors attention back into your physical surroundings when feeling overwhelmed, disoriented, or spiraling.',
      steps: [
        '👁️ Name 5 things you can SEE around the room (e.g. lamp, shadow, window, book, pen)',
        '✋ Name 4 things you can physically TOUCH or feel (e.g. fabric of your sleeve, desk edge, chair, smooth screen)',
        '👂 Name 3 things you can HEAR right now (e.g. distant traffic, fan hum, your own breath)',
        '👃 Name 2 things you can SMELL (or two scents you enjoy, like coffee or fresh rain)',
        '🤍 Name 1 thing you like, appreciate, or find comforting about yourself or your day'
      ]
    },
    body_scan: {
      type: 'steps',
      title: 'Progressive Body Scan & Release',
      desc: 'Releases subconscious muscle tension stored in your forehead, jaw, shoulders, and hands.',
      steps: [
        '1. Soften your forehead and uncrease your brow.',
        '2. Unclench your teeth and let your tongue rest gently away from the roof of your mouth.',
        '3. Drop your shoulders down and back, away from your ears.',
        '4. Loosen your hands, uncurling your fingers on your lap.',
        '5. Take a deep, gentle breath and let your belly expand without holding it in.',
        '6. Feel the solid, steady support of the chair or floor underneath you.'
      ]
    },
    thought_defusion: {
      type: 'canvas',
      title: 'Leaves on a Stream (Thought Defusion)',
      desc: 'Visualize your anxious or sticky thoughts drifting gently down a stream without having to struggle with them.'
    }
  };

  function loadExercise(key) {
    stopExercise();
    STATE.activeExerciseKey = key;
    const cfg = EXERCISE_CONFIGS[key] || EXERCISE_CONFIGS.box_breathing;

    if (DOM.exerciseTabBtns) {
      DOM.exerciseTabBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.ex === key);
      });
    }

    if (DOM.exDisplayTitle) DOM.exDisplayTitle.textContent = cfg.title;
    if (DOM.exDisplayDesc) DOM.exDisplayDesc.textContent = cfg.desc;

    if (cfg.type === 'breathing') {
      DOM.breathingContainer.style.display = 'block';
      DOM.exerciseStepsContainer.style.display = 'none';
      DOM.thoughtDefusionContainer.style.display = 'none';
      DOM.btnExerciseToggle.style.display = 'inline-flex';
      DOM.btnExerciseToggle.textContent = '▶️ Start Exercise';
    } else if (cfg.type === 'steps') {
      DOM.breathingContainer.style.display = 'none';
      DOM.exerciseStepsContainer.style.display = 'block';
      DOM.thoughtDefusionContainer.style.display = 'none';
      DOM.btnExerciseToggle.style.display = 'none';

      let html = '<div style="display:flex; flex-direction:column; gap:10px;">';
      cfg.steps.forEach(st => {
        html += `<div style="padding:14px 18px; background:var(--bg-surface-secondary); border:1px solid var(--border-subtle); border-radius:var(--radius-md); font-size:14.5px; line-height:1.5;">${st}</div>`;
      });
      html += '</div>';
      DOM.exerciseStepsContainer.innerHTML = html;
    } else if (cfg.type === 'canvas') {
      DOM.breathingContainer.style.display = 'none';
      DOM.exerciseStepsContainer.style.display = 'none';
      DOM.thoughtDefusionContainer.style.display = 'block';
      DOM.btnExerciseToggle.style.display = 'none';
      initThoughtCanvas();
    }
  }

  function toggleExercise() {
    if (STATE.exerciseActive) {
      stopExercise();
    } else {
      startExercise();
    }
  }

  function startExercise() {
    const cfg = EXERCISE_CONFIGS[STATE.activeExerciseKey];
    if (!cfg || cfg.type !== 'breathing') return;

    AUDIO.init();
    STATE.exerciseActive = true;
    STATE.exerciseCycle = 0;
    if (DOM.btnExerciseToggle) DOM.btnExerciseToggle.textContent = '⏸️ Pause Exercise';
    runBreathingCycle(cfg);
  }

  function stopExercise() {
    STATE.exerciseActive = false;
    clearTimeout(STATE.exerciseTimer);
    AUDIO.stopAll();
    if (DOM.btnExerciseToggle) DOM.btnExerciseToggle.textContent = '▶️ Start Exercise';
    if (DOM.breathingOrb) {
      DOM.breathingOrb.className = 'breathing-orb';
      DOM.breathingOrb.textContent = 'Ready';
    }
    if (DOM.breathingPhaseText) DOM.breathingPhaseText.textContent = 'Press Start to Begin';
  }

  function runBreathingCycle(cfg) {
    if (!STATE.exerciseActive) return;

    let phaseIndex = 0;

    function step() {
      if (!STATE.exerciseActive) return;
      const phase = cfg.phases[phaseIndex];

      DOM.breathingOrb.className = `breathing-orb ${phase.action}`;
      DOM.breathingOrb.textContent = phase.action.toUpperCase();
      DOM.breathingPhaseText.textContent = `${phase.label} (${phase.duration}s)`;

      AUDIO.playChime(phase.freq || 432, 1.2);

      if (phaseIndex === 0) {
        STATE.exerciseCycle++;
        DOM.breathingCycleCounter.textContent = `Cycle: ${STATE.exerciseCycle} / 4`;
      }

      STATE.exerciseTimer = setTimeout(() => {
        phaseIndex = (phaseIndex + 1) % cfg.phases.length;
        step();
      }, phase.duration * 1000);
    }

    step();
  }

  // Thought Defusion Canvas
  let thoughtLeaves = [];
  let thoughtCanvasCtx = null;
  let thoughtAnimFrame = null;

  function initThoughtCanvas() {
    if (!DOM.thoughtCanvas) return;
    thoughtCanvasCtx = DOM.thoughtCanvas.getContext('2d');
    thoughtLeaves = [];
    if (!thoughtAnimFrame) {
      animateThoughtCanvas();
    }
  }

  function addThoughtLeaf() {
    const text = DOM.thoughtInput.value.trim();
    if (!text) return;
    DOM.thoughtInput.value = '';

    thoughtLeaves.push({
      text: text,
      x: 30,
      y: 80 + Math.random() * 40,
      vx: 1.2 + Math.random() * 0.8,
      vy: Math.sin(Math.random()) * 0.4,
      rotation: 0
    });
  }

  function animateThoughtCanvas() {
    if (DOM.thoughtCanvas && thoughtCanvasCtx) {
      const ctx = thoughtCanvasCtx;
      const w = DOM.thoughtCanvas.width;
      const h = DOM.thoughtCanvas.height;

      ctx.clearRect(0, 0, w, h);

      // Water stream gradient
      const grad = ctx.createLinearGradient(0, 0, 0, h);
      grad.addColorStop(0, '#bae6fd');
      grad.addColorStop(1, '#60a5fa');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, w, h);

      // Draw leaves
      for (let i = thoughtLeaves.length - 1; i >= 0; i--) {
        const l = thoughtLeaves[i];
        l.x += l.vx;
        l.y += Math.sin(l.x * 0.03) * 0.5;

        // Draw leaf
        ctx.save();
        ctx.translate(l.x, l.y);
        ctx.fillStyle = '#84cc16';
        ctx.beginPath();
        ctx.ellipse(0, 0, 30, 16, 0.2, 0, Math.PI * 2);
        ctx.fill();

        // Draw thought text on leaf
        ctx.fillStyle = '#1e293b';
        ctx.font = '11px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(l.text.slice(0, 20), 0, 4);
        ctx.restore();

        if (l.x > w + 60) {
          thoughtLeaves.splice(i, 1);
        }
      }
    }
    thoughtAnimFrame = requestAnimationFrame(animateThoughtCanvas);
  }

  // ==========================================================================
  // 6. Protected History & PIN Verification
  // ==========================================================================
  async function initHistoryTab() {
    STATE.currentPinInput = '';
    updatePinDots();
    DOM.pinErrorMsg.textContent = '';

    // Check if user has a PIN setup (either on account or on device)
    let hasPin = false;
    if (STATE.currentUser && STATE.currentUser.has_pin) {
      hasPin = true;
    } else if (localStorage.getItem('olive_guest_pin_hash')) {
      hasPin = true;
    } else if (STATE.authToken) {
      try {
        const res = await apiFetch('/api/auth/me');
        if (res.ok) {
          const u = await res.json();
          STATE.currentUser = u;
          hasPin = Boolean(u.has_pin);
        }
      } catch (e) {}
    }

    if (!hasPin) {
      STATE.pinAction = 'setup';
      DOM.historyLockedTitle.textContent = 'Set Up Your Privacy PIN';
      DOM.historyLockedDesc.textContent = 'Choose a 4-digit PIN to securely protect your conversation history.';
    } else {
      STATE.pinAction = 'unlock';
      DOM.historyLockedTitle.textContent = 'Enter Your Privacy PIN';
      DOM.historyLockedDesc.textContent = 'Please enter your PIN to view and continue previous conversations with Liv.';
    }

    DOM.historyLockedCard.style.display = 'block';
    DOM.historyUnlockedCard.style.display = 'none';
  }

  function handlePinKeyClick(num) {
    if (STATE.currentPinInput.length >= 4) return;
    STATE.currentPinInput += num;
    updatePinDots();

    if (STATE.currentPinInput.length === 4) {
      setTimeout(submitPin, 200);
    }
  }

  function updatePinDots() {
    const len = STATE.currentPinInput.length;
    DOM.pinDots.forEach((dot, idx) => {
      if (dot) dot.classList.toggle('filled', idx < len);
    });
  }

  async function submitPin() {
    const pin = STATE.currentPinInput;
    DOM.pinErrorMsg.textContent = '';

    try {
      if (STATE.pinAction === 'setup') {
        const res = await apiFetch('/api/auth/setup-pin', {
          method: 'POST',
          body: JSON.stringify({ pin })
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || 'Failed to setup PIN');
        }

        const data = await res.json();
        if (data.hashed_pin) {
          localStorage.setItem('olive_guest_pin_hash', data.hashed_pin);
        }
        if (STATE.currentUser) {
          STATE.currentUser.has_pin = true;
          localStorage.setItem('olive_user', JSON.stringify(STATE.currentUser));
        }

        STATE.isHistoryUnlocked = true;
        DOM.historyLockedCard.style.display = 'none';
        DOM.historyUnlockedCard.style.display = 'block';
        loadHistorySessions();
      } else {
        const storedHash = localStorage.getItem('olive_guest_pin_hash');
        const res = await apiFetch('/api/auth/verify-pin', {
          method: 'POST',
          body: JSON.stringify({ pin, hashed_pin: storedHash || undefined })
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || 'Incorrect PIN. Please try again.');
        }

        STATE.isHistoryUnlocked = true;
        DOM.historyLockedCard.style.display = 'none';
        DOM.historyUnlockedCard.style.display = 'block';
        loadHistorySessions();
      }
    } catch (err) {
      DOM.pinErrorMsg.textContent = err.message || 'Incorrect PIN. Try again.';
      STATE.currentPinInput = '';
      updatePinDots();
    }
  }

  async function loadHistorySessions() {
    DOM.historySessionsContainer.innerHTML = '<div style="color:var(--text-muted); font-size:13px; text-align:center; padding:20px;">Loading sessions...</div>';

    try {
      const res = await apiFetch('/api/chat/sessions');
      if (!res.ok) throw new Error('Failed to load history');
      const sessions = await res.json();

      DOM.historySessionCount.textContent = `${sessions.length} conversation${sessions.length === 1 ? '' : 's'} found`;

      if (!sessions.length) {
        DOM.historySessionsContainer.innerHTML = '<div style="color:var(--text-muted); font-size:13.5px; text-align:center; padding:30px;">No saved conversations yet. Message Liv to start one!</div>';
        return;
      }

      DOM.historySessionsContainer.innerHTML = '';
      sessions.forEach(s => {
        const card = document.createElement('div');
        card.style.cssText = 'padding:14px 18px; background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:var(--radius-md); display:flex; justify-content:space-between; align-items:center; cursor:pointer; transition:all 0.15s ease;';
        card.onmouseover = () => card.style.borderColor = 'var(--primary)';
        card.onmouseout = () => card.style.borderColor = 'var(--border-subtle)';

        const modeInfo = MODE_INFO[s.current_mode] || MODE_INFO.just_listen;
        const dateStr = s.updated_at ? new Date(s.updated_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'Recent';

        card.innerHTML = `
          <div style="flex:1; margin-right:12px;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
              <strong class="session-card-title" style="font-size:15px; color:var(--text-primary);">${escapeHtml(s.title || 'Conversation')}</strong>
              <span class="bubble-mode-tag" style="font-size:11px;">${modeInfo.tag}</span>
            </div>
            <p style="font-size:13px; color:var(--text-secondary); margin-bottom:4px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:480px;">
              ${escapeHtml(s.latest_message_preview || 'No messages yet')}
            </p>
            <span style="font-size:11.5px; color:var(--text-muted);">${dateStr} • ${s.message_count} messages</span>
          </div>
          <div style="display:flex; gap:8px;">
            <button class="btn-quick-hide btn-rename-session" type="button" style="font-size:12px; padding:4px 10px;" title="Rename conversation">✏️</button>
            <button class="btn-quick-hide btn-open-session" type="button" style="font-size:12px; padding:4px 12px;">Open</button>
            <button class="btn-quick-hide btn-del-session" type="button" style="font-size:12px; padding:4px 8px; color:#DC2626;" title="Delete conversation">🗑️</button>
          </div>
        `;

        card.querySelector('.btn-rename-session').onclick = async (e) => {
          e.preventDefault();
          e.stopPropagation();
          const newTitle = prompt('Enter a new title for this conversation:', s.title || 'Conversation');
          if (newTitle && newTitle.trim()) {
            const trimmed = newTitle.trim();
            try {
              const r = await apiFetch(`/api/chat/sessions/${s.id}`, {
                method: 'PATCH',
                body: JSON.stringify({ title: trimmed })
              });
              if (r.ok) {
                s.title = trimmed;
                card.querySelector('.session-card-title').textContent = trimmed;
              }
            } catch (err) {
              console.error('Rename failed', err);
            }
          }
        };

        card.querySelector('.btn-open-session').onclick = (e) => {
          e.preventDefault();
          e.stopPropagation();
          openConversationViewer(s.id, s.title);
        };
        card.onclick = () => openConversationViewer(s.id, s.title);

        card.querySelector('.btn-del-session').onclick = async (e) => {
          e.preventDefault();
          e.stopPropagation();
          if (confirm('Delete this conversation from history?')) {
            await apiFetch(`/api/chat/sessions/${s.id}`, { method: 'DELETE' });
            loadHistorySessions();
          }
        };

        DOM.historySessionsContainer.appendChild(card);
      });

    } catch (err) {
      DOM.historySessionsContainer.innerHTML = '<div style="color:#DC2626; font-size:13px; text-align:center;">Failed to load conversation history.</div>';
    }
  }

  async function openConversationViewer(sessionId, title) {
    STATE.viewingSessionId = sessionId;
    STATE.viewingSessionTitle = title || 'Conversation Details';
    DOM.viewerChatTitle.innerHTML = `${escapeHtml(title || 'Conversation Details')} <button id="btn-viewer-edit-title" type="button" class="btn-icon-round" style="width:26px; height:26px; font-size:12px; margin-left:6px;" title="Rename Title">✏️</button>`;
    DOM.viewerMessagesContainer.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-muted);">Loading conversation...</div>';
    DOM.modalConversationViewer.classList.add('active');

    // Attach viewer title edit handler
    const btnEditTitle = document.getElementById('btn-viewer-edit-title');
    if (btnEditTitle) {
      btnEditTitle.onclick = async (e) => {
        e.preventDefault();
        e.stopPropagation();
        const newTitle = prompt('Rename this conversation:', STATE.viewingSessionTitle);
        if (newTitle && newTitle.trim()) {
          const trimmed = newTitle.trim();
          try {
            const res = await apiFetch(`/api/chat/sessions/${sessionId}`, {
              method: 'PATCH',
              body: JSON.stringify({ title: trimmed })
            });
            if (res.ok) {
              STATE.viewingSessionTitle = trimmed;
              DOM.viewerChatTitle.innerHTML = `${escapeHtml(trimmed)} <button id="btn-viewer-edit-title" type="button" class="btn-icon-round" style="width:26px; height:26px; font-size:12px; margin-left:6px;" title="Rename Title">✏️</button>`;
              loadHistorySessions();
            }
          } catch (err) {
            console.error('Failed to rename in viewer', err);
          }
        }
      };
    }

    try {
      const res = await apiFetch(`/api/chat/sessions/${sessionId}/messages`);
      if (!res.ok) throw new Error('Failed to load messages');
      const msgs = await res.json();

      DOM.viewerChatMeta.textContent = `${msgs.length} messages`;
      DOM.viewerMessagesContainer.innerHTML = '';

      if (!msgs.length) {
        DOM.viewerMessagesContainer.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-muted);">No messages found in this conversation.</div>';
        return;
      }

      msgs.forEach(m => {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${m.role}`;
        bubble.innerHTML = `
          <p style="font-size:14px; line-height:1.5; white-space:pre-wrap;">${escapeHtml(m.content)}</p>
          <div class="chat-bubble-footer">
            <span>${m.role === 'assistant' ? 'Liv' : 'You'}</span>
            <span style="font-size:11px; color:var(--text-muted);">${new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        `;
        DOM.viewerMessagesContainer.appendChild(bubble);
      });
      DOM.viewerMessagesContainer.scrollTop = DOM.viewerMessagesContainer.scrollHeight;
    } catch (err) {
      DOM.viewerMessagesContainer.innerHTML = '<div style="color:#DC2626; text-align:center;">Failed to load messages.</div>';
    }
  }

  function continueViewingConversation() {
    if (!STATE.viewingSessionId) return;
    STATE.sessionId = STATE.viewingSessionId;

    // Transfer messages to main chat
    DOM.chatMessagesContainer.innerHTML = DOM.viewerMessagesContainer.innerHTML;
    DOM.modalConversationViewer.classList.remove('active');
    switchTab('chat');
  }

  // ==========================================================================
  // 7. Feelings Check-in Implementation
  // ==========================================================================
  function initFeelings() {
    if (DOM.feelingTagBtns) {
      DOM.feelingTagBtns.forEach(btn => {
        btn.onclick = () => {
          const val = btn.dataset.feeling;
          const idx = STATE.selectedFeelings.indexOf(val);
          if (idx >= 0) {
            STATE.selectedFeelings.splice(idx, 1);
            btn.classList.remove('selected');
          } else {
            if (STATE.selectedFeelings.length >= 3) {
              alert('You can select up to 3 feelings in one check-in.');
              return;
            }
            STATE.selectedFeelings.push(val);
            btn.classList.add('selected');
          }
          if (DOM.feelingsCountBadge) {
            DOM.feelingsCountBadge.textContent = `Select 1 to 3 feelings (${STATE.selectedFeelings.length}/3 selected)`;
          }
        };
      });
    }

    if (DOM.btnSaveFeeling) {
      DOM.btnSaveFeeling.onclick = async () => {
        if (!STATE.selectedFeelings.length) {
          alert('Please select at least 1 feeling to record your check-in.');
          return;
        }

        const score = parseInt(DOM.pleasantSlider ? DOM.pleasantSlider.value : 3, 10);
        const label = STATE.selectedFeelings[0];
        const notes = DOM.feelingNoteInput ? DOM.feelingNoteInput.value.trim() : '';

        try {
          const res = await apiFetch('/api/mood', {
            method: 'POST',
            body: JSON.stringify({
              mood_score: score,
              mood_label: label,
              emotion_tags: STATE.selectedFeelings,
              notes: notes
            })
          });

          if (!res.ok) throw new Error('Failed to save feeling');

          // Reset
          STATE.selectedFeelings = [];
          if (DOM.feelingTagBtns) DOM.feelingTagBtns.forEach(b => b.classList.remove('selected'));
          if (DOM.feelingsCountBadge) DOM.feelingsCountBadge.textContent = 'Select 1 to 3 feelings (0/3 selected)';
          if (DOM.feelingNoteInput) DOM.feelingNoteInput.value = '';

          loadFeelingsHistory();
          alert('Your feelings check-in has been recorded.');
        } catch (err) {
          alert('Could not save feeling check-in. Please try again.');
        }
      };
    }
  }

  async function loadFeelingsHistory() {
    if (!DOM.moodHistoryList) return;
    try {
      const res = await apiFetch('/api/mood/history');
      if (!res.ok) return;
      const logs = await res.json();

      DOM.moodHistoryList.innerHTML = '';
      if (!logs.length) {
        DOM.moodHistoryList.innerHTML = '<div style="color:var(--text-muted); font-size:13px; text-align:center; padding:12px;">No check-ins logged yet. Record your first feeling above!</div>';
        return;
      }

      logs.slice(0, 8).forEach(l => {
        const item = document.createElement('div');
        item.style.cssText = 'padding:10px 14px; background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:var(--radius-md); display:flex; justify-content:space-between; align-items:center;';
        
        const tagsHtml = (l.emotion_tags || []).map(t => `<span class="bubble-mode-tag" style="font-size:11px; margin-right:4px;">${escapeHtml(t)}</span>`).join('');
        const dateStr = new Date(l.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });

        item.innerHTML = `
          <div>
            <div style="margin-bottom:2px;">${tagsHtml}</div>
            ${l.notes ? `<p style="font-size:12.5px; color:var(--text-secondary); margin-top:4px;">${escapeHtml(l.notes)}</p>` : ''}
          </div>
          <span style="font-size:11px; color:var(--text-muted); white-space:nowrap;">${dateStr}</span>
        `;
        DOM.moodHistoryList.appendChild(item);
      });
    } catch (e) {}
  }

  // ==========================================================================
  // 8. Private Journal Implementation
  // ==========================================================================
  let journalEntriesCache = [];

  async function loadJournalEntries() {
    if (!DOM.journalEntriesList) return;
    DOM.journalEntriesList.innerHTML = '<div style="color:var(--text-muted); font-size:12px; text-align:center; padding:10px;">Loading entries...</div>';

    try {
      const res = await apiFetch('/api/journal');
      if (!res.ok) throw new Error('Failed to load journal entries');
      journalEntriesCache = await res.json();

      renderJournalList(journalEntriesCache);
    } catch (e) {
      DOM.journalEntriesList.innerHTML = '<div style="color:var(--text-muted); font-size:12px; text-align:center;">Could not load entries.</div>';
    }
  }

  function renderJournalList(entries) {
    if (!DOM.journalEntriesList) return;
    DOM.journalEntriesList.innerHTML = '';
    if (!entries.length) {
      DOM.journalEntriesList.innerHTML = '<div style="color:var(--text-muted); font-size:12.5px; text-align:center; padding:16px;">No entries yet. Write your thoughts!</div>';
      return;
    }

    entries.forEach(e => {
      const item = document.createElement('div');
      item.style.cssText = `padding:10px 12px; background:var(--bg-surface); border:1px solid ${e.id === STATE.activeJournalId ? 'var(--primary)' : 'var(--border-subtle)'}; border-radius:var(--radius-md); cursor:pointer; transition:all 0.15s ease;`;
      
      const dateStr = new Date(e.updated_at || e.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
      item.innerHTML = `
        <div style="font-weight:600; font-size:13.5px; color:var(--text-primary); margin-bottom:2px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${escapeHtml(e.title || 'Untitled Entry')}</div>
        <div style="font-size:11.5px; color:var(--text-muted);">${dateStr}</div>
      `;

      item.onclick = () => selectJournalEntry(e);
      DOM.journalEntriesList.appendChild(item);
    });
  }

  function selectJournalEntry(entry) {
    STATE.activeJournalId = entry.id;
    DOM.journalTitleInput.value = entry.title || '';
    DOM.journalContentInput.value = entry.content || '';
    DOM.btnDeleteJournalEntry.style.display = 'inline-flex';
    renderJournalList(journalEntriesCache);
  }

  function createNewJournalEntry() {
    STATE.activeJournalId = null;
    DOM.journalTitleInput.value = '';
    DOM.journalContentInput.value = '';
    DOM.journalPromptSelect.value = '';
    DOM.btnDeleteJournalEntry.style.display = 'none';
    renderJournalList(journalEntriesCache);
    DOM.journalTitleInput.focus();
  }

  async function saveJournalEntry() {
    const title = DOM.journalTitleInput.value.trim() || 'Untitled Entry';
    const content = DOM.journalContentInput.value.trim();

    if (!content) {
      alert('Please write something in your journal entry before saving.');
      return;
    }

    try {
      if (STATE.activeJournalId) {
        const res = await apiFetch(`/api/journal/${STATE.activeJournalId}`, {
          method: 'PUT',
          body: JSON.stringify({ title, content })
        });
        if (!res.ok) throw new Error('Failed to update entry');
        alert('Journal entry updated.');
      } else {
        const res = await apiFetch('/api/journal', {
          method: 'POST',
          body: JSON.stringify({ title, content })
        });
        if (!res.ok) throw new Error('Failed to save entry');
        const saved = await res.json();
        STATE.activeJournalId = saved.id;
        DOM.btnDeleteJournalEntry.style.display = 'inline-flex';
        alert('Journal entry saved privately.');
      }
      loadJournalEntries();
    } catch (err) {
      alert('Could not save journal entry. Please try again.');
    }
  }

  async function deleteJournalEntry() {
    if (!STATE.activeJournalId) return;
    if (confirm('Delete this journal entry permanently?')) {
      try {
        await apiFetch(`/api/journal/${STATE.activeJournalId}`, { method: 'DELETE' });
        createNewJournalEntry();
        loadJournalEntries();
      } catch (err) {
        alert('Could not delete entry.');
      }
    }
  }

  // ==========================================================================
  // 9. Helpline Resources (India Dedicated)
  // ==========================================================================
  async function loadHelplineResources() {
    if (!DOM.resourcesContainer) return;
    DOM.resourcesContainer.innerHTML = '<div style="color:var(--text-muted); font-size:13px; text-align:center; padding:20px;">Loading helpline directory...</div>';

    try {
      const res = await fetch('/api/resources/private-help');
      if (!res.ok) throw new Error('Failed to load helpline data');
      const data = await res.json();

      DOM.resourcesContainer.innerHTML = '';
      (data.services || []).forEach(s => {
        const card = document.createElement('div');
        card.className = 'resource-card';
        card.innerHTML = `
          <div class="resource-header">
            <div>
              <h3 class="resource-title">${escapeHtml(s.name)}</h3>
              <span class="resource-category">${escapeHtml(s.category)}</span>
            </div>
            ${s.badge ? `<span class="resource-badge">${escapeHtml(s.badge)}</span>` : ''}
          </div>
          <p class="resource-desc">${escapeHtml(s.description)}</p>
          <div class="resource-contact-row">
            <span class="resource-phone">${escapeHtml(s.display_phone || s.phone)}</span>
            <div style="display:flex; gap:8px;">
              ${s.call_link ? `<a href="${s.call_link}" class="btn-call-primary">📞 Call</a>` : ''}
              ${s.whatsapp_link ? `<a href="${s.whatsapp_link}" target="_blank" rel="noopener noreferrer" class="btn-call-primary" style="background:#16A34A;">💬 WhatsApp</a>` : ''}
            </div>
          </div>
          <div style="font-size:11.5px; color:var(--text-muted); margin-top:8px;">
            🕒 Availability: ${escapeHtml(s.availability || '24/7')}
          </div>
        `;
        DOM.resourcesContainer.appendChild(card);
      });
    } catch (e) {
      console.error('Failed to load helpline resources', e);
    }
  }

  // ==========================================================================
  // 10. Real Authentication & Account Management
  // ==========================================================================
  function initAuth() {
    updateProfileUI();

    if (DOM.btnProfileTrigger) {
      DOM.btnProfileTrigger.onclick = (e) => {
        e.preventDefault();
        DOM.modalProfile.classList.add('active');
        DOM.authErrorMsg.style.display = 'none';
        updateProfileUI();
      };
    }

    if (DOM.btnCloseProfile) {
      DOM.btnCloseProfile.onclick = (e) => {
        e.preventDefault();
        DOM.modalProfile.classList.remove('active');
      };
    }

    if (DOM.btnTabSignin) {
      DOM.btnTabSignin.onclick = (e) => {
        e.preventDefault();
        DOM.btnTabSignin.classList.add('active');
        DOM.btnTabSignup.classList.remove('active');
        DOM.formSignin.style.display = 'flex';
        DOM.formSignup.style.display = 'none';
        DOM.authErrorMsg.style.display = 'none';
      };
    }

    if (DOM.btnTabSignup) {
      DOM.btnTabSignup.onclick = (e) => {
        e.preventDefault();
        DOM.btnTabSignup.classList.add('active');
        DOM.btnTabSignin.classList.remove('active');
        DOM.formSignup.style.display = 'flex';
        DOM.formSignin.style.display = 'none';
        DOM.authErrorMsg.style.display = 'none';
      };
    }

    // Google Sign In Handler
    if (DOM.btnGoogleSignin) {
      DOM.btnGoogleSignin.onclick = async (e) => {
        e.preventDefault();
        DOM.authErrorMsg.style.display = 'none';

        const promptEmail = prompt('Sign in with Google - Enter your Google email address:', (STATE.currentUser ? STATE.currentUser.email : 'student@gmail.com'));
        if (!promptEmail || !promptEmail.trim()) return;

        const email = promptEmail.trim().toLowerCase();
        const rawName = email.split('@')[0].replace(/[._-]/g, ' ');
        const name = rawName.charAt(0).toUpperCase() + rawName.slice(1);

        try {
          const res = await fetch('/api/auth/google', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: email,
              name: name
            })
          });

          if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Google sign-in failed');
          }

          const data = await res.json();
          STATE.authToken = data.token;
          STATE.currentUser = data.user;
          localStorage.setItem('olive_auth_token', data.token);
          localStorage.setItem('olive_user', JSON.stringify(data.user));

          DOM.modalProfile.classList.remove('active');
          updateProfileUI();
          startNewConversation();
          alert(`Signed in with Google as ${data.user.username}!`);
        } catch (err) {
          DOM.authErrorMsg.textContent = err.message;
          DOM.authErrorMsg.style.display = 'block';
        }
      };
    }

    // Sign In Form Submission
    if (DOM.formSignin) {
      DOM.formSignin.onsubmit = async (e) => {
        e.preventDefault();
        DOM.authErrorMsg.style.display = 'none';
        const userOrEmail = document.getElementById('signin-user').value.trim();
        const password = document.getElementById('signin-pass').value;

        try {
          const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username_or_email: userOrEmail, password })
          });

          if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Login failed');
          }

          const data = await res.json();
          STATE.authToken = data.token;
          STATE.currentUser = data.user;
          localStorage.setItem('olive_auth_token', data.token);
          localStorage.setItem('olive_user', JSON.stringify(data.user));

          DOM.modalProfile.classList.remove('active');
          updateProfileUI();
          startNewConversation();
          alert(`Welcome back, ${data.user.username}!`);
        } catch (err) {
          DOM.authErrorMsg.textContent = err.message;
          DOM.authErrorMsg.style.display = 'block';
        }
      };
    }

    // Sign Up Form Submission
    if (DOM.formSignup) {
      DOM.formSignup.onsubmit = async (e) => {
        e.preventDefault();
        DOM.authErrorMsg.style.display = 'none';
        const username = document.getElementById('signup-user').value.trim();
        const email = document.getElementById('signup-email').value.trim();
        const password = document.getElementById('signup-pass').value;

        try {
          const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
          });

          if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Registration failed');
          }

          const data = await res.json();
          STATE.authToken = data.token;
          STATE.currentUser = data.user;
          localStorage.setItem('olive_auth_token', data.token);
          localStorage.setItem('olive_user', JSON.stringify(data.user));

          DOM.modalProfile.classList.remove('active');
          updateProfileUI();
          startNewConversation();
          alert(`Account created successfully! Welcome to Olive, ${data.user.username}.`);
        } catch (err) {
          DOM.authErrorMsg.textContent = err.message;
          DOM.authErrorMsg.style.display = 'block';
        }
      };
    }

    // Sign Out
    if (DOM.btnSignOut) {
      DOM.btnSignOut.onclick = (e) => {
        e.preventDefault();
        STATE.authToken = null;
        STATE.currentUser = null;
        localStorage.removeItem('olive_auth_token');
        localStorage.removeItem('olive_user');
        updateProfileUI();
        DOM.modalProfile.classList.remove('active');
        startNewConversation();
        alert('You have signed out.');
      };
    }

    // Verify session on launch
    if (STATE.authToken) {
      apiFetch('/api/auth/me').then(res => {
        if (res.ok) {
          return res.json();
        } else if (res.status === 401) {
          STATE.authToken = null;
          STATE.currentUser = null;
          localStorage.removeItem('olive_auth_token');
          localStorage.removeItem('olive_user');
          updateProfileUI();
        }
      }).then(user => {
        if (user) {
          STATE.currentUser = user;
          localStorage.setItem('olive_user', JSON.stringify(user));
          updateProfileUI();
        }
      }).catch(() => {});
    }
  }

  function updateProfileUI() {
    if (!DOM.authLoggedInView || !DOM.authFormsView) return;
    if (STATE.currentUser) {
      DOM.authLoggedInView.style.display = 'block';
      DOM.authFormsView.style.display = 'none';
      if (DOM.profileNameDisplay) DOM.profileNameDisplay.textContent = STATE.currentUser.username;
      if (DOM.profileEmailDisplay) DOM.profileEmailDisplay.textContent = STATE.currentUser.email;
      if (DOM.profileAvatarDisplay) DOM.profileAvatarDisplay.textContent = STATE.currentUser.username.charAt(0).toUpperCase();
      if (DOM.userAvatarIcon) {
        DOM.userAvatarIcon.textContent = '👤';
        DOM.userAvatarIcon.style.color = 'var(--primary)';
      }
    } else {
      DOM.authLoggedInView.style.display = 'none';
      DOM.authFormsView.style.display = 'block';
      if (DOM.userAvatarIcon) {
        DOM.userAvatarIcon.textContent = '👤';
        DOM.userAvatarIcon.style.color = 'inherit';
      }
    }
  }

  // ==========================================================================
  // 11. Multi-Slide Quick Privacy Hide Disguise
  // ==========================================================================
  const STUDY_SLIDES = [
    {
      subject: "Biology",
      topic: "Cell Structure & Organelles",
      course: "AP / IB Biology — Unit 2: Cellular Organization",
      last_edited: "Today at 3:42 PM",
      breadcrumbs: ["Science", "Grade 11 Biology", "Cell Structure"],
      summary: "Core structural components of eukaryotic and prokaryotic cells, membrane transport mechanisms, and organelle compartmentalization.",
      sections: [
        {
          heading: "1. Eukaryotic vs. Prokaryotic Cells",
          content: "Prokaryotes (Bacteria, Archaea) lack membrane-bound nucleus; genetic material resides in nucleoid region. Circular plasmid DNA often present. Eukaryotes (Animals, Plants, Fungi) contain membrane-bound organelles with distinct biochemical microenvironments.",
          bullets: [
            "Plasma Membrane: Phospholipid bilayer with fluid mosaic model (amphipathic molecules).",
            "Ribosomes: 70S in prokaryotes, 80S in eukaryotic cytoplasm and rough endoplasmic reticulum.",
            "Endosymbiotic Theory: Mitochondria and Chloroplasts originated from engulfed aerobic bacteria."
          ]
        },
        {
          heading: "2. Endomembrane System Flow",
          content: "Nucleus (transcription to mRNA) → Rough ER (translation & peptide folding) → Transport Vesicles → Golgi Apparatus (cis face phosphorylation & glycosylation, trans face sorting) → Secretory Vesicles or Lysosomes.",
          key_terms: ["Rough ER", "Golgi Apparatus", "Lysosome hydrolases", "Exocytosis"]
        },
        {
          heading: "3. Mitochondria & ATP Generation",
          content: "Inner mitochondrial membrane contains cristae to maximize surface area for electron transport chain (ETC) complexes and ATP Synthase (chemiosmosis gradient H+ across intermembrane space).",
          formula: "C6H12O6 + 6O2 → 6CO2 + 6H2O + ~30-32 ATP"
        }
      ]
    },
    {
      subject: "Economics",
      topic: "Demand, Supply & Market Equilibrium",
      course: "Intro to Microeconomics — Module 3",
      last_edited: "Yesterday at 6:15 PM",
      breadcrumbs: ["Social Sciences", "Economics 101", "Price Theory"],
      summary: "Mechanisms of market price determination, determinants of demand/supply shifts, and elasticity coefficients.",
      sections: [
        {
          heading: "1. The Law of Demand & Substitution Effect",
          content: "Inverse relationship between price (P) and quantity demanded (Qd), ceteris paribus. As price rises, purchasing power diminishes (Income Effect) and consumers substitute towards cheaper alternatives (Substitution Effect).",
          bullets: [
            "Demand Curve Shifters: Consumer income (normal vs inferior goods), prices of related goods (substitutes vs complements), tastes & preferences, future price expectations.",
            "Movement along curve: ONLY caused by change in the good's own price."
          ]
        },
        {
          heading: "2. Price Elasticity of Demand (PED)",
          content: "Measures the responsiveness of quantity demanded to a change in price.",
          formula: "PED = (% Change in Qd) / (% Change in Price) = (ΔQ / Q_avg) / (ΔP / P_avg)",
          bullets: [
            "|PED| > 1: Elastic (Luxury goods, many substitutes available).",
            "|PED| < 1: Inelastic (Necessities, addictive goods, few alternatives).",
            "|PED| = 1: Unit elastic (Total revenue is maximized)."
          ]
        },
        {
          heading: "3. Market Equilibrium & Deadweight Loss",
          content: "Equilibrium occurs where Qd = Qs. Price ceilings below equilibrium create shortages; price floors above equilibrium create surpluses and producer deadweight loss."
        }
      ]
    },
    {
      subject: "Chemistry",
      topic: "Chemical Equilibrium & Le Chatelier's Principle",
      course: "General Chemistry II — Chapter 14",
      last_edited: "Sep 1 at 11:20 AM",
      breadcrumbs: ["Physical Sciences", "Chemistry", "Equilibrium"],
      summary: "Dynamic equilibrium in reversible reactions, equilibrium constants (Kc, Kp), and stress response mechanisms.",
      sections: [
        {
          heading: "1. Dynamic Equilibrium Definition",
          content: "Occurs in a closed system when the rate of the forward reaction equals the rate of the reverse reaction. Concentrations of reactants and products remain constant over time, though reactions continue simultaneously.",
          formula: "aA + bB ⇌ cC + dD  ==>  Kc = ([C]^c * [D]^d) / ([A]^a * [B]^b)"
        },
        {
          heading: "2. Le Chatelier's Principle Applications",
          content: "If an external stress (concentration, temperature, pressure/volume) is applied to a system at equilibrium, the system shifts in the direction that partially offsets the stress.",
          bullets: [
            "Adding reactant: Shifts forward (to the right) to consume excess reactant.",
            "Increasing pressure (decreasing volume): Shifts toward the side with fewer moles of gas.",
            "Exothermic reaction (ΔH < 0): Increasing temperature shifts left (acts like adding product heat)."
          ]
        },
        {
          heading: "3. Reaction Quotient (Q) vs. Equilibrium Constant (K)",
          content: "If Q < K, forward reaction proceeds (shifts right). If Q > K, reverse reaction proceeds (shifts left). If Q = K, system is at equilibrium."
        }
      ]
    },
    {
      subject: "History",
      topic: "The Industrial Revolution (1760–1840)",
      course: "World History — Era 7: Modern Transformations",
      last_edited: "Aug 29 at 4:05 PM",
      breadcrumbs: ["Humanities", "Modern World History", "Industrialization"],
      summary: "Technological innovations, agrarian shift, urbanization patterns, and socioeconomic class reorganization in 18th-century Britain.",
      sections: [
        {
          heading: "1. Preconditions in Great Britain",
          content: "Why Britain first? Abundant coal and iron ore deposits, capital accumulation from global trade empires, agricultural revolution producing labor surplus, stable patent laws, and insular geography with navigable waterways.",
          bullets: [
            "Enclosure Acts: Consolidated common land, driving rural laborers into industrial urban centers.",
            "Steam Power: James Watt's condensation chamber innovation (1769) detached manufacturing from riverbanks."
          ]
        },
        {
          heading: "2. Key Technological Inventions",
          content: "Textiles led mechanization: John Kay's Flying Shuttle (1733), James Hargreaves' Spinning Jenny (1764), Richard Arkwright's Water Frame (1769), and Cartwright's Power Loom (1785).",
          key_terms: ["Cottage Industry", "Factory System", "Urban Sprawl", "Proletariat"]
        },
        {
          heading: "3. Socioeconomic Repercussions",
          content: "Rapid demographic migration to Manchester, Birmingham, Leeds. Lack of sanitation infrastructure led to cholera outbreaks. Emergence of the industrial middle class (bourgeoisie) and organized labor movements (Chartism, Luddites)."
        }
      ]
    },
    {
      subject: "Physics",
      topic: "Newton's Laws of Motion & Classical Mechanics",
      course: "Mechanics & Dynamics — Chapter 4",
      last_edited: "Aug 31 at 2:10 PM",
      breadcrumbs: ["STEM", "Physics 1", "Dynamics"],
      summary: "Vector analysis of forces, inertia, acceleration under net force, action-reaction pairs, and friction coefficients.",
      sections: [
        {
          heading: "1. First & Second Laws of Motion",
          content: "Law of Inertia: An object maintains constant velocity unless acted upon by a non-zero net external force. Second Law: Net force equals the time rate of change of momentum (F_net = m * a for constant mass).",
          formula: "Σ F = m * a   |   F_friction = μ * N   |   p = m * v"
        },
        {
          heading: "2. Free Body Diagrams & Inclined Planes",
          content: "Resolution of gravitational force on angle θ: Parallel component F_parallel = m*g*sin(θ); Perpendicular component F_perp = m*g*cos(θ). Normal force N = m*g*cos(θ) on static incline.",
          bullets: [
            "Static Friction (μs): Maximum resistive force before motion begins (fs ≤ μs * N).",
            "Kinetic Friction (μk): Constant resistive force during sliding motion (fk = μk * N, μk < μs)."
          ]
        },
        {
          heading: "3. Newton's Third Law Pairs",
          content: "For every interaction, forces occur in equal magnitude and opposite direction acting on DIFFERENT bodies. Action-reaction pairs never cancel out on a single free body diagram."
        }
      ]
    },
    {
      subject: "Mathematics",
      topic: "Differential Calculus & Derivatives",
      course: "Calculus AB — Chapter 3: Differentiation",
      last_edited: "Sep 1 at 9:45 AM",
      breadcrumbs: ["Math", "Calculus", "Differentiation Rules"],
      summary: "Limit definition of derivatives, product/quotient/chain rules, implicit differentiation, and tangent line equations.",
      sections: [
        {
          heading: "1. Definition of the Derivative",
          content: "The derivative represents the instantaneous rate of change of a function f(x) at point x, defined geometrically as the slope of the tangent line.",
          formula: "f'(x) = lim (h → 0) [f(x + h) - f(x)] / h"
        },
        {
          heading: "2. Fundamental Differentiation Rules",
          content: "Standard operational rules for computing derivatives of composite and algebraic functions without limits.",
          bullets: [
            "Power Rule: d/dx [x^n] = n * x^(n-1)",
            "Product Rule: d/dx [u * v] = u' * v + u * v'",
            "Quotient Rule: d/dx [u / v] = (u' * v - u * v') / v^2",
            "Chain Rule: d/dx [f(g(x))] = f'(g(x)) * g'(x)"
          ]
        },
        {
          heading: "3. Optimization & First Derivative Test",
          content: "Set f'(x) = 0 or undefined to locate critical points. If f' changes from positive to negative, x is a local maximum. If f' changes from negative to positive, x is a local minimum."
        }
      ]
    },
    {
      subject: "Geography",
      topic: "Plate Tectonics & Seismic Activity",
      course: "Physical Geography — Unit 4: Earth Systems",
      last_edited: "Sep 2 at 1:15 PM",
      breadcrumbs: ["Earth Sciences", "Geography 101", "Geomorphology"],
      summary: "Lithospheric plate boundaries, subduction zones, continental drift evidence, seismic wave propagation (P and S waves), and volcanism.",
      sections: [
        {
          heading: "1. Plate Boundary Classifications",
          content: "Interactions along plate margins determine seismic and volcanic hazard profiles worldwide.",
          bullets: [
            "Divergent Boundaries: Plates pull apart (Mid-Atlantic Ridge, East African Rift Valley), creating new oceanic crust via upwelling magma.",
            "Convergent Boundaries: Subduction of denser oceanic crust beneath continental crust (Ring of Fire) or continental-continental collision (Himalayas).",
            "Transform Boundaries: Lateral strike-slip faults (San Andreas Fault) generating high-magnitude shallow focus earthquakes without volcanism."
          ]
        },
        {
          heading: "2. Seismic Wave Characteristics",
          content: "Primary (P) waves are compressional longitudinal waves traveling through solids and liquids. Secondary (S) waves are transverse shear waves traveling only through solids, establishing Earth's liquid outer core shadow zone.",
          formula: "Vp = √((K + 4/3 μ) / ρ)   |   Vs = √(μ / ρ)"
        }
      ]
    },
    {
      subject: "English",
      topic: "Narrative Structures & Motif Analysis",
      course: "AP Literature & Composition — Module 2: Prose Analysis",
      last_edited: "Today at 10:30 AM",
      breadcrumbs: ["Humanities", "English Literature", "Critical Analysis"],
      summary: "Exploration of recurring symbolic motifs, non-linear chronological sequencing, unreliable narrators, and socio-cultural subtext in modern literature.",
      sections: [
        {
          heading: "1. Freytag's Pyramid & Non-Linear Framing",
          content: "Traditional dramatic arc (Exposition → Inciting Incident → Rising Action → Climax → Falling Action → Resolution) contrasted with in media res openers, epistolary frames, and stream-of-consciousness focalization.",
          bullets: [
            "Diegetic Levels: Intradiegetic narrators within the story world vs. extradiegetic omniscient observers.",
            "Dramatic Irony: Discrepancy between reader omniscience and protagonist awareness.",
            "Foil Characters: Juxtaposition designed to illuminate contrasting moral or psychological traits."
          ]
        },
        {
          heading: "2. Symbolism vs. Leitmotif",
          content: "A motif is a recurring thematic element (colors, weather phenomena, recurring phraseology) that accumulates symbolic resonance over the text's progression, reinforcing the core philosophical inquiry of the author.",
          key_terms: ["Allegory", "Synecdoche", "Syntactical Pacing", "Catharsis"]
        }
      ]
    }
  ];

  let currentStudySlideIndex = -1;

  function renderStudySlide(index) {
    if (!STUDY_SLIDES.length) return;
    const normIndex = ((index % STUDY_SLIDES.length) + STUDY_SLIDES.length) % STUDY_SLIDES.length;
    const slide = STUDY_SLIDES[normIndex];

    if (DOM.studyNbTitle) DOM.studyNbTitle.textContent = `StudyNotes • ${slide.subject} Workspace`;
    if (DOM.studyBreadcrumbsDisplay && slide.breadcrumbs) {
      DOM.studyBreadcrumbsDisplay.textContent = slide.breadcrumbs.join(' > ');
    }
    if (DOM.studyLastSaved) DOM.studyLastSaved.textContent = `Saved ${slide.last_edited || 'just now'}`;
    if (DOM.studySidebarCourse) DOM.studySidebarCourse.textContent = slide.course || slide.subject;
    if (DOM.studySubjectTag) DOM.studySubjectTag.textContent = slide.subject || 'Academic Notes';
    if (DOM.studyMainHeading) DOM.studyMainHeading.textContent = slide.topic || 'Subject Overview';
    if (DOM.studyEditTime) DOM.studyEditTime.textContent = `Last edited ${slide.last_edited || 'recently'}`;
    if (DOM.studySummaryText) DOM.studySummaryText.textContent = slide.summary || '';

    if (DOM.studySectionsContainer) {
      let html = '';
      (slide.sections || []).forEach(sec => {
        html += `
          <div class="study-card">
            <h2 class="study-section-title">${escapeHtml(sec.heading)}</h2>
            <div class="study-section-content">${escapeHtml(sec.content || sec.body || '')}</div>
            ${sec.formula ? `
              <div style="margin: 10px 0; padding: 8px 12px; background: #F3F4F6; border-left: 3px solid #6366F1; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 13px; color: #1F2937; border-radius: 4px;">
                ${escapeHtml(sec.formula)}
              </div>
            ` : ''}
            ${sec.bullets && sec.bullets.length ? `
              <ul class="study-bullet-list">
                ${sec.bullets.map(b => `<li>${escapeHtml(b)}</li>`).join('')}
              </ul>
            ` : ''}
            ${sec.key_terms && sec.key_terms.length ? `
              <div style="margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; align-items: center;">
                <span style="font-size: 11.5px; font-weight: 600; color: #4B5563;">Key Terms:</span>
                ${sec.key_terms.map(t => `<span style="font-size: 11.5px; padding: 2px 8px; background: #EEF2FF; color: #4F46E5; border-radius: 9999px;">${escapeHtml(t)}</span>`).join('')}
              </div>
            ` : ''}
          </div>
        `;
      });
      DOM.studySectionsContainer.innerHTML = html;
    }
  }

  // ==========================================================================
  // 12. Quick Privacy Hide & Theme Toggle
  // ==========================================================================
  function initPrivacyHide() {
    if (DOM.btnQuickHide) {
      DOM.btnQuickHide.onclick = (e) => {
        e.preventDefault();
        showPrivacyHide();
      };
    }

    if (DOM.btnReturnFromHide) {
      DOM.btnReturnFromHide.onclick = (e) => {
        e.preventDefault();
        hidePrivacyHide();
      };
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        if (DOM.privacyHideOverlay && DOM.privacyHideOverlay.classList.contains('active')) {
          hidePrivacyHide();
        } else {
          showPrivacyHide();
        }
      }
    });

    // Populate initial study note slide
    renderStudySlide(0);

    // Fetch any dynamic updates from backend
    fetchStudyNotesData();
  }

  function showPrivacyHide() {
    if (!DOM.privacyHideOverlay) return;
    currentStudySlideIndex = (currentStudySlideIndex + 1) % STUDY_SLIDES.length;
    renderStudySlide(currentStudySlideIndex);
    DOM.privacyHideOverlay.classList.add('active');
    DOM.privacyHideOverlay.setAttribute('aria-hidden', 'false');
  }

  function hidePrivacyHide() {
    if (!DOM.privacyHideOverlay) return;
    DOM.privacyHideOverlay.classList.remove('active');
    DOM.privacyHideOverlay.setAttribute('aria-hidden', 'true');
  }

  async function fetchStudyNotesData() {
    try {
      const res = await fetch('/api/resources/study-notes');
      if (res.ok) {
        const subjects = await res.json();
        if (Array.isArray(subjects) && subjects.length) {
          STUDY_SLIDES.length = 0;
          subjects.forEach(s => STUDY_SLIDES.push(s));
          if (currentStudySlideIndex < 0) {
            renderStudySlide(0);
          }
        }
      }
    } catch (e) {}
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.body.setAttribute('data-theme', theme);
    if (DOM.themeIcon) {
      DOM.themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
  }

  function initTheme() {
    const saved = localStorage.getItem('olive_theme') || 'light';
    applyTheme(saved);

    if (DOM.btnThemeToggle) {
      DOM.btnThemeToggle.onclick = (e) => {
        e.preventDefault();
        const cur = document.body.getAttribute('data-theme') || 'light';
        const next = cur === 'dark' ? 'light' : 'dark';
        applyTheme(next);
        localStorage.setItem('olive_theme', next);
      };
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // ==========================================================================
  // 13. Event Listeners Wiring & App Boot
  // ==========================================================================
  function wireEventListeners() {
    // Return to Home on logo or title click
    const brandElements = document.querySelectorAll('#brand-home-link, .brand-wrapper, .brand-icon-box, .brand-logo-img, .brand-name');
    brandElements.forEach(el => {
      el.onclick = (e) => {
        e.preventDefault();
        switchTab('chat');
      };
      el.onkeydown = (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          switchTab('chat');
        }
      };
    });

    // Protected History Header Lock shortcut
    if (DOM.btnHeaderLock) {
      DOM.btnHeaderLock.onclick = (e) => {
        e.preventDefault();
        switchTab('history');
      };
    }

    // Navigation Pills
    if (DOM.navPills) {
      DOM.navPills.forEach(btn => {
        btn.onclick = (e) => {
          e.preventDefault();
          const tab = btn.getAttribute('data-tab') || btn.dataset.tab;
          switchTab(tab);
        };
      });
    }

    // Global Keypad Listener for Protected History PIN
    document.addEventListener('keydown', (e) => {
      if (STATE.currentTab === 'history' && !STATE.isHistoryUnlocked) {
        if (/^[0-9]$/.test(e.key)) {
          handlePinKeyClick(e.key);
        } else if (e.key === 'Backspace') {
          STATE.currentPinInput = STATE.currentPinInput.slice(0, -1);
          updatePinDots();
          if (DOM.pinErrorMsg) DOM.pinErrorMsg.textContent = '';
        } else if (e.key.toLowerCase() === 'c' && (!DOM.privacyHideOverlay || !DOM.privacyHideOverlay.classList.contains('active'))) {
          STATE.currentPinInput = '';
          updatePinDots();
          if (DOM.pinErrorMsg) DOM.pinErrorMsg.textContent = '';
        }
      }
    });

    // Chat Modes
    if (DOM.modeCards) {
      DOM.modeCards.forEach(card => {
        card.onclick = () => setChatMode(card.dataset.mode);
      });
    }

    // Chat Actions
    if (DOM.btnChatSend) DOM.btnChatSend.onclick = handleSendMessage;
    if (DOM.chatInput) {
      DOM.chatInput.onkeydown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          handleSendMessage();
        }
      };
      DOM.chatInput.oninput = () => {
        DOM.chatInput.style.height = 'auto';
        DOM.chatInput.style.height = Math.min(DOM.chatInput.scrollHeight, 120) + 'px';
      };
    }

    if (DOM.btnNewChat) DOM.btnNewChat.onclick = startNewConversation;
    if (DOM.btnExportChat) DOM.btnExportChat.onclick = exportChatHistory;

    // Mic
    initSpeechRecognition();
    if (DOM.btnChatMic) DOM.btnChatMic.onclick = toggleSpeechRecognition;

    // Calming Exercises
    if (DOM.exerciseTabBtns) {
      DOM.exerciseTabBtns.forEach(btn => {
        btn.onclick = () => {
          AUDIO.init();
          loadExercise(btn.dataset.ex);
        };
      });
    }

    if (DOM.btnExerciseToggle) {
      DOM.btnExerciseToggle.onclick = () => {
        AUDIO.init();
        toggleExercise();
      };
    }

    if (DOM.btnChimeToggle) {
      DOM.btnChimeToggle.onclick = () => {
        AUDIO.init();
        STATE.chimeSoundEnabled = !STATE.chimeSoundEnabled;
        if (DOM.chimeStatusText) DOM.chimeStatusText.textContent = STATE.chimeSoundEnabled ? 'On' : 'Off';
        if (STATE.chimeSoundEnabled) {
          AUDIO.playChime(432, 1.4);
        }
      };
    }

    if (DOM.btnReleaseThought) DOM.btnReleaseThought.onclick = addThoughtLeaf;
    if (DOM.thoughtInput) {
      DOM.thoughtInput.onkeydown = (e) => { if (e.key === 'Enter') addThoughtLeaf(); };
    }

    // Protected History PIN Keypad
    if (DOM.pinKeys) {
      DOM.pinKeys.forEach(btn => {
        btn.onclick = (e) => {
          e.preventDefault();
          handlePinKeyClick(btn.dataset.num);
        };
      });
    }

    if (DOM.btnPinClear) {
      DOM.btnPinClear.onclick = (e) => {
        e.preventDefault();
        STATE.currentPinInput = '';
        updatePinDots();
        if (DOM.pinErrorMsg) DOM.pinErrorMsg.textContent = '';
      };
    }

    if (DOM.btnPinBackspace) {
      DOM.btnPinBackspace.onclick = (e) => {
        e.preventDefault();
        STATE.currentPinInput = STATE.currentPinInput.slice(0, -1);
        updatePinDots();
        if (DOM.pinErrorMsg) DOM.pinErrorMsg.textContent = '';
      };
    }

    if (DOM.btnPurgeHistory) {
      DOM.btnPurgeHistory.onclick = async (e) => {
        e.preventDefault();
        if (confirm('Permanently delete all your conversation history? This cannot be undone.')) {
          await apiFetch('/api/chat/sessions', { method: 'DELETE' });
          loadHistorySessions();
        }
      };
    }

    // Viewer modal
    if (DOM.btnCloseViewer) DOM.btnCloseViewer.onclick = () => DOM.modalConversationViewer.classList.remove('active');
    if (DOM.btnViewerCloseFooter) DOM.btnViewerCloseFooter.onclick = () => DOM.modalConversationViewer.classList.remove('active');
    if (DOM.btnViewerContinue) DOM.btnViewerContinue.onclick = continueViewingConversation;

    // Feelings
    initFeelings();

    // Journal
    if (DOM.btnNewJournalEntry) DOM.btnNewJournalEntry.onclick = createNewJournalEntry;
    if (DOM.btnSaveJournalEntry) DOM.btnSaveJournalEntry.onclick = saveJournalEntry;
    if (DOM.btnDeleteJournalEntry) DOM.btnDeleteJournalEntry.onclick = deleteJournalEntry;
    if (DOM.journalSearchInput) {
      DOM.journalSearchInput.oninput = () => {
        const q = DOM.journalSearchInput.value.toLowerCase();
        const filtered = journalEntriesCache.filter(e => 
          (e.title && e.title.toLowerCase().includes(q)) || 
          (e.content && e.content.toLowerCase().includes(q))
        );
        renderJournalList(filtered);
      };
    }
    if (DOM.journalPromptSelect) {
      DOM.journalPromptSelect.onchange = () => {
        const promptText = DOM.journalPromptSelect.value;
        if (promptText && DOM.journalContentInput) {
          DOM.journalContentInput.value = promptText + '\n\n' + DOM.journalContentInput.value;
        }
      };
    }

    // Auth
    initAuth();

    // Privacy Hide & Theme
    initPrivacyHide();
    initTheme();
  }

  // App Bootstrap (Reliable Execution under any document ready state)
  function bootstrap() {
    initDOM();
    wireEventListeners();
    setChatMode('just_listen');
    loadExercise('box_breathing');
    loadHelplineResources();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootstrap);
  } else {
    bootstrap();
  }

})();

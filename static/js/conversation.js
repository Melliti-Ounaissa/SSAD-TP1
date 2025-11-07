// [REMPLACER TOUT LE FICHIER conversation.js]

const messagesArea = document.getElementById('messages-area');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const algorithmSelect = document.getElementById('algorithm-select');
const keyInputsDiv = document.getElementById('key-inputs');
const refreshBtn = document.getElementById('refresh-btn');

// Nouveaux éléments pour les onglets et la stéganographie
const cryptoInputArea = document.getElementById('crypto-input-area');
const stegoInputArea = document.getElementById('stego-input-area');
const stegoMessageInput = document.getElementById('stego-message-input');
const stegoFileInput = document.getElementById('stego-file-input');
const stegoFileInfo = document.getElementById('stego-file-info');
const sendError = document.getElementById('send-error');
const modeSwitcher = document.querySelector('.mode-switcher');
let currentSendMode = 'crypto'; // 'crypto' or 'stego'

let otherUsername = '';
const decryptTimers = {};
const decryptedMessages = new Set(); // Pour le déchiffrement crypto

// --- GESTION DES ONGLETS ---

modeSwitcher.addEventListener('click', (e) => {
  if (e.target.classList.contains('mode-btn')) {
    const mode = e.target.dataset.mode;
    if (mode === currentSendMode) return;

    currentSendMode = mode;
    sendError.textContent = ''; // Vider les erreurs

    // Mettre à jour les boutons
    document
      .querySelector('.mode-btn.active')
      .classList.remove('active');
    e.target.classList.add('active');

    // Afficher la bonne zone de saisie
    if (mode === 'crypto') {
      cryptoInputArea.classList.add('active');
      stegoInputArea.classList.remove('active');
      sendBtn.textContent = 'Envoyer';
    } else {
      cryptoInputArea.classList.remove('active');
      stegoInputArea.classList.add('active');
      sendBtn.textContent = 'Envoyer (Audio)';
    }
  }
});

stegoFileInput.addEventListener('change', () => {
  if (stegoFileInput.files.length > 0) {
    const file = stegoFileInput.files[0];
    stegoFileInfo.textContent = `Fichier: ${
      file.name
    } (${(file.size / 1024).toFixed(1)} Ko)`;
  } else {
    stegoFileInfo.textContent = '';
  }
});

// --- LOGIQUE DE CRYPTOGRAPHIE (Texte) ---

function updateKeyInputs() {
  const algorithm = algorithmSelect.value;
  let html = '';

  switch (algorithm) {
    case 'ceasar':
      html = `
                <label class="input-label">Shift:</label>
                <input type="number" id="caesar-shift" value="3" min="1" max="25" class="neon-input">
                <label class="input-label">Direction:</label>
                <select id="caesar-direction" class="neon-select">
                    <option value="droite">Droite →</option>
                    <option value="gauche">Gauche ←</option>
                </select>
            `;
      break;
    case 'playfair':
      html = `
                <label class="input-label">Key:</label>
                <input type="text" id="playfair-key" value="MONARCHY" maxlength="25" class="neon-input">
            `;
      break;
    case 'hill':
      html = `
                <label class="input-label">Key:</label>
                <input type="text" id="hill-key" value="FRID" placeholder="Length must be 4, 9, 16..." class="neon-input">
            `;
      break;
  }
  keyInputsDiv.innerHTML = html;
}

algorithmSelect.addEventListener('change', updateKeyInputs);

function getKeyParams(algorithm) {
  const params = {};
  try {
    switch (algorithm) {
      case 'ceasar':
        params.shift = parseInt(
          document.getElementById('caesar-shift').value,
        );
        params.direction = document.getElementById(
          'caesar-direction',
        ).value;
        break;
      case 'playfair':
        params.key = document.getElementById('playfair-key').value;
        break;
      case 'hill':
        params.key = document.getElementById('hill-key').value.trim();
        break;
    }
  } catch (e) {
    console.error('Erreur de récupération des clés:', e);
  }
  return params;
}

// --- CHARGEMENT ET AFFICHAGE DES MESSAGES (Unifié) ---

async function loadConversation() {
  try {
    const response = await fetch(
      `/api/messages/conversation/${otherUserId}`,
    );
    const data = await response.json();

    if (data.success && data.messages) {
      displayMessages(data.messages);
      if (data.messages.length > 0) {
        // Tente de trouver un nom d'utilisateur
        const firstMessage = data.messages[0];
        const other =
          firstMessage.sender_id === currentUserId
            ? firstMessage.receiver
            : firstMessage.sender;
        if (other && other.username) {
          otherUsername = other.username;
          document.getElementById(
            'conversation-title',
          ).textContent = `Conversation avec ${otherUsername}`;
        }
      }
    } else {
      console.error('Échec du chargement:', data.message);
      messagesArea.innerHTML =
        '<p class="no-messages">Erreur de chargement des messages</p>';
    }
  } catch (error) {
    console.error('Error loading conversation:', error);
    messagesArea.innerHTML =
      '<p class="no-messages">Erreur de connexion</p>';
  }
}

function displayMessages(messages) {
  if (messages.length === 0) {
    messagesArea.innerHTML =
      '<p class="no-messages">Aucun message pour le moment</p>';
    return;
  }

  const isScrolledToBottom =
    messagesArea.scrollHeight - messagesArea.clientHeight <=
    messagesArea.scrollTop + 1;

  messagesArea.innerHTML = '';
  messages.forEach((message) => {
    // Aiguillage vers la bonne fonction d'affichage
    if (message.message_type === 'crypto') {
      messagesArea.appendChild(createCryptoMessageElement(message));
    } else if (message.message_type === 'stego') {
      messagesArea.appendChild(createStegoMessageElement(message));
    }
  });

  if (isScrolledToBottom) {
    messagesArea.scrollTop = messagesArea.scrollHeight;
  }
}

// --- CRÉATION DES BULLES DE MESSAGE ---

function createCryptoMessageElement(message) {
  const isSent = message.sender_id === currentUserId;
  const div = document.createElement('div');
  div.className = `message-bubble ${isSent ? 'sent' : 'received'}`;
  div.dataset.messageId = message.id;

  const sender = isSent ? 'Vous' : message.sender.username;
  const date = new Date(message.date_created).toLocaleString('fr-FR');

  const isDecrypted = decryptedMessages.has(message.id);
  const messageText = isDecrypted
    ? '🔓 Message déchiffré (recharger pour re-chiffrer)'
    : escapeHtml(message.encrypted);
  const messageClass = isDecrypted ? 'decrypted-text' : 'encrypted';

  div.innerHTML = `
        <div class="message-info">${sender} • ${date} (Crypto)</div>
        <div class="message-text ${messageClass}" 
             data-encrypted="${escapeHtml(message.encrypted)}" 
             data-algo="${message.algo_name}" 
             data-key='${escapeHtml(message.algorithm_key || '{}')}'>
            ${messageText}
        </div>
        <div class="message-meta">Algorithme: ${capitalizeFirst(
          message.algo_name,
        )}</div>
        ${
          !isSent
            ? createDecryptButton(message.id, isDecrypted)
            : ''
        }
    `;

  return div;
}

function createStegoMessageElement(message) {
  const isSent = message.sender_id === currentUserId;
  const div = document.createElement('div');
  div.className = `message-bubble stego ${isSent ? 'sent' : 'received'}`;
  div.dataset.messageId = message.id;

  const sender = isSent ? 'Vous' : message.sender.username;
  const date = new Date(message.date_created).toLocaleString('fr-FR');

  div.innerHTML = `
        <div class="message-info">${sender} • ${date} (Audio)</div>
        <div class="message-text">
            <p>Message audio reçu :</p>
            <audio controls src="/api/stego/audio/${
              message.audio_filename
            }"></audio>
        </div>
        <div class="stego-decrypted-text" id="stego-decrypted-${
          message.id
        }"></div>
        
        ${
          !isSent
            ? `<button class="decrypt-stego-btn" onclick="decryptStegoMessage(this, ${message.id})">
                 🎵 Extraire le message
               </button>`
            : ''
        }
    `;
  return div;
}

function createDecryptButton(messageId, isDecrypted) {
  if (isDecrypted) {
    return '<button class="decrypt-btn decrypted" disabled>✅ Déchiffré</button>';
  } else {
    return '<button class="decrypt-btn" onclick="decryptCryptoMessage(this)">🔓 Déchiffrer (Texte)</button>';
  }
}

// --- LOGIQUE DE DÉCHIFFREMENT (Crypto & Stego) ---

async function decryptCryptoMessage(button) {
  const messageText = button.previousElementSibling.previousElementSibling;
  const encrypted = messageText.dataset.encrypted;
  const algorithm = messageText.dataset.algo;
  const keyParams = JSON.parse(messageText.dataset.key || '{}');
  const messageBubble = button.closest('.message-bubble');
  const messageId = messageBubble.dataset.messageId;

  if (decryptTimers[messageId]) {
    clearTimeout(decryptTimers[messageId]);
  }

  button.disabled = true;
  button.textContent = '⏳ Déchiffrement...';

  try {
    const response = await fetch('/api/crypto/decrypt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        encrypted_message: encrypted,
        algorithm: algorithm,
        key_params: keyParams,
      }),
    });
    const data = await response.json();

    if (data.success) {
      decryptedMessages.add(messageId);
      messageText.textContent = data.decrypted;
      messageText.classList.remove('encrypted');
      messageText.classList.add('decrypted-text'); // Ajout du style vert néon

      button.textContent = '✅ Déchiffré';
      button.disabled = true;
      button.classList.add('decrypted');

      // Timer pour re-cacher
      const DECRYPT_DISPLAY_TIME = 60000; // 1 minute
      decryptTimers[messageId] = setTimeout(() => {
        if (decryptedMessages.has(messageId)) {
          messageText.textContent = encrypted;
          messageText.classList.add('encrypted');
          messageText.classList.remove('decrypted-text');
          button.textContent = '🔓 Déchiffrer (Texte)';
          button.disabled = false;
          button.classList.remove('decrypted');
          decryptedMessages.delete(messageId);
          delete decryptTimers[messageId];
        }
      }, DECRYPT_DISPLAY_TIME);
    } else {
      alert('Erreur de déchiffrement: ' + data.message);
      button.disabled = false;
      button.textContent = '🔓 Déchiffrer (Texte)';
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Échec du déchiffrement');
    button.disabled = false;
    button.textContent = '🔓 Déchiffrer (Texte)';
  }
}

async function decryptStegoMessage(button, messageId) {
  const decryptedTextDiv = document.getElementById(
    `stego-decrypted-${messageId}`,
  );
  button.disabled = true;
  button.textContent = '⏳ Extraction...';

  try {
    const response = await fetch(`/api/stego/decrypt/${messageId}`);
    const data = await response.json();

    if (data.success) {
      decryptedTextDiv.textContent = `Message extrait: "${data.decrypted_message}"`;
      decryptedTextDiv.classList.add('show');
      button.textContent = '✅ Extrait';
    } else {
      decryptedTextDiv.textContent = `Erreur: ${data.message}`;
      decryptedTextDiv.classList.add('show');
      button.disabled = false;
      button.textContent = '🎵 Extraire le message';
    }
  } catch (error) {
    console.error('Error:', error);
    decryptedTextDiv.textContent = 'Échec de la connexion.';
    decryptedTextDiv.classList.add('show');
    button.disabled = false;
    button.textContent = '🎵 Extraire le message';
  }
}

// --- LOGIQUE D'ENVOI (Unifiée) ---

sendBtn.addEventListener('click', () => {
  if (currentSendMode === 'crypto') {
    sendCryptoMessage();
  } else {
    sendStegoMessage();
  }
});

messageInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (currentSendMode === 'crypto') {
      sendCryptoMessage();
    }
  }
});

async function sendCryptoMessage() {
  const message = messageInput.value.trim();
  const algorithm = algorithmSelect.value;
  if (!message) {
    sendError.textContent = 'Veuillez entrer un message';
    return;
  }
  sendError.textContent = '';
  const keyParams = getKeyParams(algorithm);

  sendBtn.disabled = true;
  sendBtn.textContent = 'Envoi...';

  try {
    const response = await fetch('/api/messages/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        algo_name: algorithm,
        receiver_id: otherUserId,
        key_params: keyParams,
      }),
    });
    const data = await response.json();
    if (data.success) {
      messageInput.value = '';
      await loadConversation();
    } else {
      sendError.textContent = 'Erreur: ' + data.message;
    }
  } catch (error) {
    console.error('Error:', error);
    sendError.textContent = "Échec de l'envoi du message";
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = 'Envoyer';
  }
}

async function sendStegoMessage() {
  const secretMessage = stegoMessageInput.value.trim();
  const audioFile =
    stegoFileInput.files.length > 0 ? stegoFileInput.files[0] : null;

  if (!secretMessage) {
    sendError.textContent = 'Veuillez entrer un message secret';
    return;
  }
  if (!audioFile) {
    sendError.textContent = 'Veuillez sélectionner un fichier .wav';
    return;
  }
  if (audioFile.type !== 'audio/wav') {
    sendError.textContent = 'Le fichier doit être au format .wav';
    return;
  }
  sendError.textContent = '';

  const formData = new FormData();
  formData.append('audio_file', audioFile);
  formData.append('secret_message', secretMessage);
  formData.append('receiver_id', otherUserId);

  sendBtn.disabled = true;
  sendBtn.textContent = 'Envoi (Audio)...';

  try {
    const response = await fetch('/api/stego/send', {
      method: 'POST',
      body: formData, // Pas de headers 'Content-Type', le navigateur le gère
    });
    const data = await response.json();
    if (data.success) {
      stegoMessageInput.value = '';
      stegoFileInput.value = '';
      stegoFileInfo.textContent = '';
      await loadConversation();
    } else {
      sendError.textContent = 'Erreur: ' + data.message;
    }
  } catch (error) {
    console.error('Error:', error);
    sendError.textContent = "Échec de l'envoi (stégano)";
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = 'Envoyer (Audio)';
  }
}

// --- FONCTIONS UTILITAIRES ---

function capitalizeFirst(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function escapeHtml(text) {
  if (text === null || text === undefined) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

async function manualRefresh() {
  await loadConversation();
}

// Init
updateKeyInputs();
loadConversation();
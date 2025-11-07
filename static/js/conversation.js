const messagesArea = document.getElementById('messages-area');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const algorithmSelect = document.getElementById('algorithm-select');
const keyInputsDiv = document.getElementById('key-inputs');
const refreshBtn = document.getElementById('refresh-btn');

let otherUsername = '';
let autoRefreshInterval = null;
const decryptTimers = {};
const decryptedMessages = new Set();

function updateKeyInputs() {
    const algorithm = algorithmSelect.value;
    let html = '';

    switch(algorithm) {
        case 'ceasar':
            html = `
                <label>Shift:</label>
                <input type="number" id="caesar-shift" value="3" min="1" max="25">
                <label>Direction:</label>
                <select id="caesar-direction">
                    <option value="droite">Droite →</option>
                    <option value="gauche">Gauche ←</option>
                </select>
            `;
            break;
        case 'playfair':
            html = `
                <label>Key:</label>
                <input type="text" id="playfair-key" value="MONARCHY" maxlength="25">
            `;
            break;
        case 'hill':
            html = `
                <label>Key:</label>
                <input type="text" id="hill-key" value="FRID" placeholder="Length must be 4, 9, 16...">
            `;
            break;
    }

    keyInputsDiv.innerHTML = html;
}

algorithmSelect.addEventListener('change', updateKeyInputs);

async function loadConversation() {
    try {
        const response = await fetch(`/api/messages/conversation/${otherUserId}`);
        const data = await response.json();

        if (data.success && data.messages) {
            displayMessages(data.messages);
            if (data.messages.length > 0) {
                const other = data.messages[0].sender_id === currentUserId
                    ? data.messages[0].receiver
                    : data.messages[0].sender;
                otherUsername = other.username;
                document.getElementById('conversation-title').textContent = `Conversation avec ${otherUsername}`;
            }
        } else {
            console.error('Failed to load conversation:', data.message);
            messagesArea.innerHTML = '<p class="no-messages">Erreur de chargement des messages</p>';
        }
    } catch (error) {
        console.error('Error loading conversation:', error);
        messagesArea.innerHTML = '<p class="no-messages">Erreur de connexion</p>';
    }
}

function displayMessages(messages) {
    if (messages.length === 0) {
        messagesArea.innerHTML = '<p class="no-messages">Aucun message pour le moment</p>';
        return;
    }

    const isScrolledToBottom = messagesArea.scrollHeight - messagesArea.clientHeight <= messagesArea.scrollTop + 1;

    messagesArea.innerHTML = '';
    messages.forEach(message => {
        const messageEl = createMessageElement(message);
        messagesArea.appendChild(messageEl);
    });

    if (isScrolledToBottom) {
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }
}

function createMessageElement(message) {
    const isSent = message.sender_id === currentUserId;
    const div = document.createElement('div');
    div.className = `message-bubble ${isSent ? 'sent' : 'received'}`;
    div.dataset.messageId = message.id;

    const sender = isSent ? 'Vous' : message.sender.username;
    const date = new Date(message.date_created).toLocaleString('fr-FR');

    const isDecrypted = decryptedMessages.has(message.id);
    const messageText = isDecrypted ? getDecryptedText(message) : escapeHtml(message.encrypted);
    const messageClass = isDecrypted ? '' : 'encrypted';

    div.innerHTML = `
        <div class="message-info">${sender} • ${date}</div>
        <div class="message-text ${messageClass}" 
             data-encrypted="${escapeHtml(message.encrypted)}" 
             data-algo="${message.algo_name}" 
             data-key='${escapeHtml(message.algorithm_key || '{}')}'>
            ${messageText}
        </div>
        <div class="message-meta">Algorithme: ${capitalizeFirst(message.algo_name)}</div>
        ${!isSent ? createDecryptButton(message.id, isDecrypted) : ''}
    `;

    return div;
}

function getDecryptedText(message) {
    return "🔓 Message déchiffré (recharger pour voir le texte chiffré)";
}

function createDecryptButton(messageId, isDecrypted) {
    if (isDecrypted) {
        return '<button class="decrypt-btn decrypted" disabled>✅ Déchiffré</button>';
    } else {
        return '<button class="decrypt-btn" onclick="decryptMessage(this)">🔓 Déchiffrer</button>';
    }
}

async function decryptMessage(button) {
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
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                encrypted_message: encrypted,
                algorithm: algorithm,
                key_params: keyParams
            })
        });

        const data = await response.json();

        if (data.success) {
            decryptedMessages.add(messageId);
            
            messageText.textContent = data.decrypted;
            messageText.classList.remove('encrypted');
            
            button.textContent = '✅ Déchiffré';
            button.disabled = true;
            button.classList.add('decrypted');

            decryptTimers[messageId] = setTimeout(() => {
                if (decryptedMessages.has(messageId)) {
                    messageText.textContent = encrypted;
                    messageText.classList.add('encrypted');
                    button.textContent = '🔓 Déchiffrer';
                    button.disabled = false;
                    button.classList.remove('decrypted');
                    decryptedMessages.delete(messageId);
                    delete decryptTimers[messageId];
                }
            }, 300000);

        } else {
            alert('Erreur de déchiffrement: ' + data.message);
            button.disabled = false;
            button.textContent = '🔓 Déchiffrer';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Échec du déchiffrement');
        button.disabled = false;
        button.textContent = '🔓 Déchiffrer';
    }
}

async function sendMessage() {
    const message = messageInput.value.trim();
    const algorithm = algorithmSelect.value;

    if (!message) {
        alert('Veuillez entrer un message');
        return;
    }

    const keyParams = getKeyParams(algorithm);

    sendBtn.disabled = true;
    sendBtn.textContent = 'Envoi...';

    try {
        const response = await fetch('/api/messages/send', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: message,
                algo_name: algorithm,
                receiver_id: otherUserId,
                key_params: keyParams
            })
        });

        const data = await response.json();

        if (data.success) {
            messageInput.value = '';
            await loadConversation();
        } else {
            alert('Erreur: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Échec de l\'envoi du message');
    } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = 'Envoyer';
    }
}

function getKeyParams(algorithm) {
    const params = {};

    switch(algorithm) {
        case 'ceasar':
            const shiftEl = document.getElementById('caesar-shift');
            const directionEl = document.getElementById('caesar-direction');
            params.shift = shiftEl ? parseInt(shiftEl.value) : 3;
            params.direction = directionEl ? directionEl.value : 'droite';
            break;
        case 'playfair':
            const keyEl = document.getElementById('playfair-key');
            params.key = keyEl ? keyEl.value : 'MONARCHY';
            break;
        case 'hill':
            const hillKeyEl = document.getElementById('hill-key');
            params.key = hillKeyEl ? hillKeyEl.value.trim() : 'FRID';
            break;
    }

    return params;
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function manualRefresh() {
    await loadConversation();
}

window.addEventListener('beforeunload', () => {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    Object.values(decryptTimers).forEach(timer => clearTimeout(timer));
});

sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

updateKeyInputs();
loadConversation();
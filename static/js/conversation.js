const messagesArea = document.getElementById('messages-area');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const algorithmSelect = document.getElementById('algorithm-select');
const keyInputsDiv = document.getElementById('key-inputs');

let otherUsername = '';

// Store timers for auto-hide functionality
const decryptTimers = {};

function updateKeyInputs() {
    const algorithm = algorithmSelect.value;
    let html = '';

    switch(algorithm) {
        case 'ceasar':
            html = `
                <label>Shift:</label>
                <input type="number" id="caesar-shift" value="3" min="1" max="25">
            `;
            break;
        case 'affine':
            html = `
                <label>a:</label>
                <input type="number" id="affine-a" value="5" min="1">
                <label>b:</label>
                <input type="number" id="affine-b" value="8" min="0">
            `;
            break;
        case 'playfair':
            html = `
                <label>Key:</label>
                <input type="text" id="playfair-key" value="MONARCHY" maxlength="25">
            `;
            break;
        case 'hill':
            html = `<p style="color: #666; font-size: 0.85rem;">Hill uses default 3x3 matrix</p>`;
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
        }
    } catch (error) {
        console.error('Error loading conversation:', error);
    }
}

function displayMessages(messages) {
    if (messages.length === 0) {
        messagesArea.innerHTML = '<p class="no-messages">Aucun message pour le moment</p>';
        return;
    }

    messagesArea.innerHTML = '';
    messages.forEach(message => {
        const messageEl = createMessageElement(message);
        messagesArea.appendChild(messageEl);
    });

    messagesArea.scrollTop = messagesArea.scrollHeight;
}

function createMessageElement(message) {
    const isSent = message.sender_id === currentUserId;
    const div = document.createElement('div');
    div.className = `message-bubble ${isSent ? 'sent' : 'received'}`;
    div.dataset.messageId = message.id;

    const sender = isSent ? 'You' : message.sender.username;
    const date = new Date(message.date_created).toLocaleString('fr-FR');

    div.innerHTML = `
        <div class="message-info">${sender} • ${date}</div>
        <div class="message-text encrypted" data-encrypted="${message.encrypted}" data-algo="${message.algo_name}" data-key='${message.algorithm_key || '{}'}'>${message.encrypted}</div>
        <div class="message-meta">Algorithm: ${capitalizeFirst(message.algo_name)}</div>
        ${!isSent ? '<button class="decrypt-btn" onclick="decryptMessage(this)">Decrypt</button>' : ''}
    `;

    return div;
}

async function decryptMessage(button) {
    const messageText = button.previousElementSibling.previousElementSibling;
    const encrypted = messageText.dataset.encrypted;
    const algorithm = messageText.dataset.algo;
    const keyParams = JSON.parse(messageText.dataset.key || '{}');
    const messageBubble = button.closest('.message-bubble');
    const messageId = messageBubble.dataset.messageId;

    // Clear any existing timer for this message
    if (decryptTimers[messageId]) {
        clearTimeout(decryptTimers[messageId]);
    }

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
            const originalEncrypted = messageText.textContent;
            messageText.textContent = data.decrypted;
            messageText.classList.remove('encrypted');
            button.style.display = 'none';

            // Set timer to hide decrypted message after 1 minute (60 seconds)
            decryptTimers[messageId] = setTimeout(() => {
                messageText.textContent = originalEncrypted;
                messageText.classList.add('encrypted');
                button.style.display = 'inline-block';
                delete decryptTimers[messageId];
            }, 60000); // 60000ms = 60 seconds = 1 minute
        } else {
            alert('Decryption error: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to decrypt message');
    }
}

async function sendMessage() {
    const message = messageInput.value.trim();
    const algorithm = algorithmSelect.value;

    if (!message) {
        alert('Please enter a message');
        return;
    }

    const keyParams = getKeyParams(algorithm);

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
            loadConversation();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to send message');
    }
}

function getKeyParams(algorithm) {
    const params = {};

    switch(algorithm) {
        case 'ceasar':
            params.shift = document.getElementById('caesar-shift')?.value || 3;
            break;
        case 'affine':
            params.a = document.getElementById('affine-a')?.value || 5;
            params.b = document.getElementById('affine-b')?.value || 8;
            break;
        case 'playfair':
            params.key = document.getElementById('playfair-key')?.value || 'MONARCHY';
            break;
    }

    return params;
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

loadConversation();
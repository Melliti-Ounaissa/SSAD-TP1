const audioFileInput = document.getElementById('audio-file');
const fileInfo = document.getElementById('file-info');
const secretMessageInput = document.getElementById('secret-message');
const recipientSelect = document.getElementById('stego-recipient-select');
const sendErrorMessage = document.getElementById('send-error-message');
const stegoMessagesList = document.getElementById('stego-messages-list');
const uploadArea = document.getElementById('upload-area');

let selectedFile = null;

// Load recipients
async function loadRecipients() {
    try {
        const response = await fetch('/api/users');
        const data = await response.json();

        if (data.success && data.users) {
            recipientSelect.innerHTML = '<option value="">Choisir un destinataire...</option>';
            data.users.forEach(user => {
                const option = document.createElement('option');
                option.value = user.id;
                option.textContent = user.username;
                recipientSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading recipients:', error);
    }
}

// Handle file selection
audioFileInput.addEventListener('change', (e) => {
    selectedFile = e.target.files[0];
    if (selectedFile) {
        if (selectedFile.type !== 'audio/wav' && !selectedFile.name.endsWith('.wav')) {
            showError('Seuls les fichiers WAV sont acceptés');
            selectedFile = null;
            fileInfo.textContent = '';
            return;
        }
        fileInfo.innerHTML = `<strong>Fichier sélectionné:</strong> ${selectedFile.name} (${(selectedFile.size / 1024).toFixed(2)} KB)`;
        showError('');
    }
});

// Drag and drop support
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#4a90e2';
    uploadArea.style.backgroundColor = '#f8f9fa';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = '#d0d0d0';
    uploadArea.style.backgroundColor = 'transparent';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#d0d0d0';
    uploadArea.style.backgroundColor = 'transparent';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        audioFileInput.files = files;
        audioFileInput.dispatchEvent(new Event('change'));
    }
});

// Send steganography message
async function sendStegoMessage() {
    const secretMessage = secretMessageInput.value.trim();
    const receiverId = recipientSelect.value;

    if (!selectedFile) {
        showError('Veuillez sélectionner un fichier audio WAV');
        return;
    }

    if (!secretMessage) {
        showError('Veuillez entrer un message secret');
        return;
    }

    if (!receiverId) {
        showError('Veuillez sélectionner un destinataire');
        return;
    }

    const formData = new FormData();
    formData.append('audio_file', selectedFile);
    formData.append('secret_message', secretMessage);
    formData.append('receiver_id', receiverId);

    try {
        showError('Envoi en cours...');
        const response = await fetch('/api/stego/send', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showError('Message envoyé avec succès!', 'success');
            secretMessageInput.value = '';
            selectedFile = null;
            fileInfo.textContent = '';
            audioFileInput.value = '';
            recipientSelect.value = '';
            loadStegoMessages();
            setTimeout(() => showError(''), 3000);
        } else {
            showError(data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Erreur lors de l\'envoi du message');
    }
}

// Load steganography messages
async function loadStegoMessages() {
    try {
        const response = await fetch('/api/stego/messages');
        const data = await response.json();

        if (data.success && data.messages) {
            displayStegoMessages(data.messages);
        }
    } catch (error) {
        console.error('Error loading messages:', error);
        stegoMessagesList.innerHTML = '<p class="no-messages">Erreur de chargement</p>';
    }
}

// Display steganography messages
function displayStegoMessages(messages) {
    if (messages.length === 0) {
        stegoMessagesList.innerHTML = '<p class="no-messages">Aucun message audio</p>';
        return;
    }

    const receivedMessages = messages.filter(msg => msg.receiver_id === userId);

    if (receivedMessages.length === 0) {
        stegoMessagesList.innerHTML = '<p class="no-messages">Aucun message audio reçu</p>';
        return;
    }

    stegoMessagesList.innerHTML = '';
    receivedMessages.forEach(message => {
        const card = createStegoMessageCard(message);
        stegoMessagesList.appendChild(card);
    });
}

// Create message card
function createStegoMessageCard(message) {
    const div = document.createElement('div');
    div.className = 'stego-message-card';
    
    const date = new Date(message.date_created).toLocaleString('fr-FR');
    const senderName = message.sender.username;
    const audioUrl = `/api/stego/audio/${message.audio_filename}`;

    div.innerHTML = `
        <div class="stego-message-header">
            <div>
                <div class="stego-message-from">De: ${senderName}</div>
                <div class="stego-message-date">${date}</div>
            </div>
            <button class="decrypt-audio-btn" onclick="decryptStegoMessage(${message.id}, this)">
                🔓 Déchiffrer le message
            </button>
        </div>
        <div>
            <strong>📁 Fichier audio:</strong> ${message.audio_filename}
        </div>
        <div class="audio-player">
            <strong>🎵 Écouter l'audio:</strong>
            <audio controls preload="metadata">
                <source src="${audioUrl}" type="audio/wav">
                Votre navigateur ne supporte pas la lecture audio.
            </audio>
            <div class="audio-info">💡 Cliquez sur lecture pour écouter l'audio complet</div>
        </div>
        <div class="decrypted-content" id="decrypted-${message.id}">
            <strong>🔓 Message caché:</strong>
            <p id="message-${message.id}"></p>
        </div>
    `;

    return div;
}

// Decrypt steganography message
async function decryptStegoMessage(messageId, button) {
    button.disabled = true;
    button.textContent = 'Déchiffrement...';

    try {
        const response = await fetch(`/api/stego/decrypt/${messageId}`);
        const data = await response.json();

        if (data.success) {
            const decryptedDiv = document.getElementById(`decrypted-${messageId}`);
            const messageP = document.getElementById(`message-${messageId}`);
            
            messageP.textContent = data.decrypted_message;
            decryptedDiv.classList.add('show');
            button.textContent = '✓ Déchiffré';
            button.style.backgroundColor = '#28a745';
            
            // Hide the decrypted message after 60 seconds (1 minute)
            setTimeout(() => {
                decryptedDiv.classList.remove('show');
                button.textContent = '🔓 Déchiffrer le message';
                button.style.backgroundColor = '#0d214f';
                button.disabled = false;
                messageP.textContent = '';
            }, 60000); // 60000ms = 60 seconds = 1 minute
        } else {
            alert('Erreur: ' + data.message);
            button.disabled = false;
            button.textContent = '🔓 Déchiffrer';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erreur lors du déchiffrement');
        button.disabled = false;
        button.textContent = '🔓 Déchiffrer';
    }
}

function showError(message, type = 'error') {
    sendErrorMessage.textContent = message;
    if (type === 'success') {
        sendErrorMessage.style.color = '#28a745';
    } else {
        sendErrorMessage.style.color = '#dc3545';
    }
}

// Initialize
loadRecipients();
loadStegoMessages();
setInterval(loadStegoMessages, 5000);
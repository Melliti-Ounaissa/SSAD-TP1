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

// Create visualization modal
function createVisualizationModal(analysis) {
    const modal = document.createElement('div');
    modal.className = 'visualization-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>🔬 Analyse de la Stéganographie</h2>
                <button class="modal-close" onclick="closeVisualizationModal()">&times;</button>
            </div>
            <div class="modal-body">
                ${createAnalysisHTML(analysis)}
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close on outside click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeVisualizationModal();
        }
    });
}

function createAnalysisHTML(analysis) {
    const original = analysis.original;
    const modified = analysis.modified;
    const lsb = analysis.lsb_comparison;
    
    let html = `
        <div class="analysis-section">
            <h3>📊 Informations Audio</h3>
            <div class="comparison-grid">
                <div class="comparison-card">
                    <h4>Audio Original</h4>
                    <table class="info-table">
                        <tr><td>Canaux:</td><td>${original.channels}</td></tr>
                        <tr><td>Fréquence:</td><td>${original.framerate} Hz</td></tr>
                        <tr><td>Durée:</td><td>${original.duration.toFixed(2)}s</td></tr>
                        <tr><td>Échantillons:</td><td>${original.n_frames.toLocaleString()}</td></tr>
                        <tr><td>Capacité:</td><td>${original.capacity_chars} caractères</td></tr>
                    </table>
                </div>
                
                <div class="comparison-card">
                    <h4>Audio Modifié</h4>
                    <table class="info-table">
                        <tr><td>Canaux:</td><td>${modified.channels}</td></tr>
                        <tr><td>Fréquence:</td><td>${modified.framerate} Hz</td></tr>
                        <tr><td>Durée:</td><td>${modified.duration.toFixed(2)}s</td></tr>
                        <tr><td>Échantillons:</td><td>${modified.n_frames.toLocaleString()}</td></tr>
                        <tr><td>Capacité:</td><td>${modified.capacity_chars} caractères</td></tr>
                    </table>
                </div>
            </div>
        </div>
        
        <div class="analysis-section">
            <h3>💬 Message Caché</h3>
            <div class="message-info">
                <p><strong>Texte:</strong> "${analysis.message_hidden}"</p>
                <p><strong>Longueur:</strong> ${analysis.message_length} caractères (${analysis.binary_length} bits)</p>
                <p><strong>Utilisation:</strong> ${((analysis.binary_length / original.capacity_bits) * 100).toFixed(2)}% de la capacité</p>
            </div>
            <div class="binary-preview">
                <strong>Représentation binaire:</strong>
                <code>${lsb.binary_message}</code>
            </div>
        </div>
        
        <div class="analysis-section">
            <h3>🔍 Modifications LSB (Échantillons: 1-${lsb.samples.length})</h3>
            <div class="stats-summary">
                <div class="stat-box">
                    <div class="stat-value">${lsb.total_changes}</div>
                    <div class="stat-label">Modifications</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">${lsb.change_percentage.toFixed(1)}%</div>
                    <div class="stat-label">Taux de changement</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">±1</div>
                    <div class="stat-label">Différence maximale</div>
                </div>
            </div>
            
            <div class="lsb-table-container">
                <table class="lsb-table">
                    <thead>
                        <tr>
                            <th>Index</th>
                            <th>Original</th>
                            <th>Modifié</th>
                            <th>LSB Avant</th>
                            <th>LSB Après</th>
                            <th>Bit Message</th>
                            <th>Changé?</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${lsb.samples.map(sample => `
                            <tr class="${sample.changed ? 'changed-row' : ''}">
                                <td>${sample.index}</td>
                                <td>${sample.original}</td>
                                <td>${sample.modified}</td>
                                <td><code>${sample.lsb_before}</code></td>
                                <td><code>${sample.lsb_after}</code></td>
                                <td><code>${sample.message_bit}</code></td>
                                <td>${sample.changed ? '✓ OUI' : '✗ NON'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            
            <div class="explanation">
                <p><strong>💡 Explication:</strong></p>
                <p>La stéganographie LSB modifie le bit de poids faible (LSB) de chaque échantillon audio pour cacher un message. 
                Ces modifications sont imperceptibles à l'oreille humaine car elles représentent une différence de ±1 sur des valeurs 
                pouvant aller jusqu'à ±32768.</p>
            </div>
        </div>
    `;
    
    return html;
}

function closeVisualizationModal() {
    const modal = document.querySelector('.visualization-modal');
    if (modal) {
        modal.remove();
    }
}

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
        showError('Envoi en cours...', 'info');
        const response = await fetch('/api/stego/send', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showError('Message envoyé avec succès!', 'success');
            
            // Show visualization if analysis data is available
            if (data.analysis) {
                setTimeout(() => {
                    createVisualizationModal(data.analysis);
                }, 500);
            }
            
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
            
            // Hide the decrypted message after 60 seconds
            setTimeout(() => {
                decryptedDiv.classList.remove('show');
                button.textContent = '🔓 Déchiffrer le message';
                button.style.backgroundColor = '#0d214f';
                button.disabled = false;
                messageP.textContent = '';
            }, 60000);
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
    } else if (type === 'info') {
        sendErrorMessage.style.color = '#0d214f';
    } else {
        sendErrorMessage.style.color = '#dc3545';
    }
}

// Initialize
loadRecipients();
loadStegoMessages();
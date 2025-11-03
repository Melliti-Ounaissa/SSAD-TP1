const messageInput = document.getElementById('message-input');
const encryptedDisplay = document.getElementById('encrypted-display');
const decryptedDisplay = document.getElementById('decrypted-display');
const recipientSelect = document.getElementById('recipient-select');
const errorMessage = document.getElementById('error-message');
const keyInputsDiv = document.getElementById('key-inputs');

// Load recipients when page loads
async function loadRecipients() {
    try {
        const response = await fetch(`/api/users`);
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
        showError('Error loading recipients');
    }
}

// Create key input fields based on algorithm
function createKeyInputs() {
    let html = '';
    
    switch(algorithm) {
        case 'ceasar':
            html = `
                <div class="key-input-group">
                    <label>Shift (clé):</label>
                    <input type="number" id="caesar-shift" value="3" min="1" max="25">
                </div>
                <div class="key-input-group">
                    <label>Direction:</label>
                    <select id="caesar-direction">
                        <option value="droite">Droite →</option>
                        <option value="gauche">Gauche ←</option>
                    </select>
                </div>
            `;
            break;
        case 'affine':
            html = `
                <div class="key-input-group">
                    <label>a (doit être copremier avec 26):</label>
                    <input type="number" id="affine-a" value="5" min="1">
                </div>
                <div class="key-input-group">
                    <label>b:</label>
                    <input type="number" id="affine-b" value="8" min="0">
                </div>
            `;
            break;
        case 'playfair':
            html = `
                <div class="key-input-group">
                    <label>Key (mot clé):</label>
                    <input type="text" id="playfair-key" value="MONARCHY" maxlength="25">
                </div>
            `;
            break;
        case 'hill':
            html = `
                <div class="key-input-group">
                    <label>Key (longueur 4, 9, 16...):</label>
                    <input type="text" id="hill-key" value="FRID">
                </div>
                <div class="key-input-group">
                    <p style="color: #666; font-size: 0.9rem;">Clé pour matrice $n \\times n$. Doit être invertible mod 27. (Ex: "FRID" pour 2x2)</p>
                </div>
            `;
            break;
    }
    
    if (keyInputsDiv) {
        keyInputsDiv.innerHTML = html;
        
        // Add event listeners for real-time encryption
        if (algorithm === 'ceasar') {
            const shiftInput = document.getElementById('caesar-shift');
            const directionSelect = document.getElementById('caesar-direction');
            if (shiftInput) shiftInput.addEventListener('input', encryptMessage);
            if (directionSelect) directionSelect.addEventListener('change', encryptMessage);
        }
    }
}

// Get key parameters based on algorithm
function getKeyParams() {
    const params = {};
    
    switch(algorithm) {
        case 'ceasar':
            const shiftInput = document.getElementById('caesar-shift');
            const directionSelect = document.getElementById('caesar-direction');
            params.shift = shiftInput ? parseInt(shiftInput.value) : 3;
            params.direction = directionSelect ? directionSelect.value : 'droite';
            break;
        case 'affine':
            const aInput = document.getElementById('affine-a');
            const bInput = document.getElementById('affine-b');
            params.a = aInput ? parseInt(aInput.value) : 5;
            params.b = bInput ? parseInt(bInput.value) : 8;
            break;
        case 'playfair':
            const playfairKeyInput = document.getElementById('playfair-key');
            params.key = playfairKeyInput ? playfairKeyInput.value : 'MONARCHY';
            break;
        case 'hill':
            const keyInput = document.getElementById('hill-key');
            params.key = keyInput ? keyInput.value.trim() : 'FRID';
            break;
    }
    
    return params;
}

// Encrypt message in real-time
async function encryptMessage() {
    const message = messageInput.value.trim();
    
    if (!message) {
        encryptedDisplay.textContent = 'Le message chiffré apparaîtra ici...';
        return;
    }
    
    const keyParams = getKeyParams();
    
    try {
        const response = await fetch('/api/crypto/encrypt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                algorithm: algorithm,
                key_params: keyParams
            }),
        });

        const data = await response.json();

        if (data.success) {
            encryptedDisplay.textContent = data.encrypted;
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Encryption error');
        console.error('Error:', error);
    }
}

// Send encrypted message
async function sendMessage() {
    const message = messageInput.value.trim();
    const receiverId = recipientSelect.value;

    if (!message) {
        showError('Veuillez entrer un message');
        return;
    }

    if (!receiverId) {
        showError('Veuillez sélectionner un destinataire');
        return;
    }

    const keyParams = getKeyParams();

    try {
        const response = await fetch('/api/messages/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                algo_name: algorithm,
                receiver_id: parseInt(receiverId),
                key_params: keyParams
            }),
        });

        const data = await response.json();

        if (data.success) {
            encryptedDisplay.textContent = data.data.encrypted;
            decryptedDisplay.textContent = message;
            messageInput.value = '';
            showError('');
            alert('Message envoyé avec succès!');
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Erreur de connexion. Veuillez réessayer.');
        console.error('Error:', error);
    }
}

function showError(message) {
    errorMessage.textContent = message;
    if (message) {
        setTimeout(() => {
            errorMessage.textContent = '';
        }, 5000);
    }
}

// Event listeners
messageInput.addEventListener('input', encryptMessage);

// Initialize
createKeyInputs();
loadRecipients();
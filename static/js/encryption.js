const messageInput = document.getElementById('message-input');
const encryptedDisplay = document.getElementById('encrypted-display');
const decryptedDisplay = document.getElementById('decrypted-display');
const recipientSelect = document.getElementById('recipient-select');
const errorMessage = document.getElementById('error-message');

async function loadRecipients() {
    try {
        const response = await fetch(`/api/users/${userId}/others`);
        const data = await response.json();

        if (data.success && data.users) {
            data.users.forEach(user => {
                const option = document.createElement('option');
                option.value = user.id;
                option.textContent = user.email;
                recipientSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading recipients:', error);
    }
}

async function sendMessage() {
    const message = messageInput.value.trim();
    const receiverId = recipientSelect.value;

    if (!message) {
        showError('Please enter a message');
        return;
    }

    if (!receiverId) {
        showError('Please select a recipient');
        return;
    }

    try {
        const response = await fetch('/api/messages/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sender_id: userId,
                receiver_id: parseInt(receiverId),
                content: message,
                algo_name: algorithm
            }),
        });

        const data = await response.json();

        if (data.success) {
            encryptedDisplay.textContent = data.data.encrypted;
            decryptedDisplay.textContent = data.data.content;
            messageInput.value = '';
            showError('');
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Connection error. Please try again.');
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

loadRecipients();

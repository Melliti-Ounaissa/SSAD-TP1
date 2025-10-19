const sentMessagesList = document.getElementById('sent-messages');
const receivedMessagesList = document.getElementById('received-messages');

// Helper to capitalize the first letter of a string
function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

async function loadMessages() {
    try {
        // userId is defined in messages.html script block
        const [sentResponse, receivedResponse] = await Promise.all([
            fetch(`/api/messages/sent/${userId}`),
            fetch(`/api/messages/received/${userId}`)
        ]);

        const sentData = await sentResponse.json();
        const receivedData = await receivedResponse.json();

        displaySentMessages(sentData.messages || []);
        displayReceivedMessages(receivedData.messages || []);
    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

function displaySentMessages(messages) {
    if (messages.length === 0) {
        sentMessagesList.innerHTML = '<p class="no-messages">Aucun message envoyé</p>';
        return;
    }

    sentMessagesList.innerHTML = '';
    messages.forEach(message => {
        const card = createMessageCard(message, true);
        sentMessagesList.appendChild(card);
    });
}

function displayReceivedMessages(messages) {
    if (messages.length === 0) {
        receivedMessagesList.innerHTML = '<p class="no-messages">Aucun message reçu</p>';
        return;
    }

    receivedMessagesList.innerHTML = '';
    messages.forEach(message => {
        const card = createMessageCard(message, false);
        receivedMessagesList.appendChild(card);
    });
}

function createMessageCard(message, isSent) {
    const card = document.createElement('div');
    card.className = 'message-card';

    // CHANGED 'email' to 'username' in the message object access
    const recipientUsername = isSent
        ? (message.users?.username || 'Unknown') // For sent messages, this is the recipient's username
        : (message.users?.username || 'Unknown'); // For received messages, this is the sender's username

    const headerText = isSent ? `À: ${recipientUsername}` : `De: ${recipientUsername}`; 
    const date = new Date(message.date_created).toLocaleString('fr-FR');
    
    // message.content is now the decrypted message (added by server)
    // message.encrypted is the original crypted message (from DB)

    card.innerHTML = `
        <div class="message-header">${headerText}</div>
        <div class="message-meta">Algorithme: ${capitalizeFirst(message.algo_name)}</div>
        <div class="message-meta">Date: ${date}</div>
        <div class="message-content">Message: ${message.content}</div> <!-- Display Decrypted Content -->
        <div class="message-encrypted">Chiffré: ${message.encrypted}</div> <!-- Display Encrypted Content -->
    `;

    return card;
}

// Initial load
document.addEventListener('DOMContentLoaded', loadMessages);
// This is where you would place subscription logic for real-time updates if needed.


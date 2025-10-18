const sentMessagesList = document.getElementById('sent-messages');
const receivedMessagesList = document.getElementById('received-messages');

async function loadMessages() {
    try {
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

    const recipientEmail = isSent
        ? (message.users?.email || 'Unknown')
        : (message.users?.email || 'Unknown');

    const headerText = isSent ? `À: ${recipientEmail}` : `De: ${recipientEmail}`;
    const date = new Date(message.date_created).toLocaleString('fr-FR');

    card.innerHTML = `
        <div class="message-header">${headerText}</div>
        <div class="message-meta">Algorithme: ${capitalizeFirst(message.algo_name)}</div>
        <div class="message-meta">Date: ${date}</div>
        <div class="message-content">Message: ${message.content}</div>
        <div class="message-encrypted">Chiffré: ${message.encrypted}</div>
    `;

    return card;
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

loadMessages();
setInterval(loadMessages, 3000);

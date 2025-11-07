const conversationList = document.getElementById('conversation-list');

async function loadConversations() {
    try {
        const response = await fetch('/api/messages/all');
        const data = await response.json();

        if (data.success && data.messages) {
            displayConversations(data.messages);
        }
    } catch (error) {
        console.error('Error loading conversations:', error);
    }
}

function displayConversations(messages) {
    const conversations = {};

    messages.forEach(message => {
        const otherUserId = message.sender_id === userId ? message.receiver_id : message.sender_id;
        const otherUsername = message.sender_id === userId
            ? message.receiver.username
            : message.sender.username;

        if (!conversations[otherUserId]) {
            conversations[otherUserId] = {
                userId: otherUserId,
                username: otherUsername,
                lastMessage: message,
                messages: []
            };
        }

        conversations[otherUserId].messages.push(message);
        if (new Date(message.date_created) > new Date(conversations[otherUserId].lastMessage.date_created)) {
            conversations[otherUserId].lastMessage = message;
        }
    });

    if (Object.keys(conversations).length === 0) {
        conversationList.innerHTML = '<p class="no-messages">Aucune conversation</p>';
        return;
    }

    conversationList.innerHTML = '';
    Object.values(conversations).forEach(conv => {
        const item = createConversationItem(conv);
        conversationList.appendChild(item);
    });
}

function createConversationItem(conversation) {
    const div = document.createElement('div');
    div.className = 'conversation-item';
    div.onclick = () => window.location.href = `/conversation/${conversation.userId}`;

    const date = new Date(conversation.lastMessage.date_created).toLocaleString('fr-FR');
    const preview = conversation.lastMessage.encrypted.substring(0, 50) + '...';
    const direction = conversation.lastMessage.sender_id === userId ? 'Sent' : 'Received';

    div.innerHTML = `
        <div class="conversation-header-info">
            <span class="conversation-username">${conversation.username}</span>
            <span class="conversation-time">${date}</span>
        </div>
        <div class="conversation-preview">
            <strong>${direction}:</strong>
            <span class="encrypted">${preview}</span>
        </div>
    `;

    return div;
}

loadConversations();

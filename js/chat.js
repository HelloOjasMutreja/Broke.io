// Live Chat System

let chatState = {
    messages: [],
    isCollapsed: false
};

// Initialize Chat
function initChat() {
    setupChatListeners();
}

// Setup Chat Event Listeners
function setupChatListeners() {
    const sendBtn = document.getElementById('send-chat');
    const chatInput = document.getElementById('chat-input');
    const toggleBtn = document.getElementById('toggle-chat');
    
    if (sendBtn) {
        sendBtn.addEventListener('click', sendChatMessage);
    }
    
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    }
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleChat);
    }
}

// Send Chat Message
function sendChatMessage() {
    const chatInput = document.getElementById('chat-input');
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    const currentPlayer = gameState.players[gameState.currentPlayerIndex];
    const timestamp = new Date().toLocaleTimeString();
    
    addChatMessage(`[${timestamp}] ${currentPlayer.name}: ${message}`, 'player');
    
    chatInput.value = '';
    
    // Simulate responses in solo mode
    if (gameState.gameMode === 'solo' && Math.random() > 0.5) {
        setTimeout(() => {
            const responses = [
                "Good move!",
                "Nice property!",
                "Watch out for bankruptcy!",
                "Let's trade!",
                "That's a great deal!",
                "Oh no!",
                "Congrats!",
                "I'm coming for you!"
            ];
            const randomBot = gameState.players.find(p => !p.isHuman);
            if (randomBot) {
                const randomResponse = responses[Math.floor(Math.random() * responses.length)];
                addChatMessage(`[${new Date().toLocaleTimeString()}] ${randomBot.name}: ${randomResponse}`, 'player');
            }
        }, 1000 + Math.random() * 2000);
    }
}

// Toggle Chat Window
function toggleChat() {
    const chatMessages = document.getElementById('chat-messages');
    const chatInputArea = document.getElementById('chat-input-area');
    const toggleBtn = document.getElementById('toggle-chat');
    
    chatState.isCollapsed = !chatState.isCollapsed;
    
    if (chatState.isCollapsed) {
        chatMessages.style.display = 'none';
        chatInputArea.style.display = 'none';
        toggleBtn.textContent = '+';
    } else {
        chatMessages.style.display = 'block';
        chatInputArea.style.display = 'flex';
        toggleBtn.textContent = '−';
    }
}

// Add System Notifications
function addSystemNotification(message) {
    addChatMessage(message, 'system');
}

// Add Game Event to Chat
function addGameEvent(event, player, details) {
    let message = '';
    
    switch(event) {
        case 'property_bought':
            message = `${player.name} bought ${details.property} for $${details.price}!`;
            break;
        case 'rent_paid':
            message = `${player.name} paid $${details.amount} rent to ${details.owner}`;
            break;
        case 'passed_go':
            message = `${player.name} passed GO and collected $200!`;
            break;
        case 'bankrupt':
            message = `${player.name} went bankrupt!`;
            break;
        case 'jail':
            message = `${player.name} is in jail!`;
            break;
        case 'powerup_used':
            message = `${player.name} used ${details.powerup}!`;
            break;
        default:
            message = `${player.name}: ${event}`;
    }
    
    addChatMessage(message, 'game');
}

// Filter Chat Messages
function filterChatMessages(filterType) {
    const allMessages = document.querySelectorAll('.chat-message');
    
    allMessages.forEach(msg => {
        if (filterType === 'all') {
            msg.style.display = 'block';
        } else if (msg.classList.contains(filterType)) {
            msg.style.display = 'block';
        } else {
            msg.style.display = 'none';
        }
    });
}

// Clear Chat
function clearChat() {
    const messagesDiv = document.getElementById('chat-messages');
    messagesDiv.innerHTML = '<div class="chat-message system">Chat cleared.</div>';
    chatState.messages = [];
}

// Initialize chat on page load
document.addEventListener('DOMContentLoaded', initChat);

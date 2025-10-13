// Game State Management
const gameState = {
    players: [],
    currentPlayerIndex: 0,
    properties: [],
    gameMode: 'solo',
    isGameActive: false,
    turnNumber: 1,
    level: 1,
    experience: 0,
    theme: 'classic'
};

// Player Class
class Player {
    constructor(name, token, isHuman = true) {
        this.name = name;
        this.token = token;
        this.money = 1500;
        this.position = 0;
        this.properties = [];
        this.isHuman = isHuman;
        this.inJail = false;
        this.powerups = [];
    }

    move(spaces) {
        this.position = (this.position + spaces) % 40;
        if (this.position < spaces) {
            // Passed GO
            this.addMoney(200);
            addChatMessage(`${this.name} passed GO and collected $200!`, 'system');
        }
        updatePlayerToken(this);
    }

    addMoney(amount) {
        this.money += amount;
        updatePlayerDisplay();
    }

    removeMoney(amount) {
        this.money -= amount;
        updatePlayerDisplay();
        if (this.money < 0) {
            handleBankruptcy(this);
        }
    }

    buyProperty(property) {
        if (this.money >= property.price) {
            this.removeMoney(property.price);
            this.properties.push(property);
            property.owner = this;
            addChatMessage(`${this.name} bought ${property.name} for $${property.price}!`, 'game');
            updatePropertiesDisplay();
            addExperience(10);
        }
    }
}

// Property Class
class Property {
    constructor(name, position, price, rent, color) {
        this.name = name;
        this.position = position;
        this.price = price;
        this.rent = rent;
        this.color = color;
        this.owner = null;
        this.houses = 0;
        this.hotel = false;
    }
}

// Initialize Game
function initGame() {
    console.log('Initializing Broke.io...');
    
    // Create initial player
    const player1 = new Player('You', '🚗', true);
    gameState.players.push(player1);
    
    // Initialize properties
    initProperties();
    
    // Setup event listeners
    setupEventListeners();
    
    // Update displays
    updatePlayerDisplay();
    updatePropertiesDisplay();
    
    console.log('Game initialized!');
}

// Initialize Properties
function initProperties() {
    const propertyData = [
        { name: 'Mediterranean Avenue', position: 1, price: 60, rent: 2, color: 'brown' },
        { name: 'Baltic Avenue', position: 3, price: 60, rent: 4, color: 'brown' },
        { name: 'Oriental Avenue', position: 6, price: 100, rent: 6, color: 'light-blue' },
        { name: 'Vermont Avenue', position: 8, price: 100, rent: 6, color: 'light-blue' },
        { name: 'Connecticut Avenue', position: 9, price: 120, rent: 8, color: 'light-blue' },
        { name: 'St. Charles Place', position: 11, price: 140, rent: 10, color: 'pink' },
        { name: 'States Avenue', position: 13, price: 140, rent: 10, color: 'pink' },
        { name: 'Virginia Avenue', position: 14, price: 160, rent: 12, color: 'pink' },
        { name: 'St. James Place', position: 16, price: 180, rent: 14, color: 'orange' },
        { name: 'Tennessee Avenue', position: 18, price: 180, rent: 14, color: 'orange' },
        { name: 'New York Avenue', position: 19, price: 200, rent: 16, color: 'orange' },
        { name: 'Kentucky Avenue', position: 21, price: 220, rent: 18, color: 'red' },
        { name: 'Indiana Avenue', position: 23, price: 220, rent: 18, color: 'red' },
        { name: 'Illinois Avenue', position: 24, price: 240, rent: 20, color: 'red' },
        { name: 'Atlantic Avenue', position: 26, price: 260, rent: 22, color: 'yellow' },
        { name: 'Ventnor Avenue', position: 27, price: 260, rent: 22, color: 'yellow' },
        { name: 'Marvin Gardens', position: 29, price: 280, rent: 24, color: 'yellow' },
        { name: 'Pacific Avenue', position: 31, price: 300, rent: 26, color: 'green' },
        { name: 'North Carolina Avenue', position: 32, price: 300, rent: 26, color: 'green' },
        { name: 'Pennsylvania Avenue', position: 34, price: 320, rent: 28, color: 'green' },
        { name: 'Park Place', position: 37, price: 350, rent: 35, color: 'dark-blue' },
        { name: 'Boardwalk', position: 39, price: 400, rent: 50, color: 'dark-blue' }
    ];

    propertyData.forEach(data => {
        gameState.properties.push(new Property(data.name, data.position, data.price, data.rent, data.color));
    });
}

// Setup Event Listeners
function setupEventListeners() {
    // Roll Dice Button
    document.getElementById('roll-dice-btn').addEventListener('click', rollDice);
    
    // Game Mode Buttons
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const mode = e.target.dataset.mode;
            changeGameMode(mode);
        });
    });
    
    // Property Spaces
    document.querySelectorAll('.space.property').forEach(space => {
        space.addEventListener('click', (e) => {
            const position = parseInt(e.currentTarget.dataset.position);
            showPropertyModal(position);
        });
    });
    
    // Modal Close Buttons
    document.querySelectorAll('.close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.target.closest('.modal').style.display = 'none';
        });
    });
    
    // Buy Property Button
    document.getElementById('buy-property-btn').addEventListener('click', buyProperty);
    
    // Auction Button
    document.getElementById('auction-property-btn').addEventListener('click', startAuction);
    
    // Theme Selector
    document.getElementById('theme-select').addEventListener('change', (e) => {
        changeTheme(e.target.value);
    });
    
    // Token Options
    document.querySelectorAll('.token-option').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const token = e.target.dataset.token;
            changePlayerToken(token);
            document.getElementById('token-modal').style.display = 'none';
        });
    });
}

// Roll Dice Function
function rollDice() {
    if (!gameState.isGameActive) {
        gameState.isGameActive = true;
    }

    const dice1 = Math.floor(Math.random() * 6) + 1;
    const dice2 = Math.floor(Math.random() * 6) + 1;
    const total = dice1 + dice2;

    // Animate dice
    const dice1Element = document.getElementById('dice1');
    const dice2Element = document.getElementById('dice2');
    
    dice1Element.classList.add('rolling');
    dice2Element.classList.add('rolling');
    
    setTimeout(() => {
        dice1Element.querySelector('.dice-face').textContent = getDiceFace(dice1);
        dice2Element.querySelector('.dice-face').textContent = getDiceFace(dice2);
        dice1Element.classList.remove('rolling');
        dice2Element.classList.remove('rolling');
        
        // Move player
        const currentPlayer = gameState.players[gameState.currentPlayerIndex];
        currentPlayer.move(total);
        
        addChatMessage(`${currentPlayer.name} rolled ${dice1} + ${dice2} = ${total}`, 'game');
        
        // Handle landing on space
        handleLanding(currentPlayer);
        
        // Next turn
        setTimeout(() => nextTurn(), 1000);
    }, 500);
}

// Get Dice Face Character
function getDiceFace(number) {
    const faces = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];
    return faces[number - 1];
}

// Handle Landing on Space
function handleLanding(player) {
    const property = gameState.properties.find(p => p.position === player.position);
    
    if (property) {
        if (!property.owner) {
            // Show option to buy
            showPropertyModal(player.position);
        } else if (property.owner !== player) {
            // Pay rent
            const rent = property.rent;
            player.removeMoney(rent);
            property.owner.addMoney(rent);
            addChatMessage(`${player.name} paid $${rent} rent to ${property.owner.name}`, 'game');
        }
    }
    
    // Special spaces handling
    const spaceElement = document.querySelector(`[data-position="${player.position}"]`);
    const spaceType = spaceElement?.dataset.type;
    
    if (spaceType === 'go') {
        player.addMoney(200);
        addChatMessage(`${player.name} landed on GO! Collect $200`, 'system');
    } else if (spaceType === 'tax') {
        const taxAmount = player.position === 4 ? 200 : 100;
        player.removeMoney(taxAmount);
        addChatMessage(`${player.name} paid $${taxAmount} in taxes`, 'system');
    } else if (spaceType === 'go-to-jail') {
        player.position = 10;
        player.inJail = true;
        addChatMessage(`${player.name} went to jail!`, 'system');
        updatePlayerToken(player);
    }
    
    addExperience(5);
}

// Show Property Modal
function showPropertyModal(position) {
    const property = gameState.properties.find(p => p.position === position);
    if (!property) return;
    
    const modal = document.getElementById('property-modal');
    document.getElementById('property-title').textContent = property.name;
    document.getElementById('modal-price').textContent = `$${property.price}`;
    document.getElementById('modal-rent').textContent = `$${property.rent}`;
    document.getElementById('modal-owner').textContent = property.owner ? property.owner.name : 'None';
    
    // Show/hide buy button based on ownership
    const buyBtn = document.getElementById('buy-property-btn');
    const auctionBtn = document.getElementById('auction-property-btn');
    
    if (property.owner) {
        buyBtn.style.display = 'none';
        auctionBtn.style.display = 'none';
    } else {
        buyBtn.style.display = 'block';
        auctionBtn.style.display = 'block';
    }
    
    modal.style.display = 'block';
    modal.dataset.propertyPosition = position;
}

// Buy Property
function buyProperty() {
    const modal = document.getElementById('property-modal');
    const position = parseInt(modal.dataset.propertyPosition);
    const property = gameState.properties.find(p => p.position === position);
    const currentPlayer = gameState.players[gameState.currentPlayerIndex];
    
    if (property && !property.owner && currentPlayer.money >= property.price) {
        currentPlayer.buyProperty(property);
        modal.style.display = 'none';
    } else if (currentPlayer.money < property.price) {
        addChatMessage("Not enough money to buy this property!", 'system');
    }
}

// Update Player Display
function updatePlayerDisplay() {
    const currentPlayer = gameState.players[gameState.currentPlayerIndex];
    document.getElementById('player-name').textContent = currentPlayer.name;
    document.getElementById('player-money').textContent = `$${currentPlayer.money}`;
    document.getElementById('player-level').textContent = `Level ${gameState.level}`;
    
    // Update player list in side panel
    const playerList = document.querySelector('.player-list');
    playerList.innerHTML = gameState.players.map((player, index) => `
        <div class="player-item ${index === gameState.currentPlayerIndex ? 'active' : ''}">
            <span class="player-token" data-token="${player.token}">${player.token}</span>
            <span class="player-info">
                <span class="player-name">${player.name}</span>
                <span class="player-cash">$${player.money}</span>
            </span>
        </div>
    `).join('');
}

// Update Player Token Position
function updatePlayerToken(player) {
    // Remove previous token positions
    document.querySelectorAll('.player-marker').forEach(marker => {
        if (marker.textContent === player.token) {
            marker.remove();
        }
    });
    
    // Add token to new position
    const spaceElement = document.querySelector(`[data-position="${player.position}"]`);
    if (spaceElement) {
        const marker = document.createElement('div');
        marker.className = 'player-marker';
        marker.textContent = player.token;
        marker.style.cssText = 'position: absolute; top: 5px; right: 5px; font-size: 1.5em; z-index: 100; animation: tokenBounce 1s ease-in-out infinite;';
        spaceElement.style.position = 'relative';
        spaceElement.appendChild(marker);
    }
}

// Update Properties Display
function updatePropertiesDisplay() {
    const currentPlayer = gameState.players[gameState.currentPlayerIndex];
    const propertyList = document.getElementById('property-list');
    
    if (currentPlayer.properties.length === 0) {
        propertyList.innerHTML = '<p class="empty-message">No properties yet</p>';
    } else {
        propertyList.innerHTML = currentPlayer.properties.map(prop => `
            <div class="property-card">
                <strong>${prop.name}</strong><br>
                <span style="color: #2ecc71;">$${prop.price}</span> | Rent: $${prop.rent}
            </div>
        `).join('');
    }
}

// Next Turn
function nextTurn() {
    gameState.currentPlayerIndex = (gameState.currentPlayerIndex + 1) % gameState.players.length;
    gameState.turnNumber++;
    updatePlayerDisplay();
    
    const currentPlayer = gameState.players[gameState.currentPlayerIndex];
    document.getElementById('current-turn').textContent = `${currentPlayer.name}'s Turn`;
    
    // AI players
    if (!currentPlayer.isHuman) {
        setTimeout(() => rollDice(), 1500);
    }
}

// Change Game Mode
function changeGameMode(mode) {
    gameState.gameMode = mode;
    addChatMessage(`Game mode changed to ${mode}`, 'system');
    
    // Highlight active button
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.style.opacity = btn.dataset.mode === mode ? '1' : '0.6';
    });
    
    if (mode === 'solo') {
        // Add AI players for solo mode
        if (gameState.players.length === 1) {
            gameState.players.push(new Player('AI Bot 1', '🚢', false));
            gameState.players.push(new Player('AI Bot 2', '🎩', false));
            updatePlayerDisplay();
        }
    }
}

// Change Theme
function changeTheme(theme) {
    gameState.theme = theme;
    document.body.className = `theme-${theme}`;
    addChatMessage(`Theme changed to ${theme}`, 'system');
}

// Change Player Token
function changePlayerToken(token) {
    const currentPlayer = gameState.players[0]; // Always change player 1's token
    currentPlayer.token = token;
    updatePlayerDisplay();
    updatePlayerToken(currentPlayer);
    addChatMessage(`Token changed to ${token}`, 'system');
}

// Handle Bankruptcy
function handleBankruptcy(player) {
    addChatMessage(`${player.name} is bankrupt!`, 'system');
    // Transfer properties to bank
    player.properties.forEach(prop => {
        prop.owner = null;
    });
    player.properties = [];
}

// Add Experience and Level Up
function addExperience(amount) {
    gameState.experience += amount;
    const expNeeded = gameState.level * 100;
    
    if (gameState.experience >= expNeeded) {
        gameState.level++;
        gameState.experience = 0;
        addChatMessage(`🎉 Level Up! You are now level ${gameState.level}!`, 'system');
        updatePlayerDisplay();
    }
}

// Chat Message Helper
function addChatMessage(message, type = 'game') {
    const messagesDiv = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${type}`;
    messageElement.textContent = message;
    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initGame);

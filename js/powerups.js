// Power-ups System

const powerupDefinitions = {
    'double-dice': {
        name: 'Double Dice',
        description: 'Roll with advantage for the next turn',
        cost: 100,
        icon: '⚡',
        duration: 1
    },
    'rent-shield': {
        name: 'Rent Shield',
        description: 'Protect from rent payments for 3 turns',
        cost: 150,
        icon: '🛡️',
        duration: 3
    },
    'property-swap': {
        name: 'Property Swap',
        description: 'Force a property trade with another player',
        cost: 200,
        icon: '🔄',
        duration: 1
    },
    'banker-boost': {
        name: "Banker's Boost",
        description: 'Receive $500 bonus money',
        cost: 250,
        icon: '💰',
        duration: 1
    }
};

let activePowerups = [];

// Setup Powerup Event Listeners
function setupPowerupListeners() {
    document.querySelectorAll('.power-up').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const powerupType = e.target.dataset.powerup;
            usePowerup(powerupType);
        });
    });
}

// Use Powerup
function usePowerup(powerupType) {
    const powerup = powerupDefinitions[powerupType];
    const currentPlayer = gameState.players[gameState.currentPlayerIndex];
    
    if (!powerup) {
        addChatMessage("Unknown power-up!", 'system');
        return;
    }
    
    if (currentPlayer.money < powerup.cost) {
        addChatMessage(`Not enough money! ${powerup.name} costs $${powerup.cost}`, 'system');
        return;
    }
    
    // Check if powerup is already active
    if (activePowerups.some(p => p.type === powerupType && p.player === currentPlayer)) {
        addChatMessage(`${powerup.name} is already active!`, 'system');
        return;
    }
    
    // Deduct cost
    currentPlayer.removeMoney(powerup.cost);
    
    // Apply powerup effect
    switch(powerupType) {
        case 'double-dice':
            activateDoubleDice(currentPlayer, powerup);
            break;
        case 'rent-shield':
            activateRentShield(currentPlayer, powerup);
            break;
        case 'property-swap':
            activatePropertySwap(currentPlayer, powerup);
            break;
        case 'banker-boost':
            activateBankerBoost(currentPlayer, powerup);
            break;
    }
    
    addChatMessage(`${currentPlayer.name} used ${powerup.name}! ${powerup.icon}`, 'game');
    addExperience(20);
}

// Double Dice Powerup
function activateDoubleDice(player, powerup) {
    activePowerups.push({
        type: 'double-dice',
        player: player,
        turnsRemaining: powerup.duration
    });
    
    addChatMessage("Next roll will have advantage!", 'system');
}

// Rent Shield Powerup
function activateRentShield(player, powerup) {
    activePowerups.push({
        type: 'rent-shield',
        player: player,
        turnsRemaining: powerup.duration
    });
    
    addChatMessage(`Protected from rent for ${powerup.duration} turns!`, 'system');
}

// Property Swap Powerup
function activatePropertySwap(player, powerup) {
    // Show property swap modal
    const otherPlayers = gameState.players.filter(p => p !== player && p.properties.length > 0);
    
    if (otherPlayers.length === 0) {
        addChatMessage("No other players have properties to swap!", 'system');
        player.addMoney(powerup.cost); // Refund
        return;
    }
    
    // For simplicity, randomly select a property from another player
    const targetPlayer = otherPlayers[Math.floor(Math.random() * otherPlayers.length)];
    const targetProperty = targetPlayer.properties[Math.floor(Math.random() * targetPlayer.properties.length)];
    
    // Swap random property
    if (player.properties.length > 0) {
        const myProperty = player.properties[Math.floor(Math.random() * player.properties.length)];
        
        // Remove properties from current owners
        player.properties = player.properties.filter(p => p !== myProperty);
        targetPlayer.properties = targetPlayer.properties.filter(p => p !== targetProperty);
        
        // Add to new owners
        player.properties.push(targetProperty);
        targetPlayer.properties.push(myProperty);
        
        // Update ownership
        myProperty.owner = targetPlayer;
        targetProperty.owner = player;
        
        addChatMessage(
            `${player.name} swapped ${myProperty.name} with ${targetPlayer.name}'s ${targetProperty.name}!`,
            'game'
        );
    } else {
        // Just take the property
        targetPlayer.properties = targetPlayer.properties.filter(p => p !== targetProperty);
        player.properties.push(targetProperty);
        targetProperty.owner = player;
        
        addChatMessage(
            `${player.name} took ${targetProperty.name} from ${targetPlayer.name}!`,
            'game'
        );
    }
    
    updatePropertiesDisplay();
    updatePropertyOwnership();
}

// Banker's Boost Powerup
function activateBankerBoost(player, powerup) {
    player.addMoney(500);
    addChatMessage("Received $500 bonus!", 'system');
}

// Check Active Powerups
function checkActivePowerups(player, event) {
    const playerPowerups = activePowerups.filter(p => p.player === player);
    
    // Rent Shield
    if (event === 'rent' && playerPowerups.some(p => p.type === 'rent-shield')) {
        addChatMessage("Rent Shield activated! No rent paid.", 'system');
        return true; // Block rent
    }
    
    return false;
}

// Apply Powerup Effects on Dice Roll
function applyPowerupsOnRoll(player) {
    const doubleDice = activePowerups.find(p => p.player === player && p.type === 'double-dice');
    
    if (doubleDice) {
        addChatMessage("Double Dice active! Rolling with advantage...", 'system');
        // Roll twice and take the better result
        return true;
    }
    
    return false;
}

// Decrease Powerup Turns
function decreasePowerupTurns() {
    activePowerups.forEach(powerup => {
        powerup.turnsRemaining--;
        
        if (powerup.turnsRemaining <= 0) {
            addChatMessage(
                `${powerupDefinitions[powerup.type].name} expired for ${powerup.player.name}`,
                'system'
            );
        }
    });
    
    // Remove expired powerups
    activePowerups = activePowerups.filter(p => p.turnsRemaining > 0);
}

// Display Active Powerups
function displayActivePowerups() {
    const currentPlayer = gameState.players[gameState.currentPlayerIndex];
    const playerPowerups = activePowerups.filter(p => p.player === currentPlayer);
    
    if (playerPowerups.length > 0) {
        const powerupText = playerPowerups.map(p => {
            const def = powerupDefinitions[p.type];
            return `${def.icon} ${def.name} (${p.turnsRemaining} turns)`;
        }).join(', ');
        
        // Could display this in UI
        console.log('Active powerups:', powerupText);
    }
}

// Initialize powerups
document.addEventListener('DOMContentLoaded', setupPowerupListeners);

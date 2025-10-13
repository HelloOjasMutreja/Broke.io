// Auction System

let auctionState = {
    isActive: false,
    property: null,
    currentBid: 0,
    highestBidder: null,
    timeRemaining: 30,
    timer: null
};

// Start Auction
function startAuction() {
    const modal = document.getElementById('property-modal');
    const position = parseInt(modal.dataset.propertyPosition);
    const property = gameState.properties.find(p => p.position === position);
    
    if (!property || property.owner) {
        addChatMessage("Cannot auction this property!", 'system');
        return;
    }
    
    // Close property modal
    modal.style.display = 'none';
    
    // Initialize auction
    auctionState.isActive = true;
    auctionState.property = property;
    auctionState.currentBid = 0;
    auctionState.highestBidder = null;
    auctionState.timeRemaining = 30;
    
    // Show auction modal
    const auctionModal = document.getElementById('auction-modal');
    document.getElementById('auction-property-name').textContent = property.name;
    document.getElementById('bid-amount').textContent = '0';
    document.getElementById('bidder-name').textContent = 'None';
    auctionModal.style.display = 'block';
    
    // Start timer
    startAuctionTimer();
    
    addChatMessage(`Auction started for ${property.name}!`, 'system');
}

// Start Auction Timer
function startAuctionTimer() {
    const timerDisplay = document.getElementById('timer-display');
    
    auctionState.timer = setInterval(() => {
        auctionState.timeRemaining--;
        timerDisplay.textContent = auctionState.timeRemaining;
        
        if (auctionState.timeRemaining <= 0) {
            endAuction();
        } else if (auctionState.timeRemaining <= 10) {
            timerDisplay.style.color = '#ff0000';
        }
    }, 1000);
}

// Place Bid
function placeBid() {
    const bidInput = document.getElementById('bid-input');
    const bidAmount = parseInt(bidInput.value);
    const currentPlayer = gameState.players[gameState.currentPlayerIndex];
    
    if (!auctionState.isActive) {
        addChatMessage("No active auction!", 'system');
        return;
    }
    
    if (isNaN(bidAmount) || bidAmount <= auctionState.currentBid) {
        addChatMessage(`Bid must be higher than $${auctionState.currentBid}!`, 'system');
        return;
    }
    
    if (bidAmount > currentPlayer.money) {
        addChatMessage("You don't have enough money for that bid!", 'system');
        return;
    }
    
    // Update auction state
    auctionState.currentBid = bidAmount;
    auctionState.highestBidder = currentPlayer;
    
    // Update display
    document.getElementById('bid-amount').textContent = bidAmount;
    document.getElementById('bidder-name').textContent = currentPlayer.name;
    
    addChatMessage(`${currentPlayer.name} bid $${bidAmount}!`, 'game');
    
    // Clear input
    bidInput.value = '';
    
    // Add 5 seconds to timer if less than 10 seconds remaining
    if (auctionState.timeRemaining < 10) {
        auctionState.timeRemaining += 5;
        addChatMessage("Timer extended by 5 seconds!", 'system');
    }
}

// End Auction
function endAuction() {
    clearInterval(auctionState.timer);
    
    const auctionModal = document.getElementById('auction-modal');
    
    if (auctionState.highestBidder && auctionState.currentBid > 0) {
        // Award property to highest bidder
        const property = auctionState.property;
        auctionState.highestBidder.removeMoney(auctionState.currentBid);
        auctionState.highestBidder.properties.push(property);
        property.owner = auctionState.highestBidder;
        
        addChatMessage(
            `${auctionState.highestBidder.name} won ${property.name} for $${auctionState.currentBid}!`,
            'system'
        );
        
        updatePropertiesDisplay();
        updatePropertyOwnership();
    } else {
        addChatMessage("Auction ended with no bids.", 'system');
    }
    
    // Close modal
    setTimeout(() => {
        auctionModal.style.display = 'none';
    }, 2000);
    
    // Reset auction state
    auctionState.isActive = false;
    auctionState.property = null;
    auctionState.currentBid = 0;
    auctionState.highestBidder = null;
    auctionState.timeRemaining = 30;
}

// Setup auction event listener
document.addEventListener('DOMContentLoaded', () => {
    const placeBidBtn = document.getElementById('place-bid-btn');
    if (placeBidBtn) {
        placeBidBtn.addEventListener('click', placeBid);
    }
    
    const bidInput = document.getElementById('bid-input');
    if (bidInput) {
        bidInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                placeBid();
            }
        });
    }
});

// Board Animation and Visualization

// Animate board on load
document.addEventListener('DOMContentLoaded', () => {
    animateBoardEntrance();
});

// Board entrance animation
function animateBoardEntrance() {
    const spaces = document.querySelectorAll('.space');
    spaces.forEach((space, index) => {
        setTimeout(() => {
            space.style.opacity = '0';
            space.style.transform = 'scale(0.8)';
            setTimeout(() => {
                space.style.transition = 'all 0.3s ease';
                space.style.opacity = '1';
                space.style.transform = 'scale(1)';
            }, 50);
        }, index * 20);
    });
}

// Highlight current player position
function highlightPlayerPosition(position) {
    // Remove previous highlights
    document.querySelectorAll('.space').forEach(space => {
        space.classList.remove('highlighted');
    });
    
    // Add highlight to current position
    const spaceElement = document.querySelector(`[data-position="${position}"]`);
    if (spaceElement) {
        spaceElement.classList.add('highlighted');
        spaceElement.style.boxShadow = '0 0 20px rgba(102, 126, 234, 0.8)';
        
        setTimeout(() => {
            spaceElement.style.boxShadow = '';
        }, 1000);
    }
}

// Animate player movement
function animatePlayerMovement(fromPosition, toPosition, callback) {
    const steps = toPosition > fromPosition ? toPosition - fromPosition : (40 - fromPosition) + toPosition;
    let currentPos = fromPosition;
    let step = 0;
    
    const interval = setInterval(() => {
        currentPos = (currentPos + 1) % 40;
        step++;
        
        highlightPlayerPosition(currentPos);
        
        if (step >= steps) {
            clearInterval(interval);
            if (callback) callback();
        }
    }, 200);
}

// Create property ownership indicators
function updatePropertyOwnership() {
    gameState.properties.forEach(property => {
        const spaceElement = document.querySelector(`[data-position="${property.position}"]`);
        if (spaceElement && property.owner) {
            // Remove existing ownership indicator
            const existingIndicator = spaceElement.querySelector('.ownership-indicator');
            if (existingIndicator) {
                existingIndicator.remove();
            }
            
            // Add new ownership indicator
            const indicator = document.createElement('div');
            indicator.className = 'ownership-indicator';
            indicator.textContent = property.owner.token;
            indicator.style.cssText = 'position: absolute; bottom: 2px; left: 2px; font-size: 1em; z-index: 50;';
            spaceElement.style.position = 'relative';
            spaceElement.appendChild(indicator);
        }
    });
}

// Board theme effects
function applyBoardTheme(theme) {
    const board = document.getElementById('game-board');
    board.className = 'animated-board';
    
    switch(theme) {
        case 'cyber':
            board.style.background = 'linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)';
            board.style.border = '2px solid #00ffff';
            break;
        case 'fantasy':
            board.style.background = 'linear-gradient(135deg, #8e2de2 0%, #4a00e0 100%)';
            board.style.border = '2px solid #ffd700';
            break;
        case 'space':
            board.style.background = 'linear-gradient(135deg, #000000 0%, #434343 100%)';
            board.style.border = '2px solid #ffffff';
            break;
        default:
            board.style.background = 'rgba(255, 255, 255, 0.95)';
            board.style.border = 'none';
    }
}

// Pulse animation for interactive elements
function pulseElement(element) {
    element.style.animation = 'none';
    setTimeout(() => {
        element.style.animation = 'pulse 0.5s ease';
    }, 10);
}

// Add CSS for pulse animation
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    .highlighted {
        animation: highlight 0.5s ease;
    }
    
    @keyframes highlight {
        0%, 100% { background-color: inherit; }
        50% { background-color: rgba(102, 126, 234, 0.3); }
    }
`;
document.head.appendChild(style);

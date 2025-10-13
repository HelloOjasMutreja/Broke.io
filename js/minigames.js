// Mini-games System

const minigames = {
    'target-click': {
        name: 'Target Click',
        description: 'Click targets as fast as you can!',
        reward: 200
    },
    'memory-match': {
        name: 'Memory Match',
        description: 'Match the property pairs!',
        reward: 300
    },
    'quick-math': {
        name: 'Quick Math',
        description: 'Solve math problems quickly!',
        reward: 250
    }
};

let minigameState = {
    active: false,
    type: null,
    score: 0,
    timeRemaining: 30
};

// Trigger Random Minigame
function triggerRandomMinigame() {
    if (Math.random() < 0.2) { // 20% chance on landing
        const types = Object.keys(minigames);
        const randomType = types[Math.floor(Math.random() * types.length)];
        startMinigame(randomType);
    }
}

// Start Minigame
function startMinigame(type) {
    const minigame = minigames[type];
    
    if (!minigame) return;
    
    minigameState.active = true;
    minigameState.type = type;
    minigameState.score = 0;
    minigameState.timeRemaining = 30;
    
    const modal = document.getElementById('minigame-modal');
    const content = document.getElementById('minigame-content');
    
    content.querySelector('p').textContent = minigame.description;
    
    // Setup minigame
    switch(type) {
        case 'target-click':
            setupTargetClick();
            break;
        case 'memory-match':
            setupMemoryMatch();
            break;
        case 'quick-math':
            setupQuickMath();
            break;
    }
    
    modal.style.display = 'block';
    addChatMessage(`Mini-game started: ${minigame.name}!`, 'system');
    
    // Start timer
    startMinigameTimer();
}

// Start Minigame Timer
function startMinigameTimer() {
    const timer = setInterval(() => {
        minigameState.timeRemaining--;
        
        if (minigameState.timeRemaining <= 0) {
            clearInterval(timer);
            endMinigame();
        }
    }, 1000);
}

// End Minigame
function endMinigame() {
    minigameState.active = false;
    
    const minigame = minigames[minigameState.type];
    const currentPlayer = gameState.players[gameState.currentPlayerIndex];
    
    // Calculate reward based on score
    const reward = Math.floor((minigameState.score / 10) * minigame.reward);
    
    if (reward > 0) {
        currentPlayer.addMoney(reward);
        addChatMessage(`Mini-game complete! Earned $${reward}!`, 'system');
        addExperience(30);
    } else {
        addChatMessage("Mini-game complete! Better luck next time!", 'system');
    }
    
    setTimeout(() => {
        document.getElementById('minigame-modal').style.display = 'none';
    }, 2000);
}

// Target Click Minigame
function setupTargetClick() {
    const area = document.getElementById('minigame-area');
    area.innerHTML = '';
    
    function createTarget() {
        if (!minigameState.active) return;
        
        const target = document.createElement('div');
        target.className = 'minigame-target';
        target.style.cssText = `
            position: absolute;
            width: 50px;
            height: 50px;
            background: radial-gradient(circle, #ff0000, #cc0000);
            border-radius: 50%;
            cursor: pointer;
            left: ${Math.random() * 80}%;
            top: ${Math.random() * 80}%;
            animation: targetPulse 0.5s ease-in-out;
        `;
        
        target.addEventListener('click', () => {
            minigameState.score++;
            document.getElementById('minigame-score-value').textContent = minigameState.score;
            target.remove();
            createTarget();
        });
        
        area.appendChild(target);
        
        // Auto-remove after 2 seconds
        setTimeout(() => {
            if (target.parentElement) {
                target.remove();
                createTarget();
            }
        }, 2000);
    }
    
    // Add CSS for target animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes targetPulse {
            from { transform: scale(0); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    createTarget();
}

// Memory Match Minigame
function setupMemoryMatch() {
    const area = document.getElementById('minigame-area');
    area.innerHTML = '';
    
    const properties = ['🏠', '🏢', '🏪', '🏨', '🏦', '🏫'];
    const cards = [...properties, ...properties].sort(() => Math.random() - 0.5);
    
    let flipped = [];
    let matched = [];
    
    area.style.display = 'grid';
    area.style.gridTemplateColumns = 'repeat(4, 1fr)';
    area.style.gap = '10px';
    
    cards.forEach((card, index) => {
        const cardElement = document.createElement('div');
        cardElement.className = 'memory-card';
        cardElement.dataset.index = index;
        cardElement.style.cssText = `
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 2em;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            cursor: pointer;
            height: 60px;
            transition: all 0.3s ease;
        `;
        cardElement.textContent = '?';
        
        cardElement.addEventListener('click', () => {
            if (flipped.length < 2 && !flipped.includes(index) && !matched.includes(index)) {
                cardElement.textContent = card;
                flipped.push(index);
                
                if (flipped.length === 2) {
                    const [first, second] = flipped;
                    if (cards[first] === cards[second]) {
                        // Match!
                        matched.push(first, second);
                        minigameState.score += 2;
                        document.getElementById('minigame-score-value').textContent = minigameState.score;
                        flipped = [];
                        
                        if (matched.length === cards.length) {
                            addChatMessage("Perfect! All matched!", 'system');
                            minigameState.score += 10;
                        }
                    } else {
                        // No match
                        setTimeout(() => {
                            document.querySelector(`[data-index="${first}"]`).textContent = '?';
                            document.querySelector(`[data-index="${second}"]`).textContent = '?';
                            flipped = [];
                        }, 1000);
                    }
                }
            }
        });
        
        area.appendChild(cardElement);
    });
}

// Quick Math Minigame
function setupQuickMath() {
    const area = document.getElementById('minigame-area');
    area.innerHTML = '';
    
    function generateProblem() {
        if (!minigameState.active) return;
        
        const num1 = Math.floor(Math.random() * 50) + 1;
        const num2 = Math.floor(Math.random() * 50) + 1;
        const operators = ['+', '-', '*'];
        const operator = operators[Math.floor(Math.random() * operators.length)];
        
        let answer;
        switch(operator) {
            case '+': answer = num1 + num2; break;
            case '-': answer = num1 - num2; break;
            case '*': answer = num1 * num2; break;
        }
        
        area.innerHTML = `
            <div style="text-align: center; font-size: 2em; margin: 40px 0;">
                ${num1} ${operator} ${num2} = ?
            </div>
            <div style="display: flex; gap: 10px; justify-content: center;">
                <input type="number" id="math-answer" 
                    style="padding: 10px; font-size: 1.2em; width: 150px; border: 2px solid #667eea; border-radius: 8px;">
                <button id="math-submit" 
                    style="padding: 10px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">
                    Submit
                </button>
            </div>
        `;
        
        const submitBtn = document.getElementById('math-submit');
        const input = document.getElementById('math-answer');
        
        const checkAnswer = () => {
            const userAnswer = parseInt(input.value);
            if (userAnswer === answer) {
                minigameState.score += 3;
                document.getElementById('minigame-score-value').textContent = minigameState.score;
                generateProblem();
            } else {
                input.style.borderColor = '#ff0000';
                setTimeout(() => {
                    input.style.borderColor = '#667eea';
                }, 500);
            }
        };
        
        submitBtn.addEventListener('click', checkAnswer);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') checkAnswer();
        });
        
        input.focus();
    }
    
    generateProblem();
}

// Randomly trigger minigames on certain events
function maybeStartMinigame() {
    if (!minigameState.active && Math.random() < 0.15) {
        const types = Object.keys(minigames);
        const randomType = types[Math.floor(Math.random() * types.length)];
        setTimeout(() => startMinigame(randomType), 1000);
    }
}

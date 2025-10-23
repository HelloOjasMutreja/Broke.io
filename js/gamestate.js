// Client-side Game State Management
// Reduces server calls by caching and managing game state on the client

class GameStateManager {
    constructor(gameId) {
        this.gameId = gameId;
        this.state = {
            game: null,
            players: [],
            currentTurn: null,
            recentActions: [],
            lastUpdate: null
        };
        this.updateCallbacks = [];
        this.pollingInterval = null;
    }

    /**
     * Initialize the state manager with initial data
     * @param {Object} initialData - Initial game state from server
     */
    initialize(initialData) {
        this.state.game = initialData.game || null;
        this.state.players = initialData.players || [];
        this.state.currentTurn = initialData.currentTurn || null;
        this.state.recentActions = initialData.recentActions || [];
        this.state.lastUpdate = Date.now();
        this.notifyCallbacks();
    }

    /**
     * Get current game state
     * @returns {Object} - Current state
     */
    getState() {
        return { ...this.state };
    }

    /**
     * Get specific player by ID
     * @param {number} playerId - Player ID
     * @returns {Object|null} - Player object or null
     */
    getPlayer(playerId) {
        return this.state.players.find(p => p.id === playerId) || null;
    }

    /**
     * Update player data locally
     * @param {number} playerId - Player ID
     * @param {Object} updates - Updates to apply
     */
    updatePlayer(playerId, updates) {
        const playerIndex = this.state.players.findIndex(p => p.id === playerId);
        if (playerIndex !== -1) {
            this.state.players[playerIndex] = {
                ...this.state.players[playerIndex],
                ...updates
            };
            this.state.lastUpdate = Date.now();
            this.notifyCallbacks();
        }
    }

    /**
     * Update multiple players at once
     * @param {Array} playersData - Array of player objects
     */
    updatePlayers(playersData) {
        playersData.forEach(playerData => {
            const playerIndex = this.state.players.findIndex(p => p.id === playerData.id);
            if (playerIndex !== -1) {
                this.state.players[playerIndex] = {
                    ...this.state.players[playerIndex],
                    ...playerData
                };
            }
        });
        this.state.lastUpdate = Date.now();
        this.notifyCallbacks();
    }

    /**
     * Update current turn information
     * @param {Object} turnData - Turn data from server
     */
    updateCurrentTurn(turnData) {
        this.state.currentTurn = turnData;
        this.state.lastUpdate = Date.now();
        this.notifyCallbacks();
    }

    /**
     * Add an action to recent actions
     * @param {Object} action - Action object
     */
    addAction(action) {
        this.state.recentActions.unshift(action);
        // Keep only last 20 actions
        if (this.state.recentActions.length > 20) {
            this.state.recentActions = this.state.recentActions.slice(0, 20);
        }
        this.state.lastUpdate = Date.now();
        this.notifyCallbacks();
    }

    /**
     * Register a callback to be notified of state changes
     * @param {Function} callback - Callback function
     */
    onUpdate(callback) {
        if (typeof callback === 'function') {
            this.updateCallbacks.push(callback);
        }
    }

    /**
     * Notify all registered callbacks of state change
     */
    notifyCallbacks() {
        this.updateCallbacks.forEach(callback => {
            try {
                callback(this.getState());
            } catch (error) {
                console.error('Error in state update callback:', error);
            }
        });
    }

    /**
     * Fetch latest state from server
     * @returns {Promise} - Promise that resolves with updated state
     */
    async fetchState() {
        try {
            const response = await fetch(`/game/${this.gameId}/state/`);
            if (!response.ok) {
                throw new Error('Failed to fetch game state');
            }
            const data = await response.json();
            
            // Update state with server data
            if (data.game) {
                this.state.game = data.game;
            }
            if (data.players) {
                this.updatePlayers(data.players);
            }
            if (data.current_turn) {
                this.updateCurrentTurn(data.current_turn);
            }
            
            return this.getState();
        } catch (error) {
            console.error('Error fetching game state:', error);
            throw error;
        }
    }

    /**
     * Start polling for state updates
     * @param {number} interval - Polling interval in milliseconds (default: 5000)
     */
    startPolling(interval = 5000) {
        if (this.pollingInterval) {
            this.stopPolling();
        }
        
        this.pollingInterval = setInterval(async () => {
            try {
                await this.fetchState();
            } catch (error) {
                console.error('Polling error:', error);
            }
        }, interval);
    }

    /**
     * Stop polling for state updates
     */
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }

    /**
     * Check if it's the current user's turn
     * @param {number} currentPlayerId - Current user's player ID
     * @returns {boolean} - True if it's the user's turn
     */
    isMyTurn(currentPlayerId) {
        return this.state.currentTurn && 
               this.state.currentTurn.player_id === currentPlayerId;
    }

    /**
     * Get time since last update
     * @returns {number} - Milliseconds since last update
     */
    getTimeSinceUpdate() {
        return this.state.lastUpdate ? Date.now() - this.state.lastUpdate : 0;
    }

    /**
     * Clear all state
     */
    clear() {
        this.stopPolling();
        this.state = {
            game: null,
            players: [],
            currentTurn: null,
            recentActions: [],
            lastUpdate: null
        };
        this.updateCallbacks = [];
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GameStateManager;
}

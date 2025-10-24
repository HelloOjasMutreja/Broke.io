// API Client for Broke.io
// Centralized API calls to reduce redundant code and improve error handling

class BrokeIOAPI {
    constructor() {
        this.baseUrl = '';
        this.csrfToken = null;
    }

    /**
     * Initialize API client with CSRF token
     * @param {string} csrfToken - CSRF token for Django
     */
    initialize(csrfToken) {
        this.csrfToken = csrfToken;
    }

    /**
     * Get CSRF token from cookies
     * @returns {string|null} - CSRF token
     */
    getCsrfToken() {
        if (this.csrfToken) {
            return this.csrfToken;
        }
        
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        this.csrfToken = cookieValue;
        return cookieValue;
    }

    /**
     * Make a request to the API
     * @param {string} url - API endpoint
     * @param {Object} options - Fetch options
     * @returns {Promise} - Response promise
     */
    async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            }
        };

        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...(options.headers || {})
            }
        };

        try {
            const response = await fetch(this.baseUrl + url, mergedOptions);
            
            // Handle non-JSON responses
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                
                if (!response.ok) {
                    throw new APIError(data.error || 'Request failed', response.status, data);
                }
                
                return data;
            } else {
                if (!response.ok) {
                    throw new APIError('Request failed', response.status);
                }
                return response;
            }
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }
            throw new APIError('Network error: ' + error.message, 0);
        }
    }

    /**
     * Create a new game
     * @param {Object} gameData - Game creation data
     * @returns {Promise} - Created game data
     */
    async createGame(gameData) {
        return this.request('/game/create/', {
            method: 'POST',
            body: JSON.stringify(gameData)
        });
    }

    /**
     * Join a game
     * @param {number} gameId - Game ID to join
     * @returns {Promise} - Join result
     */
    async joinGame(gameId) {
        return this.request(`/game/${gameId}/join/`, {
            method: 'POST'
        });
    }

    /**
     * Toggle ready status
     * @param {number} gameId - Game ID
     * @returns {Promise} - Updated ready status
     */
    async toggleReady(gameId) {
        return this.request(`/game/${gameId}/toggle-ready/`, {
            method: 'POST'
        });
    }

    /**
     * Start a game
     * @param {number} gameId - Game ID to start
     * @returns {Promise} - Start result
     */
    async startGame(gameId) {
        return this.request(`/game/${gameId}/start/`, {
            method: 'POST'
        });
    }

    /**
     * Roll dice
     * @param {number} gameId - Game ID
     * @returns {Promise} - Dice roll result
     */
    async rollDice(gameId) {
        return this.request(`/game/${gameId}/roll-dice/`, {
            method: 'POST'
        });
    }

    /**
     * Buy property
     * @param {number} gameId - Game ID
     * @returns {Promise} - Purchase result
     */
    async buyProperty(gameId) {
        return this.request(`/game/${gameId}/buy-property/`, {
            method: 'POST'
        });
    }

    /**
     * End turn
     * @param {number} gameId - Game ID
     * @returns {Promise} - End turn result
     */
    async endTurn(gameId) {
        return this.request(`/game/${gameId}/end-turn/`, {
            method: 'POST'
        });
    }

    /**
     * Get game state
     * @param {number} gameId - Game ID
     * @returns {Promise} - Current game state
     */
    async getGameState(gameId) {
        return this.request(`/game/${gameId}/state/`);
    }

    /**
     * Get game list
     * @param {Object} filters - Optional filters (mode, status, etc.)
     * @returns {Promise} - List of games
     */
    async getGameList(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`/game/list/?${params}`);
    }

    /**
     * Send chat message
     * @param {number} gameId - Game ID
     * @param {string} message - Message content
     * @returns {Promise} - Send result
     */
    async sendChatMessage(gameId, message) {
        return this.request(`/game/${gameId}/chat/`, {
            method: 'POST',
            body: JSON.stringify({ message })
        });
    }

    /**
     * Get chat messages
     * @param {number} gameId - Game ID
     * @param {number} since - Get messages since timestamp
     * @returns {Promise} - List of messages
     */
    async getChatMessages(gameId, since = null) {
        const params = since ? `?since=${since}` : '';
        return this.request(`/game/${gameId}/chat/${params}`);
    }

    /**
     * Create trade offer
     * @param {number} gameId - Game ID
     * @param {Object} tradeData - Trade offer data
     * @returns {Promise} - Created trade
     */
    async createTrade(gameId, tradeData) {
        return this.request(`/game/${gameId}/trade/`, {
            method: 'POST',
            body: JSON.stringify(tradeData)
        });
    }

    /**
     * Respond to trade
     * @param {number} gameId - Game ID
     * @param {number} tradeId - Trade ID
     * @param {boolean} accept - Accept or reject
     * @returns {Promise} - Trade response result
     */
    async respondToTrade(gameId, tradeId, accept) {
        return this.request(`/game/${gameId}/trade/${tradeId}/`, {
            method: 'POST',
            body: JSON.stringify({ accept })
        });
    }

    /**
     * Place auction bid
     * @param {number} gameId - Game ID
     * @param {number} amount - Bid amount
     * @returns {Promise} - Bid result
     */
    async placeBid(gameId, amount) {
        return this.request(`/game/${gameId}/auction/bid/`, {
            method: 'POST',
            body: JSON.stringify({ amount })
        });
    }
}

/**
 * Custom error class for API errors
 */
class APIError extends Error {
    constructor(message, statusCode, data = null) {
        super(message);
        this.name = 'APIError';
        this.statusCode = statusCode;
        this.data = data;
    }
}

// Create singleton instance
const api = new BrokeIOAPI();

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { BrokeIOAPI, APIError, api };
} else if (typeof window !== 'undefined') {
    window.BrokeIOAPI = BrokeIOAPI;
    window.APIError = APIError;
    window.api = api;
}

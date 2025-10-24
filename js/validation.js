// Client-side Validation Utilities for Broke.io
// Reduces server load by validating inputs before submission

/**
 * Validate game name
 * @param {string} name - Game name to validate
 * @returns {Object} - {valid: boolean, error: string}
 */
function validateGameName(name) {
    if (!name || name.trim().length === 0) {
        return { valid: false, error: 'Game name is required' };
    }
    if (name.length > 140) {
        return { valid: false, error: 'Game name must be 140 characters or less' };
    }
    if (name.trim().length < 3) {
        return { valid: false, error: 'Game name must be at least 3 characters' };
    }
    return { valid: true, error: null };
}

/**
 * Validate max players
 * @param {number} maxPlayers - Maximum number of players
 * @returns {Object} - {valid: boolean, error: string}
 */
function validateMaxPlayers(maxPlayers) {
    const num = parseInt(maxPlayers);
    if (isNaN(num)) {
        return { valid: false, error: 'Max players must be a number' };
    }
    if (num < 2) {
        return { valid: false, error: 'Must have at least 2 players' };
    }
    if (num > 8) {
        return { valid: false, error: 'Cannot have more than 8 players' };
    }
    return { valid: true, error: null };
}

/**
 * Validate board selection
 * @param {string} boardId - Board ID to validate
 * @returns {Object} - {valid: boolean, error: string}
 */
function validateBoardSelection(boardId) {
    if (!boardId || boardId === '') {
        return { valid: false, error: 'Please select a board' };
    }
    return { valid: true, error: null };
}

/**
 * Validate game mode
 * @param {string} mode - Game mode to validate
 * @returns {Object} - {valid: boolean, error: string}
 */
function validateGameMode(mode) {
    const validModes = ['solo', 'SOLO', 'friends', 'FRIENDS', 'online', 'ONLINE'];
    if (!mode || !validModes.includes(mode)) {
        return { valid: false, error: 'Invalid game mode selected' };
    }
    return { valid: true, error: null };
}

/**
 * Validate create game form
 * @param {Object} formData - Form data object with game details
 * @returns {Object} - {valid: boolean, errors: Array}
 */
function validateCreateGameForm(formData) {
    const errors = [];
    
    const nameValidation = validateGameName(formData.game_name);
    if (!nameValidation.valid) {
        errors.push(nameValidation.error);
    }
    
    const boardValidation = validateBoardSelection(formData.board_id);
    if (!boardValidation.valid) {
        errors.push(boardValidation.error);
    }
    
    const modeValidation = validateGameMode(formData.game_mode);
    if (!modeValidation.valid) {
        errors.push(modeValidation.error);
    }
    
    const playersValidation = validateMaxPlayers(formData.max_players);
    if (!playersValidation.valid) {
        errors.push(playersValidation.error);
    }
    
    return {
        valid: errors.length === 0,
        errors: errors
    };
}

/**
 * Show validation errors in the UI
 * @param {Array} errors - Array of error messages
 * @param {HTMLElement} container - Container element to show errors
 */
function showValidationErrors(errors, container) {
    // Clear previous errors
    container.innerHTML = '';
    
    if (errors.length === 0) {
        container.style.display = 'none';
        return;
    }
    
    // Create error display
    container.style.display = 'block';
    container.style.background = '#f8d7da';
    container.style.border = '2px solid #dc3545';
    container.style.borderRadius = '8px';
    container.style.padding = '15px';
    container.style.marginBottom = '15px';
    container.style.color = '#721c24';
    
    const errorList = document.createElement('ul');
    errorList.style.margin = '0';
    errorList.style.paddingLeft = '20px';
    
    errors.forEach(error => {
        const li = document.createElement('li');
        li.textContent = error;
        li.style.marginBottom = '5px';
        errorList.appendChild(li);
    });
    
    const title = document.createElement('strong');
    title.textContent = 'Please fix the following errors:';
    title.style.display = 'block';
    title.style.marginBottom = '10px';
    
    container.appendChild(title);
    container.appendChild(errorList);
}

/**
 * Clear validation errors from the UI
 * @param {HTMLElement} container - Container element with errors
 */
function clearValidationErrors(container) {
    container.innerHTML = '';
    container.style.display = 'none';
}

/**
 * Add real-time validation to an input field
 * @param {HTMLElement} input - Input element to validate
 * @param {Function} validationFn - Validation function to use
 * @param {HTMLElement} feedbackElement - Element to show feedback
 */
function addRealtimeValidation(input, validationFn, feedbackElement) {
    input.addEventListener('blur', () => {
        const result = validationFn(input.value);
        if (!result.valid) {
            input.style.borderColor = '#dc3545';
            feedbackElement.textContent = result.error;
            feedbackElement.style.color = '#dc3545';
            feedbackElement.style.display = 'block';
        } else {
            input.style.borderColor = '#28a745';
            feedbackElement.style.display = 'none';
        }
    });
    
    input.addEventListener('input', () => {
        // Clear error styling while typing
        if (input.style.borderColor === 'rgb(220, 53, 69)') { // #dc3545
            input.style.borderColor = '';
        }
    });
}

// Export functions for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        validateGameName,
        validateMaxPlayers,
        validateBoardSelection,
        validateGameMode,
        validateCreateGameForm,
        showValidationErrors,
        clearValidationErrors,
        addRealtimeValidation
    };
}

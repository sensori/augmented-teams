/**
 * Create Mob Module
 * 
 * Implements the Create Mob sub-epic functionality for grouping minion tokens into mobs.
 * This module handles token selection, mob creation, and confirmation.
 */

/**
 * TokenSelector - Handles selection of multiple minion tokens
 * 
 * Story: Select Multiple Tokens
 */
export class TokenSelector {
    /**
     * @param {Object} foundryTokenApi - Foundry VTT Token API dependency
     */
    constructor(foundryTokenApi) {
        this.foundryTokenApi = foundryTokenApi;
    }

    /**
     * Select multiple minion tokens from Foundry canvas
     * 
     * Scenario: Game Master selects multiple tokens successfully
     * 
     * @returns {Array<Object>} Array of selected token objects with id and actorId
     * @throws {Error} If zero tokens are selected
     */
    selectMultipleTokens() {
        const selectedTokens = this.foundryTokenApi.getSelectedTokens();
        
        if (selectedTokens.length === 0) {
            throw new Error("At least one token must be selected");
        }

        return selectedTokens.map(token => ({
            id: token.id,
            actorId: token.actorId,
            name: token.name
        }));
    }
}

/**
 * MobCreator - Handles creation of mob entities from selected tokens
 * 
 * Story: Group Tokens Into Mob
 */
export class MobCreator {
    /**
     * @param {Object} foundryTokenApi - Foundry VTT Token API dependency
     * @param {Object} foundryActorSystem - Foundry VTT Actor System dependency
     */
    constructor(foundryTokenApi, foundryActorSystem) {
        this.foundryTokenApi = foundryTokenApi;
        this.foundryActorSystem = foundryActorSystem;
    }

    /**
     * Create a new mob entity containing selected tokens
     * 
     * Scenario: Game Master groups tokens into mob successfully
     * 
     * @param {Array<Object>} selectedTokens - Array of token objects to group
     * @returns {Object} Mob entity with id, tokenIds, and actorIds
     */
    groupTokensIntoMob(selectedTokens) {
        const mobId = this._generateMobId();
        
        const tokenIds = selectedTokens.map(token => token.id);
        const actorIds = selectedTokens.map(token => token.actorId);

        // Link all tokens to mob entity via Foundry Token API
        this._linkTokensToMob(tokenIds, mobId);

        return {
            id: mobId,
            tokenIds: tokenIds,
            actorIds: actorIds,
            strategy: null
        };
    }

    /**
     * Link tokens to mob entity via Foundry Token API
     * 
     * @private
     * @param {Array<string>} tokenIds - Array of token IDs
     * @param {string} mobId - Mob entity ID
     */
    _linkTokensToMob(tokenIds, mobId) {
        tokenIds.forEach(tokenId => {
            const token = this.foundryTokenApi.getTokenById(tokenId);
            if (token) {
                token.setFlag('mob-minion', 'mobId', mobId);
            }
        });
    }

    /**
     * Generate unique mob ID
     * 
     * @private
     * @returns {string} Unique mob identifier
     */
    _generateMobId() {
        return `mob_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
}

/**
 * MobCreationConfirmation - Handles confirmation dialog and persistence
 * 
 * Story: Display Mob Creation Confirmation
 */
export class MobCreationConfirmation {
    /**
     * @param {Object} foundryActorSystem - Foundry VTT Actor System dependency
     * @param {Object} dialogManager - Dialog management dependency
     */
    constructor(foundryActorSystem, dialogManager) {
        this.foundryActorSystem = foundryActorSystem;
        this.dialogManager = dialogManager;
    }

    /**
     * Display confirmation dialog showing mob name and token count
     * 
     * Scenario: Game Master confirms mob creation
     * 
     * @param {Object} mobEntity - Mob entity to confirm
     * @returns {Promise<boolean>} True if confirmed, false if cancelled
     */
    async displayConfirmation(mobEntity) {
        const mobName = mobEntity.name || `Mob ${mobEntity.id}`;
        const tokenCount = mobEntity.tokenIds.length;

        return await this.dialogManager.showDialog({
            title: "Confirm Mob Creation",
            content: `Create mob "${mobName}" with ${tokenCount} tokens?`,
            buttons: {
                confirm: {
                    label: "Confirm",
                    callback: () => true
                },
                cancel: {
                    label: "Cancel",
                    callback: () => false
                }
            }
        });
    }

    /**
     * Persist mob in Foundry actor system
     * 
     * @param {Object} mobEntity - Mob entity to persist
     */
    persistMob(mobEntity) {
        this.foundryActorSystem.createEmbeddedDocuments('Actor', [{
            name: mobEntity.name || `Mob ${mobEntity.id}`,
            type: 'mob',
            flags: {
                'mob-minion': {
                    mobId: mobEntity.id,
                    tokenIds: mobEntity.tokenIds,
                    actorIds: mobEntity.actorIds,
                    strategy: mobEntity.strategy
                }
            }
        }]);
    }
}

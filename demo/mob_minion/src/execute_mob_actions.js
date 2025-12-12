/**
 * Execute Mob Actions Module
 * 
 * Implements the Execute Mob Actions sub-epic functionality for commanding mobs
 * and executing coordinated actions for all minions in a mob.
 */

/**
 * MobCommandHandler - Handles identification of mob from clicked token
 * 
 * Story: Click Mob Token To Command
 */
export class MobCommandHandler {
    /**
     * @param {Object} foundryTokenApi - Foundry VTT Token API dependency
     * @param {Object} foundryActorSystem - Foundry VTT Actor System dependency
     */
    constructor(foundryTokenApi, foundryActorSystem) {
        this.foundryTokenApi = foundryTokenApi;
        this.foundryActorSystem = foundryActorSystem;
    }

    /**
     * Identify mob associated with clicked token
     * 
     * Scenario: Game Master clicks mob token to command mob
     * 
     * @param {string} tokenId - ID of clicked token
     * @returns {Object|null} Mob entity if token belongs to mob, null otherwise
     */
    identifyMobFromToken(tokenId) {
        const token = this.foundryTokenApi.getTokenById(tokenId);
        
        if (!token) {
            return null;
        }

        const mobId = token.getFlag('mob-minion', 'mobId');
        
        if (!mobId) {
            return null; // Token doesn't belong to any mob
        }

        return this._getMobEntity(mobId);
    }

    /**
     * Prepare to execute action for all minions in mob
     * 
     * @param {Object} mobEntity - Mob entity to prepare
     * @returns {Object} Action preparation result with mob and minion tokens
     */
    prepareAction(mobEntity) {
        const minionTokens = mobEntity.tokenIds.map(tokenId => 
            this.foundryTokenApi.getTokenById(tokenId)
        ).filter(token => token !== null);

        return {
            mob: mobEntity,
            minionTokens: minionTokens,
            minionCount: minionTokens.length
        };
    }

    /**
     * Get mob entity from Foundry actor system
     * 
     * @private
     * @param {string} mobId - Mob entity ID
     * @returns {Object|null} Mob entity or null if not found
     */
    _getMobEntity(mobId) {
        const actors = this.foundryActorSystem.actors.filter(actor => 
            actor.getFlag('mob-minion', 'mobId') === mobId
        );

        if (actors.length === 0) {
            return null;
        }

        const actor = actors[0];
        return {
            id: actor.getFlag('mob-minion', 'mobId'),
            tokenIds: actor.getFlag('mob-minion', 'tokenIds') || [],
            actorIds: actor.getFlag('mob-minion', 'actorIds') || [],
            strategy: actor.getFlag('mob-minion', 'strategy') || null
        };
    }
}

/**
 * TargetSelector - Determines target based on mob's strategy
 * 
 * Story: Determine Target From Strategy
 */
export class TargetSelector {
    /**
     * @param {Object} foundryCombatSystem - Foundry VTT Combat System dependency
     */
    constructor(foundryCombatSystem) {
        this.foundryCombatSystem = foundryCombatSystem;
    }

    /**
     * Determine target using mob's assigned strategy
     * 
     * Scenario: System determines target using assigned strategy
     * 
     * @param {Object} mobEntity - Mob entity with assigned strategy
     * @returns {Object|null} Selected target enemy or null if none available
     */
    determineTargetFromStrategy(mobEntity) {
        const strategy = mobEntity.strategy || 'Default';
        const availableEnemies = this.foundryCombatSystem.getAvailableEnemies();

        if (availableEnemies.length === 0) {
            return null;
        }

        switch (strategy) {
            case 'AttackMostPowerful':
                return this._selectMostPowerfulTarget(availableEnemies);
            case 'AttackWeakest':
                return this._selectWeakestTarget(availableEnemies);
            case 'AttackMostDamaged':
                return this._selectMostDamagedTarget(availableEnemies);
            case 'DefendLeader':
                return this._selectLeaderTarget(availableEnemies);
            default:
                return this._selectDefaultTarget(availableEnemies);
        }
    }

    /**
     * Select most powerful target (highest power level)
     * 
     * @private
     * @param {Array<Object>} enemies - Available enemy entities
     * @returns {Object} Most powerful enemy
     */
    _selectMostPowerfulTarget(enemies) {
        return enemies.reduce((mostPowerful, enemy) => {
            const enemyPower = this._getEnemyPower(enemy);
            const mostPowerfulPower = this._getEnemyPower(mostPowerful);
            return enemyPower > mostPowerfulPower ? enemy : mostPowerful;
        }, enemies[0]);
    }

    /**
     * Select weakest target (lowest power level)
     * 
     * @private
     * @param {Array<Object>} enemies - Available enemy entities
     * @returns {Object} Weakest enemy
     */
    _selectWeakestTarget(enemies) {
        return enemies.reduce((weakest, enemy) => {
            const enemyPower = this._getEnemyPower(enemy);
            const weakestPower = this._getEnemyPower(weakest);
            return enemyPower < weakestPower ? enemy : weakest;
        }, enemies[0]);
    }

    /**
     * Select most damaged target (highest damage taken)
     * 
     * @private
     * @param {Array<Object>} enemies - Available enemy entities
     * @returns {Object} Most damaged enemy
     */
    _selectMostDamagedTarget(enemies) {
        return enemies.reduce((mostDamaged, enemy) => {
            const enemyDamage = this._getDamageTaken(enemy);
            const mostDamagedDamage = this._getDamageTaken(mostDamaged);
            return enemyDamage > mostDamagedDamage ? enemy : mostDamaged;
        }, enemies[0]);
    }

    /**
     * Select leader target (for defend leader strategy)
     * 
     * @private
     * @param {Array<Object>} enemies - Available enemy entities
     * @returns {Object} Leader enemy (first available)
     */
    _selectLeaderTarget(enemies) {
        // For now, return first enemy as leader
        // This can be enhanced based on specific leader identification logic
        return enemies[0];
    }

    /**
     * Select default target (nearest enemy or first available)
     * 
     * Scenario: System uses default strategy when no strategy assigned
     * 
     * @private
     * @param {Array<Object>} enemies - Available enemy entities
     * @returns {Object} Default target enemy
     */
    _selectDefaultTarget(enemies) {
        // Return first available enemy as default
        return enemies[0];
    }

    /**
     * Get enemy power level
     * 
     * @private
     * @param {Object} enemy - Enemy entity
     * @returns {number} Power level
     */
    _getEnemyPower(enemy) {
        return enemy.system?.attributes?.level?.value || 
               enemy.system?.details?.level || 
               1;
    }

    /**
     * Get damage taken by enemy
     * 
     * @private
     * @param {Object} enemy - Enemy entity
     * @returns {number} Damage taken
     */
    _getDamageTaken(enemy) {
        const maxHealth = enemy.system?.attributes?.hp?.max || 1;
        const currentHealth = enemy.system?.attributes?.hp?.value || maxHealth;
        return maxHealth - currentHealth;
    }
}

/**
 * AttackExecutor - Executes attack actions for all minions in mob
 * 
 * Story: Execute Attack Action
 */
export class AttackExecutor {
    /**
     * @param {Object} foundryCombatSystem - Foundry VTT Combat System dependency
     */
    constructor(foundryCombatSystem) {
        this.foundryCombatSystem = foundryCombatSystem;
    }

    /**
     * Execute attack for all minions in mob via Foundry combat system
     * 
     * Scenario: System executes attack for all minions in mob
     * 
     * @param {Object} actionPreparation - Action preparation result from MobCommandHandler
     * @param {Object} target - Target enemy entity
     * @returns {Array<Object>} Array of attack results for each minion
     */
    executeAttackAction(actionPreparation, target) {
        const { minionTokens } = actionPreparation;
        const attackResults = [];

        minionTokens.forEach(minionToken => {
            const attackResult = this._executeMinionAttack(minionToken, target);
            attackResults.push(attackResult);
        });

        return attackResults;
    }

    /**
     * Execute attack for a single minion
     * 
     * @private
     * @param {Object} minionToken - Minion token entity
     * @param {Object} target - Target enemy entity
     * @returns {Object} Attack result with hit/miss and damage
     */
    _executeMinionAttack(minionToken, target) {
        // Use Foundry combat system to execute attack
        const attackRoll = this.foundryCombatSystem.rollAttack(minionToken, target);
        const damageRoll = attackRoll.hit ? 
            this.foundryCombatSystem.rollDamage(minionToken, target) : 
            null;

        return {
            minionId: minionToken.id,
            targetId: target.id,
            hit: attackRoll.hit,
            damage: damageRoll?.total || 0
        };
    }
}

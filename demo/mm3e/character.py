"""
Character - M&M 3E Character with Abilities Configuration
Domain: Character creation and ability management for Mutants & Masterminds 3E
"""


class Ability:
    """Represents one of the 8 core abilities (STR, STA, AGL, DEX, FGT, INT, AWE, PRE)"""
    
    # Constants
    COST_PER_RANK = 2  # Power points per ability rank (M&M 3E Handbook p26)
    
    # Ability definitions
    ABILITIES = {
        'STR': {'name': 'Strength', 'description': 'Physical power, lifting, damage', 'primary_use': 'Athletics skill', 'category': 'Physical'},
        'STA': {'name': 'Stamina', 'description': 'Endurance, health, vitality', 'primary_use': 'Fortitude and Toughness', 'category': 'Physical'},
        'AGL': {'name': 'Agility', 'description': 'Balance, grace, reflexes', 'primary_use': 'Dodge, Acrobatics, Stealth', 'category': 'Reflexes'},
        'DEX': {'name': 'Dexterity', 'description': 'Coordination, accuracy, fine motor', 'primary_use': 'Sleight of Hand, ranged attacks', 'category': 'Reflexes'},
        'FGT': {'name': 'Fighting', 'description': 'Close combat skill, melee prowess', 'primary_use': 'Parry, Close Combat', 'category': 'Combat'},
        'INT': {'name': 'Intellect', 'description': 'Reasoning, knowledge, memory', 'primary_use': 'Investigation, Technology', 'category': 'Mental'},
        'AWE': {'name': 'Awareness', 'description': 'Perception, willpower, alertness', 'primary_use': 'Will, Perception, Insight', 'category': 'Mental'},
        'PRE': {'name': 'Presence', 'description': 'Personality, charisma, force of will', 'primary_use': 'Persuasion, Intimidation, Deception', 'category': 'Mental'},
    }
    
    # Rank descriptions
    RANK_DESCRIPTIONS = {
        -5: 'Far Below Average',
        -4: 'Below Average',
        -3: 'Below Average',
        -2: 'Below Average',
        -1: 'Below Average',
        0: 'Average',
        1: 'Above Average',
        2: 'Above Average',
        3: 'Exceptional',
        4: 'Exceptional',
        5: 'Peak Human',
        6: 'Peak Human',
        7: 'Peak Human',
        8: 'Superhuman',
        9: 'Superhuman',
        10: 'Superhuman',
        11: 'Superhuman',
        12: 'Superhuman',
        13: 'Superhuman',
        14: 'Superhuman',
        15: 'Superhuman',
        16: 'Superhuman',
        17: 'Superhuman',
        18: 'Superhuman',
        19: 'Superhuman',
        20: 'Cosmic-level',
    }
    
    def __init__(self, abbreviation, rank=0):
        self.abbreviation = abbreviation
        self._rank = rank
        self._info = self.ABILITIES[abbreviation]
    
    @property
    def full_name(self):
        return self._info['name']
    
    @property
    def rank(self):
        return self._rank
    
    @rank.setter
    def rank(self, value):
        self._rank = value
    
    @property
    def cost(self):
        """Cost = Rank × 2"""
        return self._rank * self.COST_PER_RANK
    
    @property
    def rank_description(self):
        """Get rank description (e.g., Average, Peak Human, Superhuman)"""
        return self.RANK_DESCRIPTIONS.get(self._rank, 'Unknown')
    
    @property
    def can_be_adjusted(self):
        """All abilities can be adjusted"""
        return True
    
    @property
    def has_warning_style(self):
        """Warning style for negative ranks"""
        return self._rank < 0
    
    @property
    def is_displayed(self):
        """Abilities are always displayed"""
        return True
    
    @property
    def description(self):
        return self._info['description']
    
    @property
    def primary_use(self):
        return self._info['primary_use']
    
    @property
    def example_usage(self):
        """Example usage based on ability type"""
        examples = {
            'STR': 'Lifting heavy objects, breaking things',
            'STA': 'Resisting poison, enduring fatigue',
            'AGL': 'Dodging attacks, maintaining balance',
            'DEX': 'Aiming ranged weapons, picking locks',
            'FGT': 'Hand-to-hand combat, parrying attacks',
            'INT': 'Solving puzzles, recalling information',
            'AWE': 'Noticing hidden threats, resisting mind control',
            'PRE': 'Persuading others, intimidating foes',
        }
        return examples.get(self.abbreviation, 'Various uses')
    
    @property
    def category(self):
        return self._info['category']


class Defense:
    """Represents a defense value (Dodge, Parry, Fortitude, Will, Toughness)"""
    
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.is_updated = True


class BudgetStatus:
    """Represents budget status information"""
    
    def __init__(self, spent, total):
        self.spent = spent
        self.total = total
        self.remaining = total - spent
        self.is_fully_used = (spent == total)
        self.is_overspending = (spent > total)
        
        if self.is_overspending:
            self.color = 'warning'
            overspend_amount = spent - total
            self.message = f'Over Budget by {overspend_amount} points'
        elif self.is_fully_used:
            self.color = 'normal'
            self.message = 'Budget Fully Used'
        else:
            self.color = 'normal'
            self.message = 'Within Budget'


class BudgetProgress:
    """Represents budget progress bar information"""
    
    def __init__(self, spent, total):
        self.spent = spent
        self.total = total
        self.percentage = int((spent / total) * 100) if total > 0 else 0


class Character:
    """M&M 3E Character with abilities configuration"""
    
    # Constants
    POINTS_PER_POWER_LEVEL = 15  # Starting points formula: PL × 15 (M&M 3E Handbook p26)
    ACTIVE_DEFENSE_BASE = 10      # Active defenses (Dodge, Parry) base value (M&M 3E Handbook p110)
    
    # Ability order
    ABILITY_ORDER = ['STR', 'STA', 'AGL', 'DEX', 'FGT', 'INT', 'AWE', 'PRE']
    
    def __init__(self, power_level=10):
        self.power_level = power_level
        self.total_budget = power_level * self.POINTS_PER_POWER_LEVEL
        
        # Initialize all 8 abilities at rank 0
        self._abilities = {abbr: Ability(abbr, 0) for abbr in self.ABILITY_ORDER}
        
        # Initialize defenses
        self._defenses = {
            'Dodge': Defense('Dodge', self.ACTIVE_DEFENSE_BASE),
            'Parry': Defense('Parry', self.ACTIVE_DEFENSE_BASE),
            'Fortitude': Defense('Fortitude', 0),
            'Toughness': Defense('Toughness', 0),
            'Will': Defense('Will', 0),
        }
    
    def set_ability_rank(self, ability_abbr, rank):
        """Set ability rank and trigger defense cascade updates"""
        ability = self._abilities[ability_abbr]
        ability.rank = rank
        
        # Cascade to defenses
        self._update_defenses_from_ability(ability_abbr, rank)
    
    def _update_defenses_from_ability(self, ability_abbr, rank):
        """Update defenses based on ability changes"""
        if ability_abbr == 'AGL':
            # Agility → Dodge (10 + Agility)
            self._defenses['Dodge'] = Defense('Dodge', self.ACTIVE_DEFENSE_BASE + rank)
        elif ability_abbr == 'FGT':
            # Fighting → Parry (10 + Fighting)
            self._defenses['Parry'] = Defense('Parry', self.ACTIVE_DEFENSE_BASE + rank)
        elif ability_abbr == 'STA':
            # Stamina → Fortitude and Toughness (both equal Stamina)
            self._defenses['Fortitude'] = Defense('Fortitude', rank)
            self._defenses['Toughness'] = Defense('Toughness', rank)
        elif ability_abbr == 'AWE':
            # Awareness → Will
            self._defenses['Will'] = Defense('Will', rank)
        # STR, DEX, INT, PRE don't affect defenses
    
    def get_abilities(self):
        """Get all 8 abilities in standard order"""
        return [self._abilities[abbr] for abbr in self.ABILITY_ORDER]
    
    def get_ability(self, abbreviation):
        """Get single ability by abbreviation"""
        return self._abilities[abbreviation]
    
    def get_abilities_by_category(self):
        """Get abilities grouped by category"""
        categories = {
            'Physical': [],
            'Reflexes': [],
            'Combat': [],
            'Mental': [],
        }
        
        for ability in self.get_abilities():
            categories[ability.category].append(ability)
        
        return categories
    
    def get_total_ability_points(self):
        """Calculate total ability points spent (sum of all ability costs)"""
        return sum(ability.cost for ability in self._abilities.values())
    
    def get_ability_points_display(self):
        """Get display string for ability points"""
        total = self.get_total_ability_points()
        return f'Ability Points: {total} / {self.total_budget}'
    
    def get_ability_points_breakdown(self):
        """Get breakdown of ability points by ability"""
        breakdown = {}
        for abbr, ability in self._abilities.items():
            if ability.cost != 0:
                breakdown[abbr] = ability.cost
        breakdown['Total'] = self.get_total_ability_points()
        return breakdown
    
    def get_defense(self, name):
        """Get defense by name"""
        return self._defenses[name]
    
    @property
    def remaining_budget(self):
        """Calculate remaining budget (total - spent)"""
        spent = self.get_total_ability_points()
        return self.total_budget - spent
    
    def get_budget_display(self):
        """Get budget display string"""
        spent = self.get_total_ability_points()
        return f'{spent} / {self.total_budget} points spent'
    
    def get_budget_status(self):
        """Get budget status object"""
        spent = self.get_total_ability_points()
        return BudgetStatus(spent, self.total_budget)
    
    def get_budget_progress(self):
        """Get budget progress object"""
        spent = self.get_total_ability_points()
        return BudgetProgress(spent, self.total_budget)
    
    def get_overspend_amount(self):
        """Get amount over budget (negative if under budget)"""
        spent = self.get_total_ability_points()
        overspend = spent - self.total_budget
        return overspend if overspend > 0 else 0
    
    def can_be_saved(self):
        """Character can always be saved (warn, don't prevent philosophy)"""
        return True



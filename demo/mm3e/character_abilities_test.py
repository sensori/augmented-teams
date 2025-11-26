"""
BDD Tests for Character Abilities Configuration
Phase: TEST IMPLEMENTATION (Stage 2 - COMPLETE)
Domain: Character with abilities being configured

Total Tests: 66 (all implemented)
- Display Abilities: 18 tests
- Set Ability Ranks: 15 tests
- Calculate Total Points: 11 tests
- Update Dependent Defenses: 10 tests
- Update Point Budget: 12 tests
"""

from mamba import description, context, it, before
from expects import expect, equal, be_true, be_false, have_length, be_none, be_above, be_below


# Helper: Create character with abilities
def create_character_with_abilities(power_level=10, ability_ranks=None):
    """Factory function to create a character with configured abilities"""
    import sys
    import os
    
    # Add demo/mm3e to path so we can import character module
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)
    
    from character import Character
    
    character = Character(power_level=power_level)
    
    if ability_ranks:
        for ability_name, rank in ability_ranks.items():
            character.set_ability_rank(ability_name, rank)
    
    return character


with description('a character whose abilities are being configured'):
    
    with context('with abilities'):
        with context('that are being displayed'):
            
            with it('should have all 8 abilities shown in standard order'):
                # Arrange
                character = create_character_with_abilities()
                
                # Act
                abilities = character.get_abilities()
                
                # Assert
                expect(abilities).to(have_length(8))
                ability_names = [ability.abbreviation for ability in abilities]
                expect(ability_names).to(equal(['STR', 'STA', 'AGL', 'DEX', 'FGT', 'INT', 'AWE', 'PRE']))
            
            with it('should have each ability showing abbreviation and full name'):
                # Arrange
                character = create_character_with_abilities()
                
                # Act
                abilities = character.get_abilities()
                
                # Assert
                first_ability = abilities[0]
                expect(first_ability.abbreviation).to(equal('STR'))
                expect(first_ability.full_name).to(equal('Strength'))
            
            with it('should have each ability showing current rank'):
                # Arrange
                character = create_character_with_abilities(ability_ranks={'STR': 5})
                
                # Act
                str_ability = character.get_ability('STR')
                
                # Assert
                expect(str_ability.rank).to(equal(5))
            
            with it('should have each ability showing calculated cost'):
                # Arrange
                character = create_character_with_abilities(ability_ranks={'STR': 5})
                
                # Act
                str_ability = character.get_ability('STR')
                
                # Assert
                expect(str_ability.cost).to(equal(10))
            
            with it('should have abilities grouped by category'):
                # Arrange
                character = create_character_with_abilities()
                
                # Act
                grouped = character.get_abilities_by_category()
                
                # Assert
                expect(grouped['Physical']).to(have_length(2))
                expect(grouped['Reflexes']).to(have_length(2))
                expect(grouped['Combat']).to(have_length(1))
                expect(grouped['Mental']).to(have_length(3))
            
            with context('at default ranks'):
                
                with it('should have all abilities showing rank 0 as average'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    abilities = character.get_abilities()
                    
                    # Assert
                    for ability in abilities:
                        expect(ability.rank).to(equal(0))
                        expect(ability.rank_description).to(equal('Average'))
                
                with it('should have all abilities showing zero cost'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    abilities = character.get_abilities()
                    
                    # Assert
                    for ability in abilities:
                        expect(ability.cost).to(equal(0))
                
                with it('should have rank adjustment controls displayed'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    abilities = character.get_abilities()
                    
                    # Assert
                    for ability in abilities:
                        expect(ability.can_be_adjusted).to(be_true)
            
            with context('with positive ranks'):
                
                with it('should have rank displayed with calculated cost'):
                    # Arrange
                    character = create_character_with_abilities(ability_ranks={'STR': 6})
                    
                    # Act
                    str_ability = character.get_ability('STR')
                    
                    # Assert
                    expect(str_ability.rank).to(equal(6))
                    expect(str_ability.cost).to(equal(12))
                
                with it('should have rank description shown'):
                    # Arrange
                    character = create_character_with_abilities(ability_ranks={'STR': 6})
                    
                    # Act
                    str_ability = character.get_ability('STR')
                    
                    # Assert
                    expect(str_ability.rank_description).to(equal('Peak Human'))
                
                with it('should have superhuman designation shown when rank is 8 or higher'):
                    # Arrange
                    character = create_character_with_abilities(ability_ranks={'STR': 8})
                    
                    # Act
                    str_ability = character.get_ability('STR')
                    
                    # Assert
                    expect(str_ability.rank_description).to(equal('Superhuman'))
            
            with context('with negative ranks'):
                
                with it('should have negative rank displayed in warning style'):
                    # Arrange
                    character = create_character_with_abilities(ability_ranks={'DEX': -2})
                    
                    # Act
                    dex_ability = character.get_ability('DEX')
                    
                    # Assert
                    expect(dex_ability.rank).to(equal(-2))
                    expect(dex_ability.has_warning_style).to(be_true)
                
                with it('should have refund shown as negative cost'):
                    # Arrange
                    character = create_character_with_abilities(ability_ranks={'DEX': -2})
                    
                    # Act
                    dex_ability = character.get_ability('DEX')
                    
                    # Assert
                    expect(dex_ability.cost).to(equal(-4))
                
                with it('should have below average designation shown'):
                    # Arrange
                    character = create_character_with_abilities(ability_ranks={'DEX': -2})
                    
                    # Act
                    dex_ability = character.get_ability('DEX')
                    
                    # Assert
                    expect(dex_ability.rank_description).to(equal('Below Average'))
            
            with context('with tooltips'):
                
                with it('should have ability description shown on hover'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    str_ability = character.get_ability('STR')
                    
                    # Assert
                    expect(str_ability.description).to(equal('Physical power, lifting, damage'))
                
                with it('should have primary use shown on hover'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    str_ability = character.get_ability('STR')
                    
                    # Assert
                    expect(str_ability.primary_use).to(equal('Athletics skill'))
                
                with it('should have example usage shown on hover'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    str_ability = character.get_ability('STR')
                    
                    # Assert
                    expect(str_ability.example_usage).not_to(be_none)
        
        with context('with ranks that are being set'):
            
            with context('that has been set to positive rank'):
                
                with it('should have cost calculated using rank times 2 formula'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    character.set_ability_rank('STR', 5)
                    
                    # Assert
                    str_ability = character.get_ability('STR')
                    expect(str_ability.cost).to(equal(10))  # 5 * 2
                
                with it('should have points deducted from remaining budget'):
                    # Arrange
                    character = create_character_with_abilities(power_level=10)
                    initial_budget = character.remaining_budget
                    
                    # Act
                    character.set_ability_rank('STR', 5)
                    
                    # Assert
                    expect(character.remaining_budget).to(equal(initial_budget - 10))
                
                with it('should have new rank value stored with character'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    character.set_ability_rank('STR', 5)
                    
                    # Assert
                    str_ability = character.get_ability('STR')
                    expect(str_ability.rank).to(equal(5))
                
                with it('should have rank displayed immediately'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    character.set_ability_rank('STR', 5)
                    str_ability = character.get_ability('STR')
                    
                    # Assert
                    expect(str_ability.rank).to(equal(5))
                    expect(str_ability.is_displayed).to(be_true)
            
            with context('that has been set to zero'):
                
                with it('should have cost calculated as zero'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    character.set_ability_rank('INT', 0)
                    
                    # Assert
                    int_ability = character.get_ability('INT')
                    expect(int_ability.cost).to(equal(0))
                
                with it('should have no points deducted from budget'):
                    # Arrange
                    character = create_character_with_abilities(power_level=10)
                    initial_budget = character.remaining_budget
                    
                    # Act
                    character.set_ability_rank('INT', 0)
                    
                    # Assert
                    expect(character.remaining_budget).to(equal(initial_budget))
                
                with it('should have average designation displayed'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    character.set_ability_rank('INT', 0)
                    
                    # Assert
                    int_ability = character.get_ability('INT')
                    expect(int_ability.rank_description).to(equal('Average'))
            
            with context('that has been set to negative rank'):
                
                with it('should have cost calculated as negative value'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    character.set_ability_rank('DEX', -2)
                    
                    # Assert
                    dex_ability = character.get_ability('DEX')
                    expect(dex_ability.cost).to(equal(-4))  # -2 * 2
                
                with it('should have points refunded to budget'):
                    # Arrange
                    character = create_character_with_abilities(power_level=10)
                    initial_budget = character.remaining_budget
                    
                    # Act
                    character.set_ability_rank('DEX', -2)
                    
                    # Assert
                    expect(character.remaining_budget).to(equal(initial_budget + 4))
                
                with it('should have warning style applied'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    character.set_ability_rank('DEX', -2)
                    
                    # Assert
                    dex_ability = character.get_ability('DEX')
                    expect(dex_ability.has_warning_style).to(be_true)
                
                with it('should have below average designation displayed'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    character.set_ability_rank('DEX', -2)
                    
                    # Assert
                    dex_ability = character.get_ability('DEX')
                    expect(dex_ability.rank_description).to(equal('Below Average'))
            
            with context('that has been changed from existing rank'):
                
                with it('should have cost recalculated for new rank'):
                    # Arrange
                    character = create_character_with_abilities(ability_ranks={'AGL': 3})
                    
                    # Act
                    character.set_ability_rank('AGL', 8)
                    
                    # Assert
                    agl_ability = character.get_ability('AGL')
                    expect(agl_ability.cost).to(equal(16))  # 8 * 2
                
                with it('should have point difference adjusted in budget'):
                    # Arrange
                    character = create_character_with_abilities(power_level=10, ability_ranks={'AGL': 3})
                    budget_after_first = character.remaining_budget
                    
                    # Act
                    character.set_ability_rank('AGL', 8)
                    
                    # Assert
                    # Changed from 3 (6pp) to 8 (16pp), so 10 more points deducted
                    expect(character.remaining_budget).to(equal(budget_after_first - 10))
                
                with it('should have display updated to new rank'):
                    # Arrange
                    character = create_character_with_abilities(ability_ranks={'AGL': 3})
                    
                    # Act
                    character.set_ability_rank('AGL', 8)
                    
                    # Assert
                    agl_ability = character.get_ability('AGL')
                    expect(agl_ability.rank).to(equal(8))
                
                with it('should have update completed within 100ms'):
                    # Arrange
                    import time
                    character = create_character_with_abilities(ability_ranks={'FGT': 10})
                    
                    # Act
                    start_time = time.time()
                    character.set_ability_rank('FGT', 6)
                    elapsed = (time.time() - start_time) * 1000  # Convert to ms
                    
                    # Assert
                    expect(elapsed).to(be_below(100))
            
            with context('that has been set to minimum rank'):
                
                with it('should have minimum rank of negative 5 accepted'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    character.set_ability_rank('PRE', -5)
                    
                    # Assert
                    pre_ability = character.get_ability('PRE')
                    expect(pre_ability.rank).to(equal(-5))
                
                with it('should have 10 points refunded to budget'):
                    # Arrange
                    character = create_character_with_abilities(power_level=10)
                    initial_budget = character.remaining_budget
                    
                    # Act
                    character.set_ability_rank('PRE', -5)
                    
                    # Assert
                    expect(character.remaining_budget).to(equal(initial_budget + 10))  # -5 * 2 = -10 (refund)
                
                with it('should have far below average designation shown'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    character.set_ability_rank('PRE', -5)
                    
                    # Assert
                    pre_ability = character.get_ability('PRE')
                    expect(pre_ability.rank_description).to(equal('Far Below Average'))
            
            with context('that has been set to maximum rank'):
                
                with it('should have maximum rank of 20 accepted'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    character.set_ability_rank('STA', 20)
                    
                    # Assert
                    sta_ability = character.get_ability('STA')
                    expect(sta_ability.rank).to(equal(20))
                
                with it('should have 40 points deducted from budget'):
                    # Arrange
                    character = create_character_with_abilities(power_level=10)
                    initial_budget = character.remaining_budget
                    
                    # Act
                    character.set_ability_rank('STA', 20)
                    
                    # Assert
                    expect(character.remaining_budget).to(equal(initial_budget - 40))  # 20 * 2
                
                with it('should have cosmic-level designation shown'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    character.set_ability_rank('STA', 20)
                    
                    # Assert
                    sta_ability = character.get_ability('STA')
                    expect(sta_ability.rank_description).to(equal('Cosmic-level'))
        
        with context('with total ability points being calculated'):
            
            with context('with all abilities at zero'):
                
                with it('should have total calculated as 0 points'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    total = character.get_total_ability_points()
                    
                    # Assert
                    expect(total).to(equal(0))
                
                with it('should have display showing 0 spent'):
                    # Arrange
                    character = create_character_with_abilities()
                    
                    # Act
                    display_text = character.get_ability_points_display()
                    
                    # Assert
                    expect(display_text).to(equal('Ability Points: 0 / 150'))
                
                with it('should have no points deducted from budget'):
                    # Arrange
                    character = create_character_with_abilities(power_level=10)
                    initial_budget = 150  # PL 10 = 150 points
                    
                    # Act
                    remaining = character.remaining_budget
                    
                    # Assert
                    expect(remaining).to(equal(initial_budget))
            
            with context('with single ability set'):
                
                with it('should have total equal to single ability cost'):
                    # Arrange
                    character = create_character_with_abilities(ability_ranks={'STR': 5})
                    
                    # Act
                    total = character.get_total_ability_points()
                    
                    # Assert
                    expect(total).to(equal(10))  # 5 * 2
                
                with it('should have breakdown showing ability contribution'):
                    # Arrange
                    character = create_character_with_abilities(ability_ranks={'STR': 5})
                    
                    # Act
                    breakdown = character.get_ability_points_breakdown()
                    
                    # Assert
                    expect(breakdown['STR']).to(equal(10))
                    expect(breakdown['Total']).to(equal(10))
            
            with context('with multiple abilities set'):
                
                with it('should have total equal to sum of all ability costs'):
                    # Arrange
                    character = create_character_with_abilities(ability_ranks={
                        'STR': 5,  # 10pp
                        'STA': 3   # 6pp
                    })
                    
                    # Act
                    total = character.get_total_ability_points()
                    
                    # Assert
                    expect(total).to(equal(16))
                
                with it('should have breakdown showing each ability contribution'):
                    # Arrange
                    character = create_character_with_abilities(ability_ranks={
                        'STR': 5,
                        'STA': 3
                    })
                    
                    # Act
                    breakdown = character.get_ability_points_breakdown()
                    
                    # Assert
                    expect(breakdown['STR']).to(equal(10))
                    expect(breakdown['STA']).to(equal(6))
                    expect(breakdown['Total']).to(equal(16))
                
                with it('should have formula validated as sum of rank times 2 for all 8'):
                    # Arrange
                    ranks = {'STR': 5, 'STA': 3, 'AGL': 2, 'DEX': 1, 'FGT': 4, 'INT': 2, 'AWE': 3, 'PRE': 2}
                    character = create_character_with_abilities(ability_ranks=ranks)
                    
                    # Act
                    total = character.get_total_ability_points()
                    manual_sum = sum(rank * 2 for rank in ranks.values())
                    
                    # Assert
                    expect(total).to(equal(manual_sum))
                    expect(total).to(equal(44))  # (5+3+2+1+4+2+3+2)*2
            
            with context('with negative ranks'):
                
                with it('should have negative costs reducing total'):
                    # Arrange
                    character = create_character_with_abilities(ability_ranks={
                        'STR': 5,   # 10pp
                        'DEX': -2   # -4pp
                    })
                    
                    # Act
                    total = character.get_total_ability_points()
                    
                    # Assert
                    expect(total).to(equal(6))  # 10 + (-4)
                
                with it('should have refunds shown in breakdown'):
                    # Arrange
                    character = create_character_with_abilities(ability_ranks={
                        'STR': 5,
                        'DEX': -2
                    })
                    
                    # Act
                    breakdown = character.get_ability_points_breakdown()
                    
                    # Assert
                    expect(breakdown['STR']).to(equal(10))
                    expect(breakdown['DEX']).to(equal(-4))
                    expect(breakdown['Total']).to(equal(6))
            
            with context('that is recalculating after ability changes'):
                
                with it('should have total updated immediately'):
                    # Arrange
                    character = create_character_with_abilities(ability_ranks={'STR': 5, 'STA': 3})
                    initial_total = character.get_total_ability_points()
                    
                    # Act
                    character.set_ability_rank('AGL', 4)
                    new_total = character.get_total_ability_points()
                    
                    # Assert
                    expect(new_total).to(equal(initial_total + 8))
                    expect(new_total).to(equal(24))  # 10 + 6 + 8
                
                with it('should have update completed within 100ms'):
                    # Arrange
                    import time
                    character = create_character_with_abilities(ability_ranks={'STR': 5, 'STA': 3})
                    
                    # Act
                    start_time = time.time()
                    character.set_ability_rank('AGL', 4)
                    total = character.get_total_ability_points()
                    elapsed = (time.time() - start_time) * 1000
                    
                    # Assert
                    expect(elapsed).to(be_below(100))
                
                with it('should have new breakdown displayed'):
                    # Arrange
                    character = create_character_with_abilities(ability_ranks={'STR': 5, 'STA': 3})
                    
                    # Act
                    character.set_ability_rank('AGL', 4)
                    breakdown = character.get_ability_points_breakdown()
                    
                    # Assert
                    expect(breakdown['STR']).to(equal(10))
                    expect(breakdown['STA']).to(equal(6))
                    expect(breakdown['AGL']).to(equal(8))
                    expect(breakdown['Total']).to(equal(24))
        
        with context('whose Agility has changed'):
            
            with it('should have Dodge recalculated as 10 plus Agility'):
                # Arrange
                character = create_character_with_abilities()
                
                # Act
                character.set_ability_rank('AGL', 5)
                
                # Assert
                dodge = character.get_defense('Dodge')
                expect(dodge.value).to(equal(15))  # 10 + 5
            
            with it('should have Dodge display updated synchronously'):
                # Arrange
                character = create_character_with_abilities()
                
                # Act
                character.set_ability_rank('AGL', 5)
                dodge = character.get_defense('Dodge')
                
                # Assert
                expect(dodge.is_updated).to(be_true)
            
            with it('should have both Agility and Dodge changed simultaneously'):
                # Arrange
                character = create_character_with_abilities()
                
                # Act
                character.set_ability_rank('AGL', 5)
                agility = character.get_ability('AGL')
                dodge = character.get_defense('Dodge')
                
                # Assert
                expect(agility.rank).to(equal(5))
                expect(dodge.value).to(equal(15))
        
        with context('whose Fighting has changed'):
            
            with it('should have Parry recalculated as 10 plus Fighting'):
                # Arrange
                character = create_character_with_abilities()
                
                # Act
                character.set_ability_rank('FGT', 8)
                
                # Assert
                parry = character.get_defense('Parry')
                expect(parry.value).to(equal(18))  # 10 + 8
            
            with it('should have Parry display updated synchronously'):
                # Arrange
                character = create_character_with_abilities()
                
                # Act
                character.set_ability_rank('FGT', 8)
                parry = character.get_defense('Parry')
                
                # Assert
                expect(parry.is_updated).to(be_true)
            
            with it('should have both Fighting and Parry changed simultaneously'):
                # Arrange
                character = create_character_with_abilities()
                
                # Act
                character.set_ability_rank('FGT', 8)
                fighting = character.get_ability('FGT')
                parry = character.get_defense('Parry')
                
                # Assert
                expect(fighting.rank).to(equal(8))
                expect(parry.value).to(equal(18))
        
        with context('whose Stamina has changed'):
            
            with it('should have Fortitude recalculated equal to Stamina'):
                # Arrange
                character = create_character_with_abilities()
                
                # Act
                character.set_ability_rank('STA', 3)
                
                # Assert
                fortitude = character.get_defense('Fortitude')
                expect(fortitude.value).to(equal(3))
            
            with it('should have Toughness recalculated equal to Stamina'):
                # Arrange
                character = create_character_with_abilities()
                
                # Act
                character.set_ability_rank('STA', 3)
                
                # Assert
                toughness = character.get_defense('Toughness')
                expect(toughness.value).to(equal(3))
            
            with it('should have both defenses updated together in same cycle'):
                # Arrange
                character = create_character_with_abilities()
                
                # Act
                character.set_ability_rank('STA', 3)
                fortitude = character.get_defense('Fortitude')
                toughness = character.get_defense('Toughness')
                
                # Assert
                expect(fortitude.value).to(equal(3))
                expect(toughness.value).to(equal(3))
                expect(fortitude.is_updated).to(be_true)
                expect(toughness.is_updated).to(be_true)
            
            with it('should have Stamina Fortitude and Toughness all changed simultaneously'):
                # Arrange
                character = create_character_with_abilities()
                
                # Act
                character.set_ability_rank('STA', 3)
                stamina = character.get_ability('STA')
                fortitude = character.get_defense('Fortitude')
                toughness = character.get_defense('Toughness')
                
                # Assert
                expect(stamina.rank).to(equal(3))
                expect(fortitude.value).to(equal(3))
                expect(toughness.value).to(equal(3))
        
        with context('whose Awareness has changed'):
            
            with it('should have Will recalculated equal to Awareness'):
                # Arrange
                character = create_character_with_abilities()
                
                # Act
                character.set_ability_rank('AWE', 2)
                
                # Assert
                will_defense = character.get_defense('Will')
                expect(will_defense.value).to(equal(2))
            
            with it('should have Will display updated synchronously'):
                # Arrange
                character = create_character_with_abilities()
                
                # Act
                character.set_ability_rank('AWE', 2)
                will_defense = character.get_defense('Will')
                
                # Assert
                expect(will_defense.is_updated).to(be_true)
            
            with it('should have both Awareness and Will changed simultaneously'):
                # Arrange
                character = create_character_with_abilities()
                
                # Act
                character.set_ability_rank('AWE', 2)
                awareness = character.get_ability('AWE')
                will_defense = character.get_defense('Will')
                
                # Assert
                expect(awareness.rank).to(equal(2))
                expect(will_defense.value).to(equal(2))
        
        with context('whose ability has been decreased'):
            
            with it('should have defense value decreased when linked ability decreased'):
                # Arrange
                character = create_character_with_abilities(ability_ranks={'AGL': 8})
                initial_dodge = character.get_defense('Dodge').value
                
                # Act
                character.set_ability_rank('AGL', 3)
                
                # Assert
                new_dodge = character.get_defense('Dodge').value
                expect(new_dodge).to(equal(13))  # 10 + 3
                expect(new_dodge).to(be_below(initial_dodge))
            
            with it('should have update completed immediately'):
                # Arrange
                import time
                character = create_character_with_abilities(ability_ranks={'AGL': 8})
                
                # Act
                start_time = time.time()
                character.set_ability_rank('AGL', 3)
                dodge = character.get_defense('Dodge')
                elapsed = (time.time() - start_time) * 1000
                
                # Assert
                expect(elapsed).to(be_below(100))
        
        with context('whose ability has been reset to zero'):
            
            with it('should have defense returned to base value'):
                # Arrange
                character = create_character_with_abilities(ability_ranks={'FGT': 10})
                
                # Act
                character.set_ability_rank('FGT', 0)
                
                # Assert
                parry = character.get_defense('Parry')
                expect(parry.value).to(equal(10))  # 10 + 0 (base)
            
            with it('should have update completed immediately'):
                # Arrange
                import time
                character = create_character_with_abilities(ability_ranks={'FGT': 10})
                
                # Act
                start_time = time.time()
                character.set_ability_rank('FGT', 0)
                parry = character.get_defense('Parry')
                elapsed = (time.time() - start_time) * 1000
                
                # Assert
                expect(elapsed).to(be_below(100))
    
    with context('with remaining point budget being updated'):
        
        with context('with initial budget and no points spent'):
            
            with it('should have 150 points available for Power Level 10'):
                # Arrange & Act
                character = create_character_with_abilities(power_level=10)
                
                # Assert
                expect(character.total_budget).to(equal(150))
                expect(character.remaining_budget).to(equal(150))
            
            with it('should have budget shown as 0 spent of 150'):
                # Arrange
                character = create_character_with_abilities(power_level=10)
                
                # Act
                budget_display = character.get_budget_display()
                
                # Assert
                expect(budget_display).to(equal('0 / 150 points spent'))
            
            with it('should have normal color displayed'):
                # Arrange
                character = create_character_with_abilities(power_level=10)
                
                # Act
                budget_status = character.get_budget_status()
                
                # Assert
                expect(budget_status.color).to(equal('normal'))
            
            with it('should have progress bar showing 0 percent filled'):
                # Arrange
                character = create_character_with_abilities(power_level=10)
                
                # Act
                progress = character.get_budget_progress()
                
                # Assert
                expect(progress.percentage).to(equal(0))
        
        with context('that has ability points spent'):
            
            with it('should have remaining budget decreased by ability cost'):
                # Arrange
                character = create_character_with_abilities(power_level=10)
                initial_budget = character.remaining_budget
                
                # Act
                character.set_ability_rank('STR', 5)
                
                # Assert
                expect(character.remaining_budget).to(equal(initial_budget - 10))
                expect(character.remaining_budget).to(equal(140))
            
            with it('should have budget display updated immediately'):
                # Arrange
                character = create_character_with_abilities(power_level=10)
                
                # Act
                character.set_ability_rank('STR', 5)
                budget_display = character.get_budget_display()
                
                # Assert
                expect(budget_display).to(equal('10 / 150 points spent'))
            
            with it('should have update completed within 100ms'):
                # Arrange
                import time
                character = create_character_with_abilities(power_level=10)
                
                # Act
                start_time = time.time()
                character.set_ability_rank('STR', 5)
                budget = character.remaining_budget
                elapsed = (time.time() - start_time) * 1000
                
                # Assert
                expect(elapsed).to(be_below(100))
        
        with context('that has points refunded'):
            
            with it('should have remaining budget increased by refund amount'):
                # Arrange
                character = create_character_with_abilities(power_level=10)
                initial_budget = character.remaining_budget
                
                # Act
                character.set_ability_rank('DEX', -2)
                
                # Assert
                expect(character.remaining_budget).to(equal(initial_budget + 4))
                expect(character.remaining_budget).to(equal(154))
            
            with it('should have budget recalculated with negative rank cost'):
                # Arrange
                character = create_character_with_abilities(power_level=10, ability_ranks={'STR': 5})
                
                # Act
                character.set_ability_rank('DEX', -2)
                budget_display = character.get_budget_display()
                
                # Assert
                expect(budget_display).to(equal('6 / 150 points spent'))  # 10 - 4
        
        with context('with budget fully used'):
            
            with it('should have 150 of 150 shown when all points allocated'):
                # Arrange
                # Create character with abilities totaling 150 points
                ranks = {'STR': 10, 'STA': 10, 'AGL': 10, 'DEX': 10, 'FGT': 10, 'INT': 10, 'AWE': 10, 'PRE': 5}
                character = create_character_with_abilities(power_level=10, ability_ranks=ranks)
                
                # Act
                budget_display = character.get_budget_display()
                
                # Assert
                expect(character.get_total_ability_points()).to(equal(150))
                expect(budget_display).to(equal('150 / 150 points spent'))
            
            with it('should have budget fully used indicator displayed'):
                # Arrange
                ranks = {'STR': 10, 'STA': 10, 'AGL': 10, 'DEX': 10, 'FGT': 10, 'INT': 10, 'AWE': 10, 'PRE': 5}
                character = create_character_with_abilities(power_level=10, ability_ranks=ranks)
                
                # Act
                budget_status = character.get_budget_status()
                
                # Assert
                expect(budget_status.is_fully_used).to(be_true)
            
            with it('should have progress bar showing 100 percent filled'):
                # Arrange
                ranks = {'STR': 10, 'STA': 10, 'AGL': 10, 'DEX': 10, 'FGT': 10, 'INT': 10, 'AWE': 10, 'PRE': 5}
                character = create_character_with_abilities(power_level=10, ability_ranks=ranks)
                
                # Act
                progress = character.get_budget_progress()
                
                # Assert
                expect(progress.percentage).to(equal(100))
            
            with it('should have normal color maintained as valid state'):
                # Arrange
                ranks = {'STR': 10, 'STA': 10, 'AGL': 10, 'DEX': 10, 'FGT': 10, 'INT': 10, 'AWE': 10, 'PRE': 5}
                character = create_character_with_abilities(power_level=10, ability_ranks=ranks)
                
                # Act
                budget_status = character.get_budget_status()
                
                # Assert
                expect(budget_status.color).to(equal('normal'))
        
        with context('that is overspending'):
            
            with it('should have overspend amount calculated as spent minus total'):
                # Arrange
                # Create character with 156 points spent (6 over budget)
                # Total ranks = 78, cost = 78 * 2 = 156
                ranks = {'STR': 10, 'STA': 10, 'AGL': 10, 'DEX': 10, 'FGT': 10, 'INT': 10, 'AWE': 10, 'PRE': 8}
                character = create_character_with_abilities(power_level=10, ability_ranks=ranks)
                
                # Act
                overspend = character.get_overspend_amount()
                
                # Assert
                expect(overspend).to(equal(6))  # 156 - 150
            
            with it('should have over budget message displayed in warning color'):
                # Arrange
                ranks = {'STR': 10, 'STA': 10, 'AGL': 10, 'DEX': 10, 'FGT': 10, 'INT': 10, 'AWE': 10, 'PRE': 8}
                character = create_character_with_abilities(power_level=10, ability_ranks=ranks)
                
                # Act
                budget_status = character.get_budget_status()
                
                # Assert
                expect(budget_status.message).to(equal('Over Budget by 6 points'))
                expect(budget_status.color).to(equal('warning'))
            
            with it('should have character save not prevented'):
                # Arrange
                ranks = {'STR': 10, 'STA': 10, 'AGL': 10, 'DEX': 10, 'FGT': 10, 'INT': 10, 'AWE': 10, 'PRE': 8}
                character = create_character_with_abilities(power_level=10, ability_ranks=ranks)
                
                # Act
                can_save = character.can_be_saved()
                
                # Assert
                expect(can_save).to(be_true)  # Warn, don't prevent
            
            with it('should have progress bar showing overfilled percentage'):
                # Arrange
                ranks = {'STR': 10, 'STA': 10, 'AGL': 10, 'DEX': 10, 'FGT': 10, 'INT': 10, 'AWE': 10, 'PRE': 8}
                character = create_character_with_abilities(power_level=10, ability_ranks=ranks)
                
                # Act
                progress = character.get_budget_progress()
                
                # Assert
                expect(progress.percentage).to(equal(104))  # 156/150 * 100
        
        with context('with multiple changes'):
            
            with it('should have budget updated after each ability change'):
                # Arrange
                character = create_character_with_abilities(power_level=10)
                
                # Act & Assert
                character.set_ability_rank('STR', 5)
                expect(character.get_total_ability_points()).to(equal(10))
                
                character.set_ability_rank('AGL', 4)
                expect(character.get_total_ability_points()).to(equal(18))
                
                character.set_ability_rank('INT', 6)
                expect(character.get_total_ability_points()).to(equal(30))
            
            with it('should have real-time updates within 100ms per change'):
                # Arrange
                import time
                character = create_character_with_abilities(power_level=10)
                
                # Act
                changes = [('STR', 5), ('AGL', 4), ('INT', 6)]
                for ability, rank in changes:
                    start_time = time.time()
                    character.set_ability_rank(ability, rank)
                    elapsed = (time.time() - start_time) * 1000
                    
                    # Assert
                    expect(elapsed).to(be_below(100))
            
            with it('should have cumulative cost reflected in total'):
                # Arrange
                character = create_character_with_abilities(power_level=10)
                
                # Act
                character.set_ability_rank('STR', 5)   # 10pp
                character.set_ability_rank('AGL', 4)   # 8pp
                character.set_ability_rank('INT', 6)   # 12pp
                
                # Assert
                expect(character.get_total_ability_points()).to(equal(30))
                expect(character.remaining_budget).to(equal(120))


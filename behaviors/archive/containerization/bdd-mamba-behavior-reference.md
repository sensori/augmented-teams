# BDD Mamba Behavior Reference

Comprehensive examples and patterns for BDD testing with Mamba/Python.

See `bdd-mamba-behavior-rule.mdc` for the concise rule file and `bdd-behavior-rule.mdc` for framework-agnostic principles.

---

## 1. Business Readable Language

### Use Nouns for Describe, Connect with Linking Words, Nest Broad→Specific

**✅ Excellent Example:**

```python
from mamba import description, context, it, before
from expects import expect, equal, be_true, be_false

with description('a ranged damage power'):
    with before.each:
        self.helper = StandardTestHelper()
        self.standard_actor = self.helper.actor
        ranged_pouvoir = self.helper.create_pouvoir_with_deltas({
            'name': "Ranged " + self.helper.pouvoir['name'],
            'portee': "distance",
            'effetsprincipaux': "Damage 10",
            'rang': 10
        })
        self.ranged_power = Power(ranged_pouvoir, self.standard_actor)
        self.test_target = mock_factory.create_target()
    
    with context('that has targeted and resulted in a successful attack'):
        with before.each:
            self.ranged_power.attack.targets.add(self.test_target)
            global_roll = lambda: mock_factory.create_roll({'total': 20, 'dice_total': 12})
            self.attack_results = await self.ranged_power.attack.roll_to_hit()
        
        with it('should have attack DC equal to target actor\'s dodge ability'):
            expect(self.attack_results[0].DC).to(equal(self.test_target.actor.system.defense.esquive.total + 10))
        
        with context('that the target has rolled a resistance save against'):
            with before.each:
                global_roll = lambda: mock_factory.create_roll({'total': 10, 'dice_total': 2})
                self.resistance_result = await self.attack_results[0].effect.roll_resistance()
            
            with it('should apply damage based on degrees of failure'):
                expect(self.resistance_result.degrees_of_failure).to(equal(2))
                expect(self.resistance_result.outcome.injuries).to(equal(2))
                expect(self.test_target.actor.system.blessure).to(equal(2))
            
            with it('should apply conditions based on degree (Dazed, Staggered, Incapacitated)'):
                expect(self.resistance_result.outcome.condition).to(equal(['staggered']))
```

**❌ Bad Example:**

```python
with description('when attacking Target'):  # Action verb, class name
    with description('Power.execute() results'):  # Method name
        with context('retrieved attack'):  # Breaks connection
            with it('sets is_submitting flag'):  # Missing "should", jargon
                expect(result.is_submitting).to(be_true)
```

---

## 2. Comprehensive and Brief

### Test Observable Behavior, Cover All Paths, Keep Tests Short & Fast

**✅ Excellent Example:**

```python
from mamba import description, context, it, before
from expects import expect, equal, be_true, be_false, be_none
from unittest.mock import Mock

with description('a damage power'):
    with before.each:
        damage_pouvoir = self.helper.create_pouvoir_with_deltas({
            'name': "Damage Power",
            'effetsprincipaux': "Damage 5",
            'notes': "<p>DC 20; Smash [5 extra ranks]</p>",
            'rang': 5
        })
        self.damage_power = Power(damage_pouvoir, self.standard_actor)
        self.damage_effect = self.damage_power.effect
        self.test_target = mock_factory.create_target({'dodge': 15, 'injury': 0})
        self.test_target.actor.system.blessure = 0
        self.test_target.actor.effects = []
    
    # Cover STATE
    with it('should be a ranged attack'):
        expect(self.damage_power.is_ranged).to(be_true)
    
    with it('should have default resistance of toughness'):
        expect(self.damage_effect.resistance).to(equal("toughness"))
    
    # Cover CALCULATIONS
    with it('should calculate DC from targets dodge'):
        self.damage_power.attack.targets.add(self.test_target)
        global_roll = lambda: mock_factory.create_roll({'total': 20})
        result = self.damage_power.attack.roll_to_hit_target(self.test_target)
        expect(result.DC).to(equal(18))  # target parade (8) + 10
    
    # Cover BUSINESS RULES
    with it('should have resistance formula that includes resistance bonus'):
        formula = self.damage_effect.resistance_formula
        expect(formula).to(contain('1d20 + 8'))
    
    # Cover INTERACTIONS
    with context('that has executed an attack that has hit the target'):
        with before.each:
            self.damage_power.attack.targets.add(self.test_target)
        
        with it('should trigger damage resistance save (toughness)'):
            mock_roll = {
                'formula': '1d20 + 8',
                'total': 25,
                'dice': [{'total': 17}]
            }
            global_roll = lambda: mock_roll
            
            resistance_result = await self.damage_effect.roll_resistance()
            expect(resistance_result).not_to(be_none)
            expect(resistance_result.success).to(be_true)
    
    # Cover NORMAL PATH
    with context('whose roll exceeds the DC'):
        with before.each:
            global_roll = lambda: mock_factory.create_roll({'total': 26, 'dice_total': 18})
            self.result = await self.damage_effect.roll_resistance()
        
        with it('should indicate a hit'):
            expect(self.result.success).to(be_true)
        
        with it('should have zero degrees of failure'):
            expect(self.result.degrees_of_failure).to(equal(0))
        
        with it('should not apply injuries'):
            expect(self.result.injuries).to(be_none)
    
    # Cover FAILURE PATH
    with context('whose roll does not exceed the DC'):
        with before.each:
            global_roll = lambda: mock_factory.create_roll({'total': 10, 'dice_total': 2})
            self.result = await self.damage_effect.roll_resistance()
        
        with it('should indicate a miss'):
            expect(self.result.success).to(be_false)
        
        with it('should calculate degrees of failure'):
            expect(self.result.degrees_of_failure).to(equal(2))
        
        with it('should apply 1 injury per degree of failure'):
            outcome = self.result.outcome
            expect(outcome.injuries).to(equal(2))
            expect(self.test_target.actor.system.blessure).to(equal(2))
        
        with it('should apply conditions based on degree (Dazed, Staggered, Incapacitated)'):
            expect(self.result.outcome.condition).to(equal(['staggered']))
            expect(len(self.test_target.actor.effects)).to(be_above(0))
```

**❌ Bad Example:**

```python
with it('calls _validate()'):  # Tests internal calls, tests private state, omits "should"
    expect(form._flag).to(be_true)
    expect(form._validate).to(have_been_called)

with it('handles attack'):  # Skips validations, long procedural test
    # 50 lines...
    time.sleep(2)  # Arbitrary sleep
    expect(db.records).to(have_len(5))  # External state dependency
```

---

## 3. Balance Context Sharing with Localization

### Nest Parent Context, Use Helper Factories, Reset Between Runs

**✅ Excellent Example:**

```python
from mamba import description, context, it, before

# Helper factory
def create_power(overrides=None):
    defaults = {'name': 'Test Power', 'rank': 10}
    return Power({**defaults, **(overrides or {})})

# More complex factory (Python equivalent of attack.test.mjs)
class StandardTestHelper:
    @property
    def actor(self):
        return {
            '_id': "Ub42p1BuHTw2J7mT",
            'name': "A Standard Power",
            'system': {
                'caracteristique': self.abilities,
                'defense': self.defenses,
            },
            'pouvoirs': [self.pouvoir],
            'items': [self.pouvoir]
        }
    
    def create_pouvoir_with_deltas(self, deltas):
        pouvoir = {**self.pouvoir}
        pouvoir['system'] = {**pouvoir['system']}
        
        if 'name' in deltas:
            pouvoir['name'] = deltas['name']
        if 'portee' in deltas:
            pouvoir['system']['portee'] = deltas['portee']
        if 'rang' in deltas:
            pouvoir['system']['cout']['rang'] = deltas['rang']
        
        return pouvoir

# Single factory instance with reset
mock_factory = MockFoundryFactory()

with description('a Power'):
    with before.each:
        self.helper = StandardTestHelper()
        self.standard_actor = self.helper.actor
        self.standard_power = Power(self.helper.pouvoir, self.standard_actor)
        mock_targets.clear()
        mock_factory.reset()  # Clear state between runs
    
    with context('created from an actor that has a pouvoir'):
        with it('should have a reference to owning actor'):
            expect(self.standard_power.actor).to(be(self.standard_actor))
        
        with it('should take power name and descriptor from pouvoir'):
            expect(self.standard_power.name).to(equal(self.helper.pouvoir['name']))
            expect(self.standard_power.descriptors[1]).to(equal(self.helper.pouvoir['system']['descripteurs'][1]))
    
    with context('that is a ranged power'):
        with before.each:
            self.ranged_power = create_power({'range': 'ranged'})  # Decorate parent setup
        
        with it('should have distance calculated from power level'):
            expect(self.ranged_power.attack.distance).to(equal(40))
        
        with context('whose actor data is being shown on a character sheet'):
            with before.each:
                result = await mock_factory.prepare_attack_sheet_and_render_html(
                    self.standard_actor, 
                    self.ranged_power
                )
                self.context = result['context']
                self.html = result['html']
            
            with it('should include ranged attack data in context'):
                expect(self.context['attack_powers'][0]['attack']['range']).to(equal(RANGES.RANGED))
                expect(self.context['attack_powers'][0]['attack']['bonus']).to(equal(
                    self.standard_actor['system']['caracteristique']['dexterite']['total']
                ))
```

**❌ Bad Example:**

```python
with description('Power'):  # Missing article
    with context('created from actor'):
        with before.each:  # Duplicated init
            self.actor = {'id': '123'}
    
    with context('that is ranged'):
        with before.each:  # Duplicated setup
            self.actor = {'id': '123'}  # Should be in parent

with it('has tokens'):
    t = get_tokens()  # Helper per test
    self.state = 'dirty'  # Side effects
```

---

## 4. Cover All Layers of the System

### Include Separate Tests for Each Layer, Isolate with Mocks, Organize to Tell a Story

**✅ Excellent Example:**

```python
with description('an Attack Power'):
    with before.each:
        self.helper = StandardTestHelper()
        self.standard_actor = self.helper.actor
        damage_pouvoir = make_damage_pouvoir(self.helper)
        self.damage_power = Power(damage_pouvoir, self.standard_actor)
        mock_factory.reset()
    
    # FRONT-END LAYER - UI/Presentation
    with context('whose actor data is being displayed on a character sheet'):
        with before.each:
            result = await mock_factory.prepare_attack_sheet_and_render_html(
                self.standard_actor,
                self.damage_power
            )
            self.context = result['context']
            self.html = result['html']
        
        with it('should include attack bonus in context'):
            expect(self.context['attack_powers'][0]['effect_fragment']).to(equal('damage'))
            expect(self.context['attack_powers'][0]['effect']['name']).to(equal("Damage"))
            expect(self.context['attack_powers'][0]['effect']['resistance']).to(equal("toughness"))
        
        with it('should render attack bonus in HTML'):
            expect(self.html).to(contain("Damage"))
            expect(self.html).to(contain(str(self.damage_power.effect.rank)))
            expect(self.html).to(contain("Toughness"))
    
    # DOMAIN LAYER - Business Logic
    with context('that is a damage power'):
        with it('should calculate damage from rank'):
            expect(self.damage_power.effect).not_to(be_none)
            expect(self.damage_power.effect.name).to(equal("Damage"))
            expect(self.damage_power.effect.rank).to(equal(13))
        
        with it('should have default resistance of toughness'):
            expect(self.damage_power.effect.resistance).to(equal("toughness"))
        
        with context('that has executed an attack that has hit the target'):
            with before.each:
                self.damage_power.attack.targets.add(self.test_target)
            
            with it('should trigger damage resistance save (toughness)'):
                mock_roll = {
                    'formula': '1d20 + 8',
                    'total': 25,
                    'dice': [{'total': 17}]
                }
                resistance_result = await self.damage_power.effect.roll_resistance()
                expect(resistance_result).not_to(be_none)
                expect(resistance_result.success).to(be_true)
    
    # DATA ACCESS LAYER - Persistence
    with context('that has been saved to the repository'):
        with before.each:
            self.mock_db = Mock()
            self.repo = AttackRepository(self.mock_db)
            self.repo.save_attack(self.damage_power.attack)
        
        with context('that is retrieved at a later time'):
            with it('should return the saved attack with all properties'):
                retrieved = self.repo.get_attack(self.damage_power.attack.id)
                expect(retrieved.bonus).to(equal(self.damage_power.attack.bonus))
                expect(retrieved.range).to(equal(self.damage_power.attack.range))
```

**❌ Bad Example:**

```python
with description('when attacking Target'):  # Action verb, class name
    with description('Power.execute() results'):  # Method name
        with context('retrieved attack'):  # Breaks connection
            with it('sets is_submitting flag'):  # Missing "should", jargon
                expect(result.is_submitting).to(be_true)
```

---

## 2. Comprehensive and Brief

### Test Observable Behavior, Cover All Paths, Keep Tests Short & Fast

**✅ Excellent Example:**

```python
with description('a damage power'):
    with before.each:
        damage_pouvoir = self.helper.create_pouvoir_with_deltas({
            'name': "Damage Power",
            'effetsprincipaux': "Damage 5",
            'notes': "<p>DC 20; Smash [5 extra ranks]</p>",
            'rang': 5
        })
        self.damage_power = Power(damage_pouvoir, self.standard_actor)
        self.damage_effect = self.damage_power.effect
        self.test_target = mock_factory.create_target({'dodge': 15, 'injury': 0})
        self.test_target.actor.system.blessure = 0
        self.test_target.actor.effects = []
    
    # Cover STATE
    with it('should be a ranged attack'):
        expect(self.damage_power.is_ranged).to(be_true)
    
    with it('should have default resistance of toughness'):
        expect(self.damage_effect.resistance).to(equal("toughness"))
    
    # Cover CALCULATIONS
    with it('should calculate DC from targets dodge'):
        self.damage_power.attack.targets.add(self.test_target)
        result = self.damage_power.attack.roll_to_hit_target(self.test_target)
        expect(result.DC).to(equal(20))
    
    # Cover BUSINESS RULES
    with it('should have resistance formula that includes resistance bonus'):
        formula = self.damage_effect.resistance_formula
        expect(formula).to(contain('1d20 + 8'))
    
    # Cover INTERACTIONS
    with context('that has executed an attack that has hit the target'):
        with before.each:
            self.damage_power.attack.targets.add(self.test_target)
        
        with it('should trigger damage resistance save (toughness)'):
            mock_roll = {
                'formula': '1d20 + 8',
                'total': 25,
                'dice': [{'total': 17}]
            }
            resistance_result = await self.damage_effect.roll_resistance()
            expect(resistance_result).not_to(be_none)
            expect(resistance_result.success).to(be_true)
    
    # Cover NORMAL PATH
    with context('whose roll exceeds the DC'):
        with before.each:
            self.result = await self.damage_effect.roll_resistance()
        
        with it('should indicate a hit'):
            expect(self.result.success).to(be_true)
        
        with it('should have zero degrees of failure'):
            expect(self.result.degrees_of_failure).to(equal(0))
        
        with it('should not apply injuries'):
            expect(self.result.injuries).to(be_none)
    
    # Cover FAILURE PATH
    with context('whose roll does not exceed the DC'):
        with before.each:
            mock_roll = Mock(total=10, dice=[Mock(total=2)])
            self.result = await self.damage_effect.roll_resistance()
        
        with it('should indicate a miss'):
            expect(self.result.success).to(be_false)
        
        with it('should calculate degrees of failure'):
            expect(self.result.degrees_of_failure).to(equal(2))
        
        with it('should apply 1 injury per degree of failure'):
            outcome = self.result.outcome
            expect(outcome.injuries).to(equal(2))
            expect(self.test_target.actor.system.blessure).to(equal(2))
        
        with it('should apply conditions based on degree'):
            expect(self.result.outcome.condition).to(equal(['staggered']))
```

**❌ Bad Example:**

```python
with it('calls _validate()'):
    expect(form._flag).to(be_true)
    expect(form._validate).to(have_been_called)

with it('handles attack'):
    # 50 lines...
    time.sleep(2)
    expect(db.records).to(have_len(5))
```

---

## 3. Balance Context Sharing with Localization

### Nest Parent Context, Use Helper Factories, Reset Between Runs

**✅ Excellent Example:**

```python
# Helper factory
def create_power(overrides=None):
    defaults = {'name': 'Test Power', 'rank': 10}
    return Power({**defaults, **(overrides or {})})

# More complex factory (Python equivalent of attack.test.mjs)
class StandardTestHelper:
    @property
    def actor(self):
        return {
            '_id': "Ub42p1BuHTw2J7mT",
            'name': "A Standard Power",
            'system': {
                'caracteristique': self.abilities,
                'defense': self.defenses,
            },
            'pouvoirs': [self.pouvoir],
            'items': [self.pouvoir]
        }
    
    def create_pouvoir_with_deltas(self, deltas):
        pouvoir = {**self.pouvoir}
        pouvoir['system'] = {**pouvoir['system']}
        pouvoir['system']['cout'] = {**pouvoir['system']['cout']}
        
        if 'name' in deltas:
            pouvoir['name'] = deltas['name']
        if 'portee' in deltas:
            pouvoir['system']['portee'] = deltas['portee']
        if 'rang' in deltas:
            pouvoir['system']['cout']['rang'] = deltas['rang']
        
        return pouvoir

# Single factory instance with reset
mock_factory = MockFoundryFactory()

with description('a Power'):
    with before.each:
        self.helper = StandardTestHelper()
        self.standard_actor = self.helper.actor
        self.standard_power = Power(self.helper.pouvoir, self.standard_actor)
        mock_targets.clear()
        mock_factory.reset()  # Reset between runs
    
    with it('should have a reference to owning actor'):
        expect(self.standard_power.actor).to(be(self.standard_actor))
    
    with it('should take power name from pouvoir'):
        expect(self.standard_power.name).to(equal(self.helper.pouvoir['name']))
    
    with context('that is a ranged power'):
        with before.each:
            self.ranged_power = create_power({'range': 'ranged'})  # Decorate parent setup
        
        with it('should have distance calculated from power level'):
            expect(self.ranged_power.attack.distance).to(equal(40))
```

**❌ Bad Example:**

```python
with description('Power'):
    with context('created from actor'):
        with before.each:
            self.actor = {'id': '123'}
    with context('that is ranged'):
        with before.each:
            self.actor = {'id': '123'}

with it('has tokens'):
    t = get_tokens()
    self.state = 'dirty'
```

---

## 4. Cover All Layers of the System

### Include Separate Tests for Each Layer, Isolate with Mocks, Organize to Tell a Story

**✅ Excellent Example:**

```python
with description('an Attack Power'):
    with before.each:
        self.helper = StandardTestHelper()
        self.standard_actor = self.helper.actor
        damage_pouvoir = make_damage_pouvoir(self.helper)
        self.damage_power = Power(damage_pouvoir, self.standard_actor)
        mock_factory.reset()
    
    # FRONT-END LAYER
    with context('whose actor data is being displayed on a character sheet'):
        with before.each:
            result = await mock_factory.prepare_attack_sheet_and_render_html(
                self.standard_actor,
                self.damage_power
            )
            self.context = result['context']
            self.html = result['html']
        
        with it('should include attack bonus in context'):
            expect(self.context['attack_powers'][0]['bonus']).to(equal(8))
        
        with it('should render attack bonus in HTML'):
            expect(self.html).to(contain('value="8"'))
    
    # DOMAIN LAYER
    with context('that is a damage power'):
        with it('should calculate damage from rank'):
            expect(calculate_damage(5)).to(equal(10))
    
    # DATA ACCESS LAYER
    with context('that has been saved to the repository'):
        with before.each:
            self.mock_db = Mock()
            self.repo = AttackRepository(self.mock_db)
            self.repo.save_attack(self.damage_power.attack)
        
        with context('that is retrieved at a later time'):
            with it('should return the saved attack with all properties'):
                retrieved = self.repo.get_attack(self.damage_power.attack.id)
                expect(retrieved.bonus).to(equal(self.damage_power.attack.bonus))
```

**❌ Bad Example:**

```python
with description('damage'):
    with it('works'):
        expect(requests.get(url)).to(be_ok)

with it('passes if repo ready'):
    render_page()
    expect(db.has_record()).to(be_true)
```

---

## 5. Unit Tests the Front-End

### Mock Services, Test Both Data and Rendering, Validate Conditional Paths

**✅ Excellent Example:**

```python
with description('an attack power display'):
    with before.each:
        self.mock_service = Mock()
        self.helper = StandardTestHelper()
        self.standard_actor = self.helper.actor
        self.standard_power = Power(self.helper.pouvoir, self.standard_actor)
        
        result = await mock_factory.prepare_attack_sheet_and_render_html(
            self.standard_actor,
            self.standard_power
        )
        self.context = result['context']
        self.html = result['html']
    
    # Test data structure
    with it('should include attack bonus in context'):
        expect(self.context['attack_powers'][0]['name']).to(equal(self.standard_power.name))
        expect(self.context['attack_powers'][0]['pouvoir']['_id']).to(equal(self.standard_power.pouvoir['_id']))
        expect(self.context['attack_powers'][0]['attack']).not_to(be_none)
        expect(self.context['attack_powers'][0]['effect']).not_to(be_none)
    
    # Test rendered output
    with it('should render attack bonus in HTML'):
        html = render_template(self.context)
        expect(html).to(contain(self.standard_power.effect.name))
        expect(html).to(contain(str(self.standard_power.effect.rank)))
        expect(html).to(contain('value="8"'))
    
    with it('should render attack button with power id'):
        expect(self.html).to(contain(self.standard_power.name))
        expect(self.html).to(contain('class="attack-roll"'))
        expect(self.html).to(contain(f'data-power-id="{self.standard_power.pouvoir["_id"]}"'))
    
    # Validate conditional render paths
    with context('that is loading'):
        with before.each:
            self.context['is_loading'] = True
            self.html = render_template(self.context)
        
        with it('should show spinner'):
            expect(self.html).to(contain('loading-spinner'))
        
        with it('should not show attack list'):
            expect(self.html).not_to(contain('attack-list'))
```

**❌ Bad Example:**

```python
with it('renders bonus'):  # Tests only HTML, hits APIs, tests styling
    expect(html).to(contain('value="8"'))
    expect(html).to(contain('color: blue'))
    requests.get('http://api.com')

with it('calls _on_mount()'):  # Tests lifecycle internals
    expect(component._on_mount).to(have_been_called)
```

---

## Common Mamba Patterns

**Single factory instance with reset:**
```python
mock_factory = MockFoundryFactory()

with before.each:
    mock_factory.reset()  # Runs before ALL tests
```

**Helper factories:**
```python
def make_ranged_pouvoir(helper):
    return helper.create_pouvoir_with_deltas({
        'name': "Ranged " + helper.pouvoir['name'],
        'portee': "distance",
        'effetsprincipaux': "Base Effect 10",
        'rang': 10
    })
```

**Mocking with unittest.mock:**
```python
from unittest.mock import Mock, patch

with before.each:
    self.api = Mock()
    self.api.post.return_value = {'id': '123', 'email': 'test@example.com'}
    self.service = UserService(self.api)

with it('should create user with email'):
    user = self.service.create_user('test@example.com')
    expect(user['email']).to(equal('test@example.com'))
    self.api.post.assert_called_once()  # Side-effect check
```

**Async tests:**
```python
with _it('should fetch data asynchronously'):
    async def spec():
        data = await fetch_data()
        expect(data).not_to(be_none)
```

**Expect matchers:**
```python
expect(value).to(equal(expected))
expect(value).to(be_true)
expect(value).to(be_false)
expect(value).to(be_none)
expect(collection).to(contain(item))
expect(collection).to(have_len(3))
expect(func).to(raise_error(ValueError))
expect(mock).to(have_been_called)
```

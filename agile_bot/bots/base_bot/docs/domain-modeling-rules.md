# Domain Modeling Rules

## Overview

These rules guide the creation of domain models that follow resource-oriented, object-oriented design principles. Domain models should represent code as closely as possible, using natural English and proper dependency management.

---

## Rule 1: Use Resource-Oriented, Object-Oriented Design

**Do:** Use object-oriented classes (singular or collection) with responsibilities that encapsulate logic over manager/doer/loader patterns. Maximize encapsulation through collaborator relationships.

**Don't:** Create manager/doer/loader classes when resource-oriented design is possible.

### Domain Model Example (Investment Domain) - CRC Format:

**GOOD - Resource-Oriented:**
```
Portfolio
    Instantiated with: AccountId, RiskTolerance
    Get total value: Holdings
    Assess risk: Holdings, RiskModel
    Get holdings: Holdings

Holdings (Collection Class)
    Instantiated with: Portfolio
    Get many positions: Position
    Get equity positions: Position
    Get bond positions: Position
    Find by symbol: Symbol
```

**BAD - Manager Pattern:**
```
PortfolioManager
    Instantiated with: FileSystem
    Get holdings: ClientId, AccountId
    Calculate total value: Holdings
    Assess risk: Holdings, RiskModel

HoldingsLoader
    Instantiated with: FileSystem
    Load holdings: ClientId, AccountId
```

### Code Example:

```python
# GOOD: Resource-oriented
class Portfolio:
    def __init__(self, account_id: AccountId, risk_tolerance: RiskTolerance):
        self.account_id = account_id
        self.risk_tolerance = risk_tolerance
    
    @property
    def holdings(self) -> Holdings:
        if not hasattr(self, '_holdings'):
            self._holdings = Holdings(self)
        return self._holdings
    
    @property
    def total_value(self) -> Money:
        return sum(position.market_value 
                  for position in self.holdings.get_many_positions())

# BAD: Manager pattern
class PortfolioManager:
    def get_holdings(self, client_id, account_id):
        return self._load_holdings(client_id, account_id)
    
    def calculate_total_value(self, holdings):
        return sum(h.value for h in holdings)
```

---

## Rule 2: Encapsulate State and Behavior Through Properties

**Do:** Use properties as the primary mechanism for encapsulation. Properties control access to object state, hide internal representation, and allow objects to manage their own data. Objects expose properties representing what they *are* or *contain*, not raw data access methods. Properties can encapsulate both simple values and complex behaviors.

**Don't:** Expose internal state through public fields or getter/setter methods that act as glorified public fields. Don't return mutable references to internal collections or objects. Don't force callers to manipulate object internals directly.

### Domain Model Example (Investment Domain) - CRC Format:

**GOOD - Property Encapsulation:**
```
Portfolio
    Instantiated with: AccountId, RiskTolerance
    Get holdings: Holdings (property encapsulates collection access)
    Get total value: Holdings (property encapsulates calculation)
    Get risk score: Holdings, RiskModel (property encapsulates complex behavior)

Holdings (Collection Class)
    Instantiated with: Portfolio
    Get many positions: Position (property encapsulates collection)
    Find by symbol: Symbol (property encapsulates search behavior)
    Get equity positions: Position (property encapsulates filtering)
```

**BAD - Exposed Internal State:**
```
Portfolio
    Instantiated with: AccountId, RiskTolerance
    Get holdings list: List (exposes internal structure)
    Get positions array: Array (exposes internal representation)
    Set holdings: List (allows external manipulation)
    Calculate total value: Holdings (method instead of property)

HoldingsLoader
    Instantiated with: FileSystem
    Load positions: ClientId, AccountId (exposes loading mechanism)
    Get raw positions: List (exposes internal structure)
```

### Code Example:

```python
# GOOD: Properties encapsulate state and behavior
class Portfolio:
    def __init__(self, account_id: AccountId, risk_tolerance: RiskTolerance):
        self._account_id = account_id  # Private field
        self._risk_tolerance = risk_tolerance
        self._holdings = None  # Encapsulated, lazy-loaded
    
    @property
    def holdings(self) -> Holdings:
        # Property encapsulates lazy initialization
        if self._holdings is None:
            self._holdings = Holdings(self)
        return self._holdings
    
    @property
    def total_value(self) -> Money:
        # Property encapsulates calculation
        return sum(position.market_value 
                  for position in self.holdings.get_many_positions())
    
    @property
    def risk_score(self) -> RiskScore:
        # Property encapsulates complex behavior
        return RiskModel.calculate(self.holdings, self._risk_tolerance)

class Holdings:
    def __init__(self, portfolio: Portfolio):
        self._portfolio = portfolio
        self._positions = []  # Private collection
    
    @property
    def get_many_positions(self) -> List[Position]:
        # Property returns defensive copy, not mutable reference
        return list(self._positions)
    
    def find_by_symbol(self, symbol: Symbol) -> Optional[Position]:
        # Encapsulated search behavior
        return next((p for p in self._positions if p.symbol == symbol), None)

# BAD: Exposed internal state
class Portfolio:
    def __init__(self, account_id, risk_tolerance):
        self.holdings = []  # Public field - no encapsulation
        self.positions = []  # Exposed internal structure
    
    def get_holdings_list(self):
        # Returns mutable reference - caller can modify internals
        return self.holdings
    
    def set_holdings(self, holdings):
        # Allows external manipulation of internal state
        self.holdings = holdings
    
    def calculate_total_value(self, holdings):
        # Method instead of property - exposes calculation as action
        return sum(h.value for h in holdings)
```

---

## Rule 3: Maximize Code Behind Properties - Hide Calculation Timing

**Do:** Use properties for lazy initialization, derived values, and complex access patterns. Properties hide when calculations occur—they may be computed on-demand, cached, pre-computed, or loaded from storage. The caller shouldn't know or care when the value was calculated.

**Don't:** Expose implementation details in method signatures. Don't reveal when or how calculations happen.

### Domain Model Example (Investment Domain) - CRC Format:

**GOOD:**
```
Portfolio
    Instantiated with: AccountId, RiskTolerance
    Get total value: Holdings (could be calculated now, cached, or pre-computed)
    Get risk score: Holdings, RiskModel (computation timing hidden)
    Get performance metrics: Holdings, PerformanceCalculator
```

**BAD:**
```
Portfolio
    Instantiated with: AccountId, RiskTolerance
    Calculate total value: Holdings (reveals it's calculated NOW)
    Get cached total value: None (reveals it's cached)
```

### Code Example:

```python
# GOOD: Properties hide WHEN calculation happens
class Portfolio:
    @property
    def total_value(self) -> Money:
        # Could be computed on-demand, cached, pre-computed, or loaded from DB
        # Caller doesn't know or care when it was calculated
        if not hasattr(self, '_total_value'):
            self._total_value = sum(
                position.market_value 
                for position in self.holdings.get_many_positions()
            )
        return self._total_value
    
    # OR it could be pre-computed and stored:
    # @property
    # def total_value(self) -> Money:
    #     return self._cached_total_value  # Calculated two weeks ago? Caller doesn't know

# BAD: Exposing calculation timing
class Portfolio:
    def calculate_total_value(self, holdings: List[Position]) -> Money:
        # Name reveals it's calculated NOW
        return sum(position.market_value for position in holdings)
    
    def get_cached_total_value(self) -> Money:
        # Name reveals it's cached (timing exposed)
        return self._cached_value
```

---

## Rule 4: Use Domain Language, Not Generic Terms (Property-Oriented)

**Do:** Use domain-specific language for classes, responsibilities, and collaborators. Objects should expose properties representing what they contain (e.g., `recommended_trades`), not methods that "generate" or "calculate" things. If field-level variables are needed for clarity, show them with dot notation (class.field).

**Don't:** Use generic terms like "parameter", "result", "data", "config" without domain context. Don't use method names like "generate" or "calculate" when a property would better represent the domain concept.

### Domain Model Example (Investment Domain) - CRC Format:

**GOOD - Domain Language with Properties:**
```
RebalanceRecommendation
    Instantiated with: Portfolio, TargetAllocation
    Get recommended trades: Portfolio, TargetAllocation
    Get allocation comparison: Portfolio, TargetAllocation

Portfolio
    Instantiated with: AccountId, RiskTolerance
    Get total value: Holdings
    Get risk score: Holdings, RiskModel
```

**BAD - Generic Terms:**
```
RebalanceRecommendation
    Generate recommendation: PortfolioData, TargetConfig
    Calculate trades: HoldingsData, PercentagesConfig

Portfolio
    Calculate total value: HoldingsData
    Get result: CalculationResult
```

### Code Example:

```python
# GOOD: Property-oriented with domain language
class RebalanceRecommendation:
    def __init__(self, portfolio: Portfolio, target: TargetAllocation):
        self.portfolio = portfolio
        self.target = target
    
    @property
    def recommended_trades(self) -> List[Trade]:
        # Property represents what the recommendation contains
        if not hasattr(self, '_recommended_trades'):
            current_holdings = self.portfolio.holdings.get_many_positions()
            target_percentages = self.target.asset_classes.percentages
            self._recommended_trades = self._calculate_trades(
                current_holdings, target_percentages
            )
        return self._recommended_trades

# BAD: Method-oriented with generic terms
class RebalanceRecommendation:
    def generate(self, portfolio_data: dict, target_config: dict):
        # Generic "data" and "config" terms
        holdings = portfolio_data['holdings']
        percentages = target_config['percentages']
        return self._calculate_trades(holdings, percentages)
```

---

## Rule 5: Delegate Responsibilities to the Lowest Level Object

**Do:** Delegate responsibilities to the lowest-level object that can handle them. If a collection class can do something, delegate to it rather than implementing it in the parent.

**Don't:** Implement responsibilities in parent objects when a lower-level collaborator can handle them. Don't create unnecessary delegation chains.

### Domain Model Example (Investment Domain) - CRC Format:

**GOOD - Delegation to Lowest Level:**
```
WealthAdvisor
    Instantiated with: Client, InvestmentStrategy
    Find client by account: Client
    Create portfolio: Client, InvestmentStrategy
    Get many portfolios: Portfolio

Client (Collection Class)
    Instantiated with: WealthAdvisor
    Find by account id: AccountId
    Get many clients: None

Portfolio
    Instantiated with: AccountId, RiskTolerance
    Find position by symbol: Holdings
    Get many positions: Holdings

Holdings (Collection Class)
    Instantiated with: Portfolio
    Find by symbol: Symbol
    Get many positions: Position
```

**BAD - Parent Doing What Child Should Do:**
```
WealthAdvisor
    Instantiated with: Client, InvestmentStrategy
    Find client by account: AccountId (WealthAdvisor doing what Client should do)
    Find position by symbol: Portfolio, Symbol (WealthAdvisor doing what Holdings should do)

Client (Collection Class)
    Instantiated with: WealthAdvisor
    Find by account id: WealthAdvisor (wrong - should take AccountId directly)

Portfolio
    Instantiated with: AccountId, RiskTolerance
    Find position by symbol: Symbol (Portfolio doing what Holdings should do)

Holdings (Collection Class)
    Instantiated with: Portfolio
    Find by symbol: Portfolio (wrong - should take Symbol directly)
```

### Code Example:

```python
# GOOD: Bot delegates to Behaviors (lowest level)
class Bot:
    def __init__(self, name: str, workspace: Workspace):
        self.name = name
        self.workspace = workspace
        self.behaviors = Behaviors(self)  # injected
    
    def find_behavior_by_name(self, name: str) -> Optional[Behavior]:
        # Delegates to Behaviors - the lowest level that can do this
        return self.behaviors.find_by_name(name)

class Behaviors:
    def __init__(self, bot: Bot):
        self.bot = bot
    
    def find_by_name(self, name: str) -> Optional[Behavior]:
        # Lowest level - does the actual finding
        # Takes name directly, not through bot
        return self._behaviors.get(name)

# BAD: Bot tries to do what Behaviors should do
class Bot:
    def find_behavior_by_name(self, name: str) -> Optional[Behavior]:
        # Bot doing what Behaviors should do
        for behavior in self.behaviors:
            if behavior.name == name:
                return behavior
        return None

# BAD: Unnecessary delegation chain
class Bot:
    def find_behavior_by_name(self, name: str) -> Optional[Behavior]:
        return self.behaviors.find_behavior(name)  # Behaviors delegates again?

class Behaviors:
    def find_behavior(self, name: str) -> Optional[Behavior]:
        return self.finder.find(name)  # Unnecessary extra level

class BehaviorFinder:  # Unnecessary abstraction
    def find(self, name: str) -> Optional[Behavior]:
        pass
```

### Examples from Domain Model:

**GOOD:**
```
Bot
    Find behavior by name: Behaviors (delegates to Behaviors)

Behaviors (Collection Class)
    Find by name: Bot (takes what it needs directly)

Behavior
    Get rules: Rules (delegates to Rules)

Rules (Collection Class)
    Find by name: Behavior or Bot (lowest level)
```

**BAD:**
```
Bot
    Find behavior by name: Behavior Name (Bot doing what Behaviors should do)

Behaviors (Collection Class)
    Find by name: Behaviors (wrong dependency - should take name directly)
```

---

## Rule 6: Chain Dependencies Through Collaborators with Constructor Injection

**Do:** Map dependencies in a chain: highest-level object → collaborator → sub-collaborator. Inject collaborators at construction time (constructor injection) so methods can use them without passing them as parameters. Access sub-collaborators through their owning objects (e.g., get InvestmentStrategy from Client, not directly). Show dependencies at creation time; later methods only reference created objects.

**Don't:** List every dependency in every method signature. Don't skip levels in the dependency chain. Don't access sub-collaborators directly when they belong to another object.

### Domain Model Example (Investment Domain) - CRC Format:

**GOOD - Proper Dependency Chaining:**
```
WealthAdvisor
    Instantiated with: Client, InvestmentStrategy
    Create portfolio: Client, InvestmentStrategy
    Get portfolio: Portfolio
    Update portfolio: Portfolio
    Get risk tolerance: Client, InvestmentStrategy

Client
    Instantiated with: AccountId, RiskProfile, InvestmentStrategy
    Get account id: AccountId
    Get risk profile: RiskProfile
    Get investment strategy: InvestmentStrategy

InvestmentStrategy
    Instantiated with: RiskTolerance, AssetAllocation
    Get risk tolerance: RiskTolerance
    Get asset allocation: AssetAllocation
```

**BAD - Skipping Levels:**
```
WealthAdvisor
    Instantiated with: Client, InvestmentStrategy
    Create portfolio: AccountId, RiskTolerance, AssetAllocation
    (Skipping Client and InvestmentStrategy levels)

Client
    Instantiated with: AccountId, RiskProfile
    (InvestmentStrategy not owned by Client)
```

### Code Example:

```python
# GOOD: Constructor injection, dependencies shown at creation
class WealthAdvisor:
    def __init__(self, client: Client, investment_strategy: InvestmentStrategy):
        self.client = client  # injected at construction
        self.investment_strategy = investment_strategy
    
    def create_portfolio(self) -> Portfolio:
        # Uses injected collaborators - dependencies shown here
        account_id = self.client.account_id
        risk_tolerance = self.get_risk_tolerance()
        return Portfolio(account_id, risk_tolerance)
    
    def get_portfolio(self) -> Portfolio:
        # No dependencies needed - portfolio already created
        return self._portfolio
    
    def get_risk_tolerance(self) -> RiskTolerance:
        # Gets strategy from client (client owns it)
        client_strategy = self.client.investment_strategy
        return self._calculate_risk_tolerance(
            self.client.risk_profile,
            client_strategy.risk_tolerance
        )

# BAD: Skipping levels, exposing all dependencies
class WealthAdvisor:
    def create_portfolio(self, account_id: AccountId, risk_tolerance: RiskTolerance, 
                        asset_allocation: AssetAllocation):
        # Too many dependencies, skipping Client and InvestmentStrategy levels
        return Portfolio(account_id, risk_tolerance)
```

---

## Rule 7: Group by Domain, Not Technical Layers

**Do:** Group classes by domain area and relationships. Keep related concepts together.

**Don't:** Group by technical layers (presentation, business, data), object types (DTOs, services, repositories), or architectural concerns.

### Domain Model Example (Investment Domain) - CRC Format:

**GOOD - Grouped by Domain Modules:**
```
## Wealth Management Domain

WealthAdvisor
    Instantiated with: Client, InvestmentStrategy
    Create portfolio: Client, InvestmentStrategy
    Get portfolio: Portfolio

Client
    Instantiated with: AccountId, RiskProfile, InvestmentStrategy
    Get account id: AccountId
    Get investment strategy: InvestmentStrategy

Portfolio
    Instantiated with: AccountId, RiskTolerance
    Get total value: Holdings

## Investment Planning Domain

RebalanceAction
    Instantiated with: Portfolio, TargetAllocation
    Create recommendation: Portfolio, TargetAllocation

RebalanceRecommendation
    Instantiated with: Portfolio, TargetAllocation
    Get recommended trades: Portfolio, TargetAllocation

## Reporting Domain (Front-End)

PortfolioReport
    Instantiated with: Portfolio
    Generate report: Portfolio

## Data Access Domain (Back-End)

PortfolioRepository
    Instantiated with: Database
    Save portfolio: Portfolio
    Load portfolio: AccountId
```

**BAD - Grouped by Technical Layers:**
```
## Presentation Layer

PortfolioReport
    Generate report: Portfolio

## Business Logic Layer

WealthAdvisor
    Create portfolio: Client, InvestmentStrategy

## Data Access Layer

PortfolioRepository
    Save portfolio: Portfolio
```

---

## Rule 8: Favor Code Representation Over Abstract Domain Models

**Do:** Domain models should represent code as closely as possible. Code should represent domain concepts. If code doesn't match domain concepts, refactor the code rather than creating abstract domain models.

**Don't:** Create abstract domain models that don't match the code. Don't separate domain models from code implementation.

### Domain Model Example (Investment Domain) - CRC Format:

**GOOD - Code-Aligned Domain Model:**
```
PortfolioAnalysis
    Instantiated with: Portfolio
    Analyze portfolio: Portfolio
    Generate report: AnalysisReport

AnalysisReport
    Instantiated with: PortfolioAnalysis
    Get recommendations: Recommendations
    Get risk assessment: RiskAssessment
    Write report: File
```

**BAD - Abstract Domain Model (No Code Basis):**
```
PortfolioAnalysis
    Analyze portfolio: PortfolioConcept
    Generate insights: DomainInsights

DomainInsights
    Extract patterns: AbstractPatterns
    Synthesize knowledge: KnowledgeBase
```

### Code Example:

```python
# GOOD: Domain model matches code
class PortfolioAnalysis:
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio
    
    def analyze_portfolio(self) -> AnalysisReport:
        # Code matches domain model
        return AnalysisReport(self)

class AnalysisReport:
    def __init__(self, analysis: PortfolioAnalysis):
        self.analysis = analysis
    
    @property
    def recommendations(self) -> Recommendations:
        # Property matches domain model
        return self._generate_recommendations()

# BAD: Abstract domain model with no code basis
class PortfolioAnalysis:
    # Domain model says "Analyze portfolio" but code doesn't exist
    # This is an abstract model, not representing actual code
    pass
```

---

## Rule 9: Avoid Unnecessary Internal/Technical Abstractions

**Do:** Stay at the domain level, even if concrete. Don't separate technical details from domain concepts—they should be the same (class vs object vs file—all represent the same domain concept).

**Don't:** Create unnecessary internal/technical extractions like "saving something", "storing something", or "mentioning a file" vs the domain object. Don't separate technical implementation details from domain concepts.

### Domain Model Example (Investment Domain) - CRC Format:

**GOOD - Domain Level (Concrete but Domain-Focused):**
```
Portfolio
    Instantiated with: AccountId, RiskTolerance
    Get total value: Holdings
    Save portfolio: None (saves to persistent storage)
    Load portfolio: AccountId (loads from persistent storage)

PortfolioRepository
    Instantiated with: Database
    Save portfolio: Portfolio
    Load portfolio: AccountId
```

**BAD - Technical Abstractions Separated:**
```
Portfolio
    Instantiated with: AccountId, RiskTolerance
    Get total value: Holdings

PortfolioSaver
    Instantiated with: FileSystem
    Save portfolio to file: Portfolio, FilePath

PortfolioLoader
    Instantiated with: FileSystem
    Load portfolio from file: FilePath

PortfolioStorage
    Instantiated with: Database
    Store portfolio: Portfolio
    Retrieve portfolio: AccountId
```

### Code Example:

```python
# GOOD: Domain level, technical details hidden
class Portfolio:
    def __init__(self, account_id: AccountId, risk_tolerance: RiskTolerance):
        self.account_id = account_id
        self.risk_tolerance = risk_tolerance
    
    def save(self):
        # Saves to file/database - technical detail hidden
        # Domain concept: "save portfolio"
        self._persist_to_storage()
    
    @classmethod
    def load(cls, account_id: AccountId) -> Portfolio:
        # Loads from file/database - technical detail hidden
        # Domain concept: "load portfolio"
        return cls._load_from_storage(account_id)

# BAD: Technical abstractions separated
class Portfolio:
    def __init__(self, account_id: AccountId):
        self.account_id = account_id

class PortfolioSaver:
    def save_to_file(self, portfolio: Portfolio, file_path: Path):
        # Technical detail exposed: "file", "save to file"
        pass

class PortfolioLoader:
    def load_from_file(self, file_path: Path) -> Portfolio:
        # Technical detail exposed: "file", "load from file"
        pass
```

---

## Rule 10: Use Natural English for Plural, Singular, and Cardinality

**Do:** Use natural English to express relationships:
- Collections: add "s" to the concept name (e.g., `Behaviors`, `Rules`, `Holdings`)
- Accessing many: use "many" in the responsibility (e.g., "Get many positions", "Find many rules")
- Optional/may: use "may" (e.g., "May submit trade", "May update portfolio")
- Required: use "will" or state directly (e.g., "Submit trade", "Will create portfolio")
- One-to-one: use singular without qualifiers (e.g., "Get portfolio", "Create client")

**Don't:** Use brackets, technical notation, or explicit cardinality markers. Don't use "0..1", "1..*", or similar notations.

### Domain Model Example (Investment Domain) - CRC Format:

**GOOD - Natural English:**
```
WealthAdvisor
    Instantiated with: Client, InvestmentStrategy
    Create portfolio: Client, InvestmentStrategy
    Get portfolio: Portfolio
    May update portfolio: Portfolio
    Get many clients: Client
    Will create many portfolios: Client, InvestmentStrategy

Client
    Instantiated with: AccountId, RiskProfile, InvestmentStrategy
    Get account id: AccountId
    Get investment strategy: InvestmentStrategy
    May have many portfolios: Portfolio
    Will have risk profile: RiskProfile

Portfolio
    Instantiated with: AccountId, RiskTolerance
    Get total value: Holdings
    Get many holdings: Holdings
    May have many positions: Position
    Will have risk score: RiskScore

Holdings  
    Instantiated with: Portfolio
    Get many positions: Position
    Get many equity positions: Position
    Get many bond positions: Position
    May find position: Position
    Will contain many positions: Position
```

**BAD - Technical Notation:**
```
WealthAdvisor
    Create portfolio: Client, InvestmentStrategy
    Get portfolio [0..1]: Portfolio
    Get clients [1..*]: Client
    Update portfolio [0..1]: Portfolio

Client
    Get portfolios [0..*]: Portfolio
    Get risk profile [1]: RiskProfile

Portfolio
    Get holdings [1..*]: Holdings
    Get positions [0..*]: Position
```

## Summary

These rules ensure domain models:

**Resource-Oriented & Object-Oriented (Rules 1, 5):**
1. Use resource-oriented, object-oriented design instead of manager/doer/loader patterns
5. Delegate to the lowest-level object that can handle responsibilities

**Property-Oriented & Encapsulation (Rules 2, 3, 4):**
2. Encapsulate state and behavior through properties
3. Hide implementation details behind properties - hide calculation timing
4. Use domain-specific language with properties, not generic terms

**Dependency Management (Rule 6):**
6. Chain dependencies properly with constructor injection

**Organization & Representation (Rules 7, 8, 9, 10):**
7. Group by domain, not technical layers
8. Represent code closely, not abstract concepts
9. Avoid unnecessary technical abstractions
10. Use natural English for relationships and cardinality

Domain models should be concrete, code-aligned, and use natural English to express domain concepts and relationships.

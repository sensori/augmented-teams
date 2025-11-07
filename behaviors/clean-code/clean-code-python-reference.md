# Clean Code Python Reference

This document provides comprehensive examples for `clean-code-python-rule.mdc`.

## Table of Contents

1. [Functions](#1-functions)
   - 1.1 [Single Responsibility](#11-single-responsibility)
   - 1.2 [Small and Focused](#12-small-and-focused)
   - 1.3 [Clear Parameters](#13-clear-parameters)
   - 1.4 [Simple Control Flow](#14-simple-control-flow)
2. [Naming](#2-naming)
   - 2.3 [Meaningful Context](#23-meaningful-context)
3. [Code Structure](#3-code-structure)
   - 3.2 [Separation of Concerns](#32-separation-of-concerns)
4. [Error Handling](#4-error-handling)
   - 4.1 [Use Exceptions Properly](#41-use-exceptions-properly)
5. [State Management](#5-state-management)
   - 5.1 [Minimize Mutable State](#51-minimize-mutable-state)
6. [Classes and Objects](#6-classes-and-objects)
   - 6.1 [Encapsulation with Validation](#61-encapsulation-with-validation)
   - 6.2 [Explicit Dependencies](#62-explicit-dependencies)
   - 6.3 [Immutable Data](#63-immutable-data)
7. [Abstraction Levels](#7-abstraction-levels)
   - 7.1 [Consistent Abstraction](#71-consistent-abstraction)

---

## 1. Functions

### 1.1 Single Responsibility

Functions should do one thing and do it well, with no hidden side effects.

**❌ DON'T:**
```python
def checkout(user, cart):
    subtotal = sum(i.price*i.qty for i in cart.items)
    total = round(subtotal * 1.13, 2)       # magic number
    db.invoices.insert({'user_id': user.id, 'total': total, 'items': cart.items})
    for it in cart.items:
        db.products.decrement(it.sku, it.qty)
    email.send(user.email, f"Thanks for your order of ${total}")
    print('checkout complete', user.id, total)
    return total
```
**✅ DO:**
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Item: sku: str; price: float; qty: int

TAX_RATE = 0.13

def subtotal(items: list[Item]) -> float:
    return sum(i.price * i.qty for i in items)

def total_with_tax(subtotal: float, tax_rate: float = TAX_RATE) -> float:
    return round(subtotal * (1 + tax_rate), 2)

def checkout(user, cart, services):
    sub = subtotal(cart.items)
    total = total_with_tax(sub)
    invoice = services.invoice_repo.save(user_id=user.id, total=total, items=cart.items)
    services.inventory.adjust_many([(i.sku, -i.qty) for i in cart.items])
    services.mailer.send_receipt(user.email, invoice)
    services.logger.info('checkout complete', extra={'user_id': user.id, 'invoice_id': invoice.id, 'total': total})
    return invoice, total
```

### 1.3 Clear Parameters

Prefer parameter objects over long parameter lists; avoid boolean flags.

**❌ DON'T:**
```python
def export_report(data, is_csv: bool):  # DON'T: Boolean flag parameter
    return to_csv(data) if is_csv else to_json(data)

def render(chart, dark_mode, pretty, borders):  # DON'T: Too many parameters
    pass
```

**✅ DO:**
```python
# DO: Separate functions instead of flags
def export_report_as_csv(data): 
    return to_csv(data)

def export_report_as_json(data): 
    return to_json(data)

# DO: Use parameter object for complex signatures
from dataclasses import dataclass

@dataclass
class ConnectionOptions:
    host: str
    port: int
    timeout_ms: int = 2000

def connect(opts: ConnectionOptions):
    pass
```

### 1.4 Simple Control Flow

Use guard clauses to flatten nested conditionals.

**❌ DON'T:**
```python
def price_for(user, plan):
    if user is not None:
        if plan is not None:
            if user.is_student:
                return plan.base * 0.5
            else:
                return plan.base
    return 0
```
**✅ DO:**
```python
def price_for(user, plan):
    if not user or not plan: return 0
    if user.is_student: return plan.base * 0.5
    return plan.base
```

---

## 2. Naming

### 2.3 Meaningful Context

Replace magic numbers with named constants.

**❌ DON'T:** `sleep(86400000)`
**✅ DO:**
```python
MILLISECONDS_PER_DAY = 86_400_000
sleep(MILLISECONDS_PER_DAY)
```

---

## 3. Code Structure

### 3.2 Separation of Concerns

Keep pure logic separate from side effects by breaking complex functions into focused subfunctions.

**❌ DON'T:**
```python
# DON'T: One large function doing everything
def checkout(user, cart):
    # Calculate subtotal
    subtotal = 0
    for item in cart.items:
        subtotal += item.price * item.qty
    
    # Apply tax
    total = round(subtotal * 1.13, 2)
    
    # Validate
    if total > user.credit_limit:
        raise ValueError("Exceeds credit limit")
    
    # Save to database
    db.invoices.insert({'user_id': user.id, 'total': total, 'items': cart.items})
    
    # Update inventory
    for item in cart.items:
        db.products.decrement(item.sku, item.qty)
    
    # Send email
    email.send(user.email, f"Thanks for ${total}")
    
    return total
```

**✅ DO:**
```python
# DO: Break into focused subfunctions - each does ONE thing
def calculate_subtotal(items: list[Item]) -> float:
    return sum(item.price * item.qty for item in items)

def calculate_total_with_tax(subtotal: float, tax_rate: float = 0.13) -> float:
    return round(subtotal * (1 + tax_rate), 2)

def validate_credit_limit(total: float, user_credit_limit: float) -> None:
    if total > user_credit_limit:
        raise ValueError("Exceeds credit limit")

def save_invoice(user_id: int, total: float, items: list[Item], invoice_repo) -> Invoice:
    return invoice_repo.create(user_id=user_id, total=total, items=items)

def adjust_inventory(items: list[Item], inventory_service) -> None:
    for item in items:
        inventory_service.decrement(item.sku, item.qty)

def send_receipt(user_email: str, total: float, mailer) -> None:
    mailer.send(user_email, f"Thanks for your order of ${total:.2f}")

# DO: Orchestrate subfunctions - clear, readable, testable
def checkout(user, cart, services):
    subtotal = calculate_subtotal(cart.items)
    total = calculate_total_with_tax(subtotal)
    validate_credit_limit(total, user.credit_limit)
    
    invoice = save_invoice(user.id, total, cart.items, services.invoice_repo)
    adjust_inventory(cart.items, services.inventory)
    send_receipt(user.email, total, services.mailer)
    
    return invoice
```

---

## 4. Error Handling

### 4.1 Use Exceptions Properly

Prefer informative exceptions over silent failures.

**❌ DON'T:**
```python
try:
    data = json.loads(payload)
except:
    data = None
```
**✅ DO:**
```python
class ParseError(ValueError): pass
def parse_json(payload: str) -> dict:
    try:
        return json.loads(payload)
    except json.JSONDecodeError as e:
        raise ParseError("Invalid JSON") from e
```

---

## 5. State Management

### 5.1 Minimize Mutable State

Prefer immutable data structures and explicit state.

**❌ DON'T:**
```python
settings = {"mode": "prod"}   # shared mutable global
def get_mode(): return settings["mode"]
```
**✅ DO:**
```python
from types import MappingProxyType
SETTINGS = MappingProxyType({"mode": "prod"})
def get_mode(cfg): return cfg["mode"]
```

---

## 6. Classes and Objects

### 6.1 Encapsulation with Validation

Hide implementation details and validate inputs at boundaries.

**❌ DON'T:**
```python
# DON'T: Direct property access, no validation
class Inventory:
    def __init__(self):
        self.items = {}  # Public mutable state
    
    def adjust(self, sku, delta):
        self.items[sku] = self.items.get(sku, 0) + delta  # No validation
```

**✅ DO:**
```python
# DO: Encapsulate state, validate inputs, use explicit repository
class Inventory:
    def __init__(self, repo):
        self._repo = repo  # Private dependency
    
    def adjust_many(self, changes: list[tuple[str, int]]) -> dict:
        for sku, delta in changes:
            # DO: Validate input types
            if not isinstance(sku, str) or not isinstance(delta, int):
                raise TypeError("Invalid inventory change")
            
            # DO: Business rule validation
            current = self._repo.get_by_sku(sku)
            next_qty = current.qty + delta
            if next_qty < 0:
                raise ValueError(f"Negative stock for {sku}")
            
            self._repo.update_qty(sku, next_qty)
        
        return {"updated": len(changes)}
```

### 6.2 Explicit Dependencies

Make all dependencies visible through constructor injection.

**❌ DON'T:**
```python
# DON'T: Hidden global dependency
def calculate_discount(amount):
    return amount * global_discount_rate  # Hidden dependency

# DON'T: Create dependencies inside class
class Mailer:
    def __init__(self):
        self.smtp = SMTPClient()  # Hidden construction
    
    def send(self, to, message):
        self.smtp.send(to, message)
```

**✅ DO:**
```python
# DO: Pass dependencies as parameters
def calculate_discount(amount: float, discount_rate: float) -> float:
    return amount * discount_rate

# DO: Inject dependencies through constructor
class Mailer:
    def __init__(self, smtp_client):
        self._smtp = smtp_client  # Explicit dependency
    
    def send_receipt(self, to: str, invoice) -> None:
        subject = f"Order #{invoice.id} receipt"
        body = f"Thanks for your order totaling ${invoice.total:.2f}."
        self._smtp.send(to=to, subject=subject, body=body)
```

### 6.3 Immutable Data

Prefer immutable structures over mutation.

**❌ DON'T:**
```python
# DON'T: Mutate input parameter
def add_tax(order: dict) -> dict:
    order['total'] *= 1.13  # Mutates caller's data
    return order

# DON'T: Return mutable reference to internal state
class Cart:
    def __init__(self):
        self._items = []
    
    def get_items(self):
        return self._items  # Returns mutable reference
```

**✅ DO:**
```python
# DO: Return new object, don't mutate
def add_tax(order: dict) -> dict:
    return {**order, 'total': order['total'] * 1.13}

# DO: Return immutable copy or use frozen dataclass
from dataclasses import dataclass

@dataclass(frozen=True)
class Item:
    sku: str
    price: float
    qty: int

class Cart:
    def __init__(self):
        self._items: list[Item] = []
    
    def get_items(self) -> tuple[Item, ...]:
        return tuple(self._items)  # Immutable copy
```

---

## 7. Abstraction Levels

### 7.1 Consistent Abstraction

Keep each function at one level of abstraction.

**❌ DON'T:**
```python
# DON'T: Mix high-level orchestration with low-level SQL
def process_order(order):
    validate_order(order)  # High-level
    
    # Low-level SQL in business logic
    db.execute("INSERT INTO orders VALUES (%s, %s)", (order.id, order.total))
    
    send_confirmation(order)  # High-level
```

**✅ DO:**
```python
# DO: Keep abstraction level consistent
def process_order(order, order_repo, notification_service):
    validate_order(order)  # High-level
    saved = order_repo.save(order)  # High-level (hides persistence)
    notification_service.send_confirmation(saved)  # High-level
    return saved
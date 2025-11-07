# Clean Code JavaScript Reference

This document provides comprehensive examples for `clean-code-js-rule.mdc`.

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
```javascript
async function checkout(user, cart) {
  let subtotal = 0;
  for (const i of cart.items) subtotal += i.price * i.qty;
  const total = subtotal * 1.13;                 // magic number
  await db.invoices.insert({ userId: user.id, total, items: cart.items });
  for (const it of cart.items) await db.products.decrement(it.sku, it.qty);
  await email.send(user.email, `Thanks for your order of $${total}`);
  console.log('checkout complete', user.id, total);
  return total;
}
```
**✅ DO:**
```javascript
export function subtotal(items){return items.reduce((s,i)=>s+i.price*i.qty,0);}
export function totalWithTax(subtotal,tax){return Math.round(subtotal*(1+tax)*100)/100;}
export async function checkout({ user, cart, taxRate, services }){
  const sub = subtotal(cart.items);
  const total = totalWithTax(sub, taxRate);
  const invoice = await services.invoiceRepo.save({ userId:user.id, total, items:cart.items });
  await services.inventory.adjustMany(cart.items.map(i=>({ sku:i.sku, delta:-i.qty })));
  await services.mailer.sendReceipt(user.email, invoice);
  services.logger.info('checkout complete', { userId:user.id, invoiceId:invoice.id, total });
  return { invoice, total };
}
```

### 1.3 Clear Parameters

Use destructuring for complex signatures; avoid boolean flags.

**❌ DON'T:**
```javascript
// DON'T: Boolean flag parameter
function exportReport(data, isCsv) { 
  return isCsv ? toCsv(data) : toJson(data); 
}

// DON'T: Too many parameters
function render(chart, darkMode, pretty, borders) {
  // ...
}
```

**✅ DO:**
```javascript
// DO: Separate functions instead of flags
function exportReportAsCsv(data) { 
  return toCsv(data); 
}

function exportReportAsJson(data) { 
  return toJson(data); 
}

// DO: Use destructured object parameter
function connect({ host, port, timeoutMs = 2000 }) {
  // ...
}
```

### 1.4 Simple Control Flow

Use guard clauses to flatten nested conditionals.

**❌ DON'T:**
```javascript
function priceFor(user, plan){
  if(user){ if(plan){ if(user.isStudent) return plan.base*0.5; return plan.base; } }
  return 0;
}
```
**✅ DO:**
```javascript
function priceFor(user, plan){
  if(!user || !plan) return 0;
  if(user.isStudent) return plan.base*0.5;
  return plan.base;
}
```

---

## 2. Naming

### 2.3 Meaningful Context

Replace magic numbers with named constants.

**❌ DON'T:** `const total = subtotal * 1.13;`
**✅ DO:**
```javascript
const TAX_RATE = 0.13;
const total = subtotal * (1 + TAX_RATE);
```

---

## 3. Code Structure

### 3.2 Separation of Concerns

Keep pure logic separate from side effects by breaking complex functions into focused subfunctions.

**❌ DON'T:**
```javascript
// DON'T: One large function doing everything
async function checkout(user, cart) {
  // Calculate subtotal
  let subtotal = 0;
  for (const item of cart.items) {
    subtotal += item.price * item.qty;
  }
  
  // Apply tax
  const total = Math.round(subtotal * 1.13 * 100) / 100;
  
  // Validate
  if (total > user.creditLimit) {
    throw new Error('Exceeds credit limit');
  }
  
  // Save to database
  await db.invoices.insert({ userId: user.id, total, items: cart.items });
  
  // Update inventory
  for (const item of cart.items) {
    await db.products.decrement(item.sku, item.qty);
  }
  
  // Send email
  await email.send(user.email, `Thanks for $${total}`);
  
  return total;
}
```

**✅ DO:**
```javascript
// DO: Break into focused subfunctions - each does ONE thing
function calculateSubtotal(items) {
  return items.reduce((sum, item) => sum + item.price * item.qty, 0);
}

function calculateTotalWithTax(subtotal, taxRate = 0.13) {
  return Math.round(subtotal * (1 + taxRate) * 100) / 100;
}

function validateCreditLimit(total, userCreditLimit) {
  if (total > userCreditLimit) {
    throw new Error('Exceeds credit limit');
  }
}

async function saveInvoice(userId, total, items, invoiceRepo) {
  return invoiceRepo.create({ userId, total, items });
}

async function adjustInventory(items, inventoryService) {
  for (const item of items) {
    await inventoryService.decrement(item.sku, item.qty);
  }
}

async function sendReceipt(userEmail, total, mailer) {
  await mailer.send(userEmail, `Thanks for your order of $${total.toFixed(2)}`);
}

// DO: Orchestrate subfunctions - clear, readable, testable
async function checkout(user, cart, services) {
  const subtotal = calculateSubtotal(cart.items);
  const total = calculateTotalWithTax(subtotal);
  validateCreditLimit(total, user.creditLimit);
  
  const invoice = await saveInvoice(user.id, total, cart.items, services.invoiceRepo);
  await adjustInventory(cart.items, services.inventory);
  await sendReceipt(user.email, total, services.mailer);
  
  return invoice;
}
```

---

## 4. Error Handling

### 4.1 Use Exceptions Properly

Prefer informative exceptions over silent failures.

**❌ DON'T:**
```javascript
try{ return JSON.parse(payload);} catch(e){ /* ignore */ }
```
**✅ DO:**
```javascript
class ParseError extends Error {}
function parseJson(payload){
  try{ return JSON.parse(payload); }
  catch(e){ throw new ParseError('Invalid JSON'); }
}
```

---

## 5. State Management

### 5.1 Minimize Mutable State

Prefer const and immutable patterns.

**❌ DON'T:**
```javascript
let currentUser = null;
export function setUser(u){ currentUser = u; }
export function isLoggedIn(){ return !!currentUser; }
```
**✅ DO:**
```javascript
export function isLoggedIn(session){ return !!session.user; }
```

---

## 6. Classes and Objects

### 6.1 Encapsulation with Validation

Hide implementation details and validate inputs at boundaries.

**❌ DON'T:**
```javascript
// DON'T: Public mutable state, no validation
export class Inventory {
  constructor() {
    this.items = {};  // Public mutable state
  }
  
  adjust(sku, delta) {
    this.items[sku] = (this.items[sku] || 0) + delta;  // No validation
  }
}
```

**✅ DO:**
```javascript
// DO: Encapsulate state, validate inputs, use repository
export class Inventory {
  #repo;  // Private field
  
  constructor(repo) {
    this.#repo = repo;  // Explicit dependency
  }
  
  async adjustMany(changes) {
    for (const { sku, delta } of changes) {
      // DO: Validate input types
      if (typeof sku !== 'string' || typeof delta !== 'number') {
        throw new TypeError('Invalid inventory change');
      }
      
      // DO: Business rule validation
      const current = await this.#repo.findBySku(sku);
      const nextQty = current.qty + delta;
      if (nextQty < 0) {
        throw new Error(`Negative stock for ${sku}`);
      }
      
      await this.#repo.updateQty(sku, nextQty);
    }
    return { updated: changes.length };
  }
}
```

### 6.2 Explicit Dependencies

Make all dependencies visible through constructor injection.

**❌ DON'T:**
```javascript
// DON'T: Hidden global dependency
function calculateDiscount(amount) {
  return amount * globalDiscountRate;  // Hidden dependency
}

// DON'T: Create dependencies inside class
class Mailer {
  constructor() {
    this.smtp = new SMTPClient();  // Hidden construction
  }
  
  send(to, message) {
    this.smtp.send(to, message);
  }
}
```

**✅ DO:**
```javascript
// DO: Pass dependencies as parameters
function calculateDiscount(amount, discountRate) {
  return amount * discountRate;
}

// DO: Inject dependencies through constructor
class Mailer {
  constructor(smtpClient) {
    this._smtp = smtpClient;  // Explicit dependency
  }
  
  async sendReceipt(to, invoice) {
    const subject = `Order #${invoice.id} receipt`;
    const body = `Thanks for your order totaling $${invoice.total.toFixed(2)}.`;
    return this._smtp.send({ to, subject, body });
  }
}
```

### 6.3 Immutable Data

Prefer immutable structures over mutation.

**❌ DON'T:**
```javascript
// DON'T: Mutate input parameter
function addTax(order) {
  order.total *= 1.13;  // Mutates caller's data
  return order;
}

// DON'T: Return mutable reference to internal state
class Cart {
  constructor() {
    this._items = [];
  }
  
  getItems() {
    return this._items;  // Returns mutable reference
  }
}
```

**✅ DO:**
```javascript
// DO: Return new object, don't mutate
function addTax(order) {
  return { ...order, total: order.total * 1.13 };
}

// DO: Return immutable copy or use Object.freeze
class Cart {
  constructor() {
    this._items = [];
  }
  
  getItems() {
    return Object.freeze([...this._items]);  // Immutable copy
  }
}
```

---

## 7. Abstraction Levels

### 7.1 Consistent Abstraction

Keep each function at one level of abstraction.

**❌ DON'T:**
```javascript
// DON'T: Mix high-level orchestration with low-level SQL
async function processOrder(order) {
  validateOrder(order);  // High-level
  
  // Low-level SQL in business logic
  await db.execute("INSERT INTO orders VALUES (?, ?)", [order.id, order.total]);
  
  sendConfirmation(order);  // High-level
}
```

**✅ DO:**
```javascript
// DO: Keep abstraction level consistent
async function processOrder(order, orderRepo, notificationService) {
  validateOrder(order);  // High-level
  const saved = await orderRepo.save(order);  // High-level (hides persistence)
  await notificationService.sendConfirmation(saved);  // High-level
  return saved;
}
```

### 7.2 Async Control Flow

Use async/await instead of callback nesting.

**❌ DON'T:**
```javascript
// DON'T: Callback hell
function fetchUserData(userId, callback) {
  fetchUser(userId, (user) => {
    fetchOrders(user.id, (orders) => {
      fetchProducts(orders, (products) => {
        callback({ user, orders, products });
      });
    });
  });
}
```

**✅ DO:**
```javascript
// DO: Use async/await for clean flow
async function fetchUserData(userId) {
  const user = await fetchUser(userId);
  const orders = await fetchOrders(user.id);
  const products = await fetchProducts(orders);
  return { user, orders, products };
}
```

---

## Additional Resources

- **Related Rules**: See `clean-code-rule.mdc` for framework-agnostic principles
- **Testing**: See `bdd-jest-rule.mdc` for JavaScript/Jest BDD testing practices
- **Type Safety**: Use TypeScript for static type checking
- **Linting**: Configure ESLint with recommended rules
- **Formatting**: Use Prettier for consistent code formatting
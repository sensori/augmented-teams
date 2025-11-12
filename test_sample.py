"""Sample file for testing clean-code runner"""

def checkout(user, cart):
    subtotal = 0  # DON'T: Declared far from use
    tax = 0
    discount = 0
    
    # Many lines later...
    
    subtotal = sum(i.price*i.qty for i in cart.items)
    total = round(subtotal * 1.13, 2)  # DON'T: Magic number
    db.invoices.insert({'user_id': user.id, 'total': total})  # DON'T: Multiple responsibilities
    for it in cart.items:
        db.products.decrement(it.sku, it.qty)
    email.send(user.email, f"Thanks for ${total}")
    print('checkout complete')  # DON'T: Hidden side effect
    return total


def d(x, y, z, w):  # DON'T: Single letter name, too many params
    if x:  # DON'T: Deep nesting
        if y:
            if z:
                if w:
                    return 100
    return 0


class BigClass:  # DON'T: Too large
    def __init__(self):
        pass
    
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    # ... many more methods ...


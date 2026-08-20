from decimal import Decimal, ROUND_HALF_UP

TAX_RATE = Decimal("0.13")

def line_total(unit_price: Decimal, quantity: int) -> Decimal:
    if quantity < 0:
        raise ValueError("quantity must not be negative")
    return (unit_price * quantity).quantize(Decimal("0.01"), ROUND_HALF_UP)

def order_total(items: list[tuple[Decimal, int]]) -> Decimal:
    """items is a list of (unit_price, quantity). Returns the tax inclusive total."""
    subtotal = sum((line_total(p, q) for p, q in items), Decimal("0"))
    tax = (subtotal * TAX_RATE).quantize(Decimal("0.01"), ROUND_HALF_UP)
    return subtotal + tax

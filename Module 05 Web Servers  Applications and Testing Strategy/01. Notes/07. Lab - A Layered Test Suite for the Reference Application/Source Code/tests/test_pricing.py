from decimal import Decimal
import pytest
from refapp.pricing import line_total, order_total

def test_line_total_rounds_half_up():
    assert line_total(Decimal("1.005"), 1) == Decimal("1.01")

def test_order_total_applies_tax():
    # (10.00 * 2) + (5.50 * 1) = 25.50 subtotal; +13% tax = 28.82
    items = [(Decimal("10.00"), 2), (Decimal("5.50"), 1)]
    assert order_total(items) == Decimal("28.82")

def test_negative_quantity_rejected():
    with pytest.raises(ValueError):
        line_total(Decimal("10.00"), -1)

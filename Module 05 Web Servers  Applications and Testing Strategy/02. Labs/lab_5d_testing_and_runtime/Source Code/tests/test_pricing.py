from decimal import Decimal
import pytest
from refapp.pricing import line_total, order_total

def test_line_total_rounds_up_at_the_half():
    assert line_total(Decimal("1.005"), 1) == Decimal("1.01")

def test_order_total_adds_tax():
    items = [(Decimal("10.00"), 2), (Decimal("5.50"), 1)]   # subtotal 25.50
    assert order_total(items) == Decimal("28.82")           # plus 13% tax of 3.32

def test_negative_quantity_is_rejected():
    with pytest.raises(ValueError):
        line_total(Decimal("10.00"), -1)

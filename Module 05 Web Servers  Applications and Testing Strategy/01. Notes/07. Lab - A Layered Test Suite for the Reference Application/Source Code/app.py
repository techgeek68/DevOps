# tests/test_flaky.py
import time
import pytest

@pytest.mark.quarantine          # tagged: runs in a non-blocking lane, not the gate
def test_timing_sensitive():
    start = time.time()
    time.sleep(0.01)
    # Flaky: on a loaded CI runner the elapsed time can exceed the bound
    assert time.time() - start < 0.02

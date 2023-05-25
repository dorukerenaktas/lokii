import time

from lokii.util.perf_timer_context import PerfTimerContext


def test_timer_should_track_elapsed_time():
    with PerfTimerContext() as t:
        time.sleep(0.1)
    assert 0.1 == round(t.time, 1)


def test_timer_should_track_only_in_context():
    with PerfTimerContext() as t:
        time.sleep(0.1)
    time.sleep(0.2)
    assert 0.1 == round(t.time, 1)


def test_timer_print_two_digits_over_seconds():
    t = PerfTimerContext()
    t.time = 1.1234
    assert "1.12s" == str(t)


def test_timer_print_four_digits_under_seconds():
    t = PerfTimerContext()
    t.time = 0.1234
    assert "0.1234s" == str(t)

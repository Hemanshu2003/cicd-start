# tests/test_signals.py
# ─────────────────────────────────────────────────────────────────
# Unit Tests — Signal Generation Logic
# ─────────────────────────────────────────────────────────────────
import pytest
from app.worker.tasks import generate_signal


class TestSignalGeneration:

    def test_strong_buy_oversold_positive_macd_diff(self):
        # RSI < 30, MACD line above signal → STRONG_BUY
        signal = generate_signal(rsi=25.0, macd_value=0.05, macd_signal=-0.01)
        assert signal == "STRONG_BUY"

    def test_strong_sell_overbought_negative_macd_diff(self):
        # RSI > 70, MACD line below signal → STRONG_SELL
        signal = generate_signal(rsi=75.0, macd_value=-0.05, macd_signal=0.01)
        assert signal == "STRONG_SELL"

    def test_buy_moderate_rsi_positive_macd(self):
        signal = generate_signal(rsi=40.0, macd_value=0.03, macd_signal=0.05)
        assert signal == "BUY"

    def test_sell_moderate_rsi_negative_macd(self):
        signal = generate_signal(rsi=60.0, macd_value=-0.02, macd_signal=-0.01)
        assert signal == "SELL"

    def test_hold_neutral_conditions(self):
        signal = generate_signal(rsi=50.0, macd_value=0.001, macd_signal=0.001)
        assert signal == "HOLD"

    def test_hold_rsi_boundary_exactly_50(self):
        signal = generate_signal(rsi=50.0, macd_value=0.0, macd_signal=0.0)
        assert signal == "HOLD"

    def test_strong_buy_boundary_rsi_29(self):
        signal = generate_signal(rsi=29.9, macd_value=0.1, macd_signal=0.05)
        assert signal == "STRONG_BUY"

    def test_strong_sell_boundary_rsi_71(self):
        signal = generate_signal(rsi=71.0, macd_value=-0.1, macd_signal=0.05)
        assert signal == "STRONG_SELL"

    @pytest.mark.parametrize("rsi,macd_value,macd_signal,expected", [
        (20.0,  0.10,  0.05, "STRONG_BUY"),
        (80.0, -0.10, -0.05, "STRONG_SELL"),
        (42.0,  0.05,  0.03, "BUY"),
        (58.0, -0.03, -0.01, "SELL"),
        (50.0,  0.00,  0.00, "HOLD"),
    ])
    def test_signal_parametrized(self, rsi, macd_value, macd_signal, expected):
        assert generate_signal(rsi, macd_value, macd_signal) == expected

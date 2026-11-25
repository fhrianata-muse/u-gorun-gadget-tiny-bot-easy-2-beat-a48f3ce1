"""Dip-buy bot for u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1.

Strategy (measured first, in run163 Tahap 1, on the kit's dev window):
buy an asset when its close is more than 5% below its close 24 bars ago,
hold it for 6 bars, then sell. At most 25% of equity per asset (the
harness cap), at most 4 positions at once. Everything else stays in cash.

Why this rule: on the dev window (136 hourly bars, 29 Oct-3 Nov 2026) the
market fell 8.5% and momentum was anti-predictive (past winners kept
falling), while 24-hour losers bounced: forward 6h return after a
past-24h drop of more than 5% had median +0.85% and 72% of cases positive.
The full replay of this rule on the dev window, with the harness's own
execution lag (orders decided on bar k fill at bar k+1's open), fees
(10 bps) and slippage (5 bps), gave Net PnL +415.63 USDC against
buy-and-hold -869.34 USDC, 33 trades, max drawdown 2.36%.

Honest limit, recorded with the entry: the dev profit is concentrated in
one crash-and-bounce event (bars 24-48 of the window) and the signal did
not replicate in the window's second half. The final window (27-30 Nov)
is future prices; this bot wins if that window falls or whipsaws, and
loses to buy-and-hold if it rises steadily.

Deterministic: no clock, no environment, no randomness. The same bars
always produce the same orders.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

LOOKBACK = 24          # bars of past return that define a "dip"
DROP_BPS = -500        # buy when past-24h return is below -5%
HOLD_BARS = 6          # bars to hold after the fill bar
MAX_POSITIONS = 4      # most assets held at once
MAX_SLIPPAGE_BPS = 10000  # wide open, like the buy-and-hold baseline: a fill
# is never refused for the open having moved; the fill price is the
# harness's open price moved by its modelled slippage and impact.

SYMBOLS = ["FARTCOIN", "JITOSOL", "POPCAT", "RAY", "SOL", "WETH", "WIF"]

history = {s: [] for s in SYMBOLS}   # closes, oldest first
held_since = {}                      # symbol -> seq of the bar its fill landed


def past_return(symbol):
    closes = history[symbol]
    if len(closes) <= LOOKBACK:
        return None
    now = closes[-1]
    then = closes[-1 - LOOKBACK]
    if then == 0:
        return None
    return (now - then) * 10000 // then  # in bps, integer math


def on_batch(state, batch):
    for symbol in SYMBOLS:
        close = state.close(symbol)
        if close is not None:
            history[symbol].append(close)

    # A position first visible in this batch was filled on this bar.
    for symbol in list(state.positions):
        if symbol not in held_since:
            held_since[symbol] = state.seq
    for symbol in list(held_since):
        if symbol not in state.positions:
            del held_since[symbol]

    if state.warming_up:
        return []

    equity = state.equity
    target = {}  # symbol -> target weight in bps of equity

    for symbol in SYMBOLS:
        if symbol in state.positions:
            if state.seq - held_since.get(symbol, state.seq) >= HOLD_BARS:
                target[symbol] = 0
            else:
                held = state.positions[symbol]
                target[symbol] = state.value(symbol, held.qty) * 10000 // equity if equity else 0
        else:
            ret = past_return(symbol)
            if ret is not None and ret < DROP_BPS:
                target[symbol] = 2500

    # At most MAX_POSITIONS names held at once: keep the deepest dips.
    wanted = [s for s, w in target.items() if w > 0]
    if len(wanted) > MAX_POSITIONS:
        wanted.sort(key=lambda s: (past_return(s), SYMBOLS.index(s)))
        keep = set(wanted[:MAX_POSITIONS])
        for symbol in list(target):
            if target[symbol] > 0 and symbol not in keep:
                # A held symbol dropped by the cap is sold; a new
                # candidate dropped by the cap is simply not bought.
                if symbol in state.positions:
                    target[symbol] = 0
                else:
                    del target[symbol]

    orders = []
    for symbol in SYMBOLS:
        held = state.positions.get(symbol)
        cur_value = state.value(symbol, held.qty) if held else 0
        want_value = target.get(symbol, 0) * equity // 10000
        if cur_value > want_value + 1 and held:
            qty = held.qty * (cur_value - want_value) // cur_value if want_value > 0 else held.qty
            if qty > 0:
                orders.append({"side": "sell", "symbol": symbol, "qty": qty,
                               "max_slippage_bps": MAX_SLIPPAGE_BPS})

    cash_left = state.cash
    for symbol in SYMBOLS:
        held = state.positions.get(symbol)
        cur_value = state.value(symbol, held.qty) if held else 0
        want_value = target.get(symbol, 0) * equity // 10000
        if want_value > cur_value + 1:
            room = state.weight_room(symbol)
            amount = want_value - cur_value
            if amount > room:
                amount = room
            if amount > cash_left:
                amount = cash_left
            if amount >= 1000000:  # harness minimum notional: 1 USDC
                orders.append({"side": "buy", "symbol": symbol,
                               "notional_quote_units": amount,
                               "max_slippage_bps": MAX_SLIPPAGE_BPS})
                cash_left -= amount

    return orders


makefun_bars.run(on_batch)

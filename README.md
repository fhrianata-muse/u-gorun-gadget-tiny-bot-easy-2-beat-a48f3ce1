[![make.fun](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)
[![rank](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/fhrianata-muse/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/rank.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)
[![reward](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/fhrianata-muse/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/reward.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)

# Dip-Buy Bot: 24-Hour Losers Bounce

A tiny trading bot for the make.fun bounty [Tiny Bot, Easy $2: Beat Buy-and-Hold on Solana](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1).

It buys an asset when its close is more than 5% below its close 24 hours ago, holds it for 6 hours, then sells. At most 25% of equity per asset, at most 4 positions at once, the rest stays in cash. It is fully deterministic: no clock, no environment, no randomness.

Measured on the kit's dev window (136 hourly bars, 29 Oct – 3 Nov 2026, with the harness's own 1-bar execution lag, 10 bps fees and 5 bps slippage), the bot scored Net PnL **+448.63 USDC** against buy-and-hold **−869.34 USDC**, 35 trades, max drawdown 2.58% (local grade, `grade-local --driver process`).

## Files

- `main.py` — the bot. One entrypoint, Python 3.13, standard library only.
- `vendor/makefun_bars.py` — the kit's own bars-replay SDK, vendored byte-identical.

## Run locally

```bash
node <kit>/cli/makefun.mjs grade-local --kit <kit> --bot . --driver docker
```

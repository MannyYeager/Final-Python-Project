# Cedi — a multi-currency wallet lab

A local Python wallet application with separate **Overview**, **Move money**, **Activity**, **Rates & insights** and **Payment methods** sections. Funds and payment methods are simulated. Currency reference rates and historical observations come from the real Frankfurter API.

## Run

Requires Python 3.10+. No third-party Python packages, API keys or frontend build are needed.

```sh
python web.py
```

Open http://127.0.0.1:8766/ . Use `--port 8771` for another loopback port. For disconnected development, run `python web.py --offline`; example rates are visibly labelled and no historical graph is invented.

## Explore

- Change the balance-display currency between GHS, USD, GBP, EUR and West African CFA franc (XOF). The wallet holds a single GHS balance; changing the view does not exchange funds.
- Add money from a demo card, bank account or mobile-money wallet. Choose a currency, amount, saved method and optional note, then review the GHS amount, rate, source, date, zero simulation fee and resulting balance.
- Withdraw a chosen amount or the entire balance to a saved destination. The review quote lasts two minutes, retains its conversion rate and prevents duplicate submissions. A changed balance requires a new review.
- Save up to eight demo methods using a label and four example ending digits. No full card/account numbers or CVVs are requested. No payment processor is connected.
- Open transaction receipts, search/filter activity, export CSV, and set a personal GHS savings target.
- Explore selectable currency pairs over 7, 30 or 90 days. The chart has an observation readout and an accessible data table. Blank dates are not interpolated into fabricated observations.

## Reference-rate integration

[Frankfurter v2](https://frankfurter.dev/) provides latest and historical blended reference rates without a key. Reference rates are published daily or a few times per day; they are not streaming trading quotes. The server requests only currency codes and date ranges, never wallet data or method labels.

`exchange.py` inverts GHS-base quotes into GHS per unit for shared Decimal conversion. Latest rates cache for 15 minutes; historical series cache for one hour. Network calls have bounded timeouts/retries and response-size limits. If latest retrieval fails, the last retrieved reference rates are labelled cached/stale; without a previous observation, clearly labelled teaching rates are used. Failed history requests show an error and retry control, never a fake graph.

Transactions retain their quoted rate and method snapshot, so later rate changes do not rewrite receipts. GHS is the base currency and needs no conversion. API currency aliases preserve the original `EURO` and `CFA` internals while presenting EUR and XOF.

## Original terminal application

```sh
python app.py
```

The terminal interface retains its fixed teaching rates from `rates.py`. The shared `Wallet` class accepts an optional per-instance rate table; its default still uses the original examples. Decimal validation/rounding and invalid-withdrawal protection apply to both interfaces.

## Verify

```sh
python -m unittest -v
node --check static/app.js
node --check static/ui.js
node test_motion.cjs
```

Tests use deterministic injected/offline rates; they never depend on an external API being available. Coverage includes Decimal operations, invalid inputs, session isolation, method validation, quote expiry/idempotency, changed balances, rate inversion/caching, explicit outage behavior, history validation, CSV and local request/file boundaries.

## Runtime and limits

The standard-library server binds only to loopback, restricts Host/Origin, uses HttpOnly same-site session cookies and serves an explicit asset whitelist under a self-only script policy. Each browser has an isolated in-memory wallet. Sessions expire after eight hours and all session data resets when the server stops. This is a portfolio simulation, not a bank or payment service.

Anime.js 4.5.0 and its MIT license are vendored in `static/vendor/`. Custom SVG icons, animated entrances and feedback work offline and respect reduced-motion preferences. `static/workspace.css` contains the expanded workspace layouts. No public deployment is required.

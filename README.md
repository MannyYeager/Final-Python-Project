# E-Wallet Converter

A Python e-wallet simulation with a working web dashboard and the original terminal interface. Deposit or withdraw in five currencies, inspect equivalent balances, and follow each transaction in a session activity list. The web interface uses the existing `Wallet` class and its decimal arithmetic.

**This is a simulation.** The rates are fixed teaching examples, not current exchange rates. No money moves, no financial account is created, and the balance disappears when the program exits.

## Open the web app

Requires **Python 3.11 or newer** and only the standard library.

```sh
git clone https://github.com/MannyYeager/Final-Python-Project.git
cd Final-Python-Project
python web.py
```

Open **http://127.0.0.1:8766/**. Use `--port 8771` if that port is occupied. No frontend build, packages, or API keys are needed.

Try **10 USD** as a deposit: the balance becomes **GHS 114.80**. Switch to **Withdraw**, choose **GHS**, and enter **25**: the balance becomes **GHS 89.80**. An oversized withdrawal shows an error without changing the balance or activity list. The full-withdrawal option pays out the selected currency's rounded equivalent and clears the simulated balance.

Each browser cookie session has an independent wallet and activity list. Refreshes retain that session; it expires after eight hours, and all data is discarded when the server stops. The interface calls the Python backend for every transaction. The on-screen pre-submit quote is approximate; the server's Decimal result determines the balance. The server binds only to `127.0.0.1`.

## Run the original terminal app

Requires **Python 3.11 or newer** and only the standard library.

```sh
git clone https://github.com/MannyYeager/Final-Python-Project.git
cd Final-Python-Project
python app.py
```

On Windows, `py app.py` also works. On macOS/Linux, use `python3 app.py` if needed.

The menu offers deposits, partial withdrawals, full withdrawals, and a balance view in every supported currency. Invalid numbers, nonfinite values, unsupported currencies, and insufficient funds leave the balance unchanged. EOF or Ctrl+C exits cleanly.

## Example session

| Step | Menu selection | Input | GHS balance |
| --- | --- | --- | ---: |
| Deposit cedis | `1` | `100` | 100.00 |
| Withdraw cedis | `6`, then `2` | `25` | 75.00 |
| Deposit US dollars | `2` | `10` | 189.80 |
| View all currencies | `11` | — | 189.80 |
| Exit | `12` | — | Session ends |

Press Enter after each result to return to the menu. Partial GHS withdrawals now use the same conversion rules as the other currencies.

You can also use the class directly:

```python
from wallet import Wallet

wallet = Wallet("Ama")
print(wallet.deposit("100", "GHS"))
print(wallet.withdrawal("25", "GHS"))
# Available balance: GHS 75.00
print(wallet.check_balance())
```

## Fixed example rates

These constants live in `rates.py` and represent **GHS per one foreign currency unit**. They have no claim to a current market date.

| Currency | Example GHS value |
| --- | ---: |
| GHS | 1.00 |
| USD | 11.48 |
| GBP | 15.57 |
| EURO | 13.45 |
| CFA | 0.021 |

The class also accepts `GH₵` as GHS and `EUR` as EURO. Currency codes are case-insensitive.

Balances use `Decimal`. Each converted transaction is rounded to two GHS decimal places using half-up rounding; converted values that round to zero are rejected. Amounts must be positive, finite, and no greater than 1,000,000,000 per transaction. A full withdrawal shows the selected currency rounded to two places and clears the entire simulated GHS balance, including conversion rounding differences. If that payout would round to zero, the balance is preserved.

## Verify

```sh
python -m unittest -v
```

Regression tests cover all five currencies, partial GHS withdrawals, invalid-currency full withdrawals, insufficient funds, nonnumeric/NaN/infinite input, rounding, recovery after invalid terminal input, HTTP transactions, per-browser isolation, activity records, and request boundaries.

| File | Responsibility |
| --- | --- |
| `app.py` | Terminal menus and input |
| `wallet.py` | Balance and transaction rules |
| `rates.py` | Fixed teaching rates |
| `test_wallet.py` | Unit tests and a terminal walkthrough |
| `web.py`, `local_web.py` | Session wallet API and loopback HTTP server |
| `static/` | HTML/CSS/JavaScript dashboard, forms, and activity view |
| `test_web.py` | HTTP regression tests |

This project has no durable storage, fees, live-rate API, or payment-service integration. The web activity list is an educational session history, not an audited financial ledger. Stop the web server with Ctrl+C.

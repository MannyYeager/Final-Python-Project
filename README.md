# E-Wallet Converter

A Python terminal project that simulates deposits and withdrawals in five currencies, using a Ghana cedi (GHS) balance. It demonstrates classes, currency conversion, validated user input, and decimal arithmetic.

**This is a simulation.** The rates are fixed teaching examples, not current exchange rates. No money moves, no financial account is created, and the balance disappears when the program exits.

## Run

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

Regression tests cover all five currencies, partial GHS withdrawals, invalid-currency full withdrawals, insufficient funds, nonnumeric/NaN/infinite input, rounding, and recovery after invalid terminal input.

| File | Responsibility |
| --- | --- |
| `app.py` | Terminal menus and input |
| `wallet.py` | Balance and transaction rules |
| `rates.py` | Fixed teaching rates |
| `test_wallet.py` | Unit tests and a terminal walkthrough |

This project has no persistence, fees, live-rate API, transaction ledger, or payment-service integration.

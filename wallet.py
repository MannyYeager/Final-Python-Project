"""In-memory wallet simulation with fixed example rates and a GHS balance."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
import rates as rs

RATES = {"GHS": Decimal("1"), "USD": Decimal(str(rs.USD)),
         "GBP": Decimal(str(rs.GBP)), "EURO": Decimal(str(rs.EURO)),
         "CFA": Decimal(str(rs.CFA))}
ALIASES = {"GH₵": "GHS", "EUR": "EURO"}
CENT = Decimal("0.01")
MAX_AMOUNT = Decimal("1000000000")


def currency_code(currency):
    code = str(currency).strip().upper()
    return ALIASES.get(code, code)


def positive_amount(amount):
    try:
        value = Decimal(str(amount))
    except (InvalidOperation, ValueError):
        raise ValueError("Enter a valid numeric amount.") from None
    if not value.is_finite() or value <= 0 or value > MAX_AMOUNT:
        raise ValueError("Amount must be finite, greater than 0, and at most 1,000,000,000.")
    return value


def money(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


class Wallet:
    def __init__(self, user, rates=None):
        self.user = user
        self.balance = Decimal("0.00")
        self.rates = dict(RATES if rates is None else rates)

    def _converted_amount(self, amount, currency):
        code = currency_code(currency)
        if code not in self.rates:
            raise ValueError("Invalid Currency")
        with localcontext() as context:
            context.prec = 28
            value = money(positive_amount(amount) * self.rates[code])
        if value <= 0:
            raise ValueError("Amount is too small: its GHS value rounds to 0.00.")
        return code, value

    def deposit(self, amount, currency):
        try:
            code, value = self._converted_amount(amount, currency)
        except ValueError as error:
            return str(error)
        self.balance += value
        return (f"Deposited currency: {code}\n"
                f"Deposit amount: {amount}\n"
                f"Converted to GHS: {value:.2f}\n"
                f"Available balance: GHS {self.balance:.2f}")

    def withdrawal(self, amount, currency):
        try:
            code, value = self._converted_amount(amount, currency)
        except ValueError as error:
            return str(error)
        if value > self.balance:
            return "Insufficient Balance"
        self.balance -= value
        return (f"Withdrawal currency: {code}\n"
                f"Withdrawal amount: {amount}\n"
                f"Amount deducted: GHS {value:.2f}\n"
                f"Available balance: GHS {self.balance:.2f}")

    def withdraw_all(self, currency):
        code = currency_code(currency)
        if code not in self.rates:
            return "Invalid Currency"
        if self.balance <= 0:
            return "No balance available to withdraw."
        amount = money(self.balance / self.rates[code])
        if amount <= 0:
            return "Balance is too small to withdraw in this currency."
        self.balance = Decimal("0.00")
        return (f"Withdrawal currency: {code}\n"
                "Withdrawal type: Full\n"
                f"Withdrawal amount: {amount:.2f}\n"
                "Available balance: GHS 0.00")

    def check_balance(self):
        lines = ["--- Simulated Account Balance ---"]
        for code, rate in self.rates.items():
            lines.append(f"{code} balance: {money(self.balance / rate):.2f}")
        return "\n".join(lines)

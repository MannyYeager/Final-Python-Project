from decimal import Decimal
from pathlib import Path
import subprocess
import sys
import unittest

from wallet import Wallet, RATES


class WalletTests(unittest.TestCase):
    def test_partial_ghs_withdrawal(self):
        wallet = Wallet("Ama")
        wallet.deposit(100, "GH₵")
        result = wallet.withdrawal(25, "GH₵")
        self.assertIn("GHS 75.00", result)
        self.assertEqual(wallet.balance, Decimal("75.00"))

    def test_each_currency_deposit_and_withdrawal(self):
        for currency in RATES:
            with self.subTest(currency=currency):
                wallet = Wallet("Ama")
                wallet.deposit(100, currency)
                self.assertGreater(wallet.balance, 0)
                wallet.withdrawal(100, currency)
                self.assertEqual(wallet.balance, 0)

    def test_invalid_currency_never_changes_balance(self):
        wallet = Wallet("Ama")
        wallet.deposit(100, "GHS")
        for operation in (wallet.deposit, wallet.withdrawal):
            self.assertEqual(operation(10, "INVALID"), "Invalid Currency")
        self.assertEqual(wallet.withdraw_all("INVALID"), "Invalid Currency")
        self.assertEqual(wallet.balance, Decimal("100.00"))

    def test_invalid_and_nonfinite_amounts_never_change_balance(self):
        wallet = Wallet("Ama")
        wallet.deposit(100, "GHS")
        for amount in ("abc", "", 0, -1, "NaN", "Infinity", "-Infinity", "1e10000", "0.00001"):
            for operation in (wallet.deposit, wallet.withdrawal):
                with self.subTest(amount=amount, operation=operation.__name__):
                    operation(amount, "GHS")
                    self.assertEqual(wallet.balance, Decimal("100.00"))

    def test_insufficient_balance_and_full_withdrawal(self):
        wallet = Wallet("Ama")
        wallet.deposit(10, "USD")
        self.assertEqual(wallet.withdrawal(11, "USD"), "Insufficient Balance")
        self.assertEqual(wallet.balance, Decimal("114.80"))
        self.assertIn("Withdrawal amount: 10.00", wallet.withdraw_all("USD"))
        self.assertEqual(wallet.balance, 0)

    def test_decimal_rounding_and_aliases(self):
        wallet = Wallet("Ama")
        for _ in range(10):
            wallet.deposit("0.1", "ghs")
        self.assertEqual(wallet.balance, Decimal("1.00"))
        wallet.deposit(1, "EUR")
        self.assertEqual(wallet.balance, Decimal("14.45"))

    def test_full_withdrawal_that_rounds_to_zero_preserves_balance(self):
        wallet = Wallet("Ama")
        wallet.deposit("0.01", "GHS")
        self.assertIn("too small", wallet.withdraw_all("GBP"))
        self.assertEqual(wallet.balance, Decimal("0.01"))

    def test_cli_handles_bad_amount_then_recovers(self):
        result = subprocess.run([sys.executable, "app.py"], input="Ama\n1\nhello\n\n1\n100\n\n6\n2\n25\n\n12\n",
                                text=True, capture_output=True, cwd=Path(__file__).parent, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("valid numeric amount", result.stdout)
        self.assertIn("GHS 75.00", result.stdout)
        self.assertIn("SIMULATION", result.stdout)


if __name__ == "__main__":
    unittest.main()

"""Browser interface for the existing Wallet class. Run: python web.py"""
import argparse
from datetime import datetime, timezone
from pathlib import Path

from local_web import LocalServer
from wallet import Wallet, RATES, currency_code, money


class WalletServer(LocalServer):
    def __init__(self, address):
        super().__init__(address, Path(__file__).with_name("static"), "wallet_lab_session",
                         lambda: {"wallet": Wallet("Your wallet"), "history": []})

    def snapshot(self, data):
        wallet = data['wallet']
        return {"balance": str(wallet.balance), "name": wallet.user, "simulation": True,
                "currencies": [{"code": code, "rate": str(rate), "balance": str(money(wallet.balance / rate))}
                               for code, rate in RATES.items()], "history": list(reversed(data['history']))}

    def action(self, path, payload, data):
        if path != "/api/transaction":
            raise ValueError("Unknown wallet action.")
        kind = payload.get('kind')
        currency = payload.get('currency', '')
        amount = payload.get('amount', '')
        if not isinstance(kind, str) or kind not in {'deposit', 'withdraw', 'withdraw_all'} or not isinstance(currency, str):
            raise ValueError("Choose a transaction and currency.")
        if not isinstance(amount, (str, int, float)) or isinstance(amount, bool):
            raise ValueError("Enter a numeric amount.")
        wallet = data['wallet']
        before = wallet.balance
        result = (wallet.withdraw_all(currency) if kind == 'withdraw_all' else
                  wallet.deposit(amount, currency) if kind == 'deposit' else wallet.withdrawal(amount, currency))
        if wallet.balance == before:
            raise ValueError(result)
        delta = wallet.balance - before
        code = currency_code(currency)
        payout = str(money(before / RATES[code])) if kind == 'withdraw_all' else str(amount)
        data['history'].append({"kind": kind, "currency": code, "amount": payout,
                                "ghs": str(abs(delta)), "balance": str(wallet.balance),
                                "time": datetime.now(timezone.utc).strftime("%H:%M UTC")})
        return f"{'Deposit added' if delta > 0 else 'Withdrawal completed'}. Your simulated balance is GHS {wallet.balance:.2f}."


def main():
    parser = argparse.ArgumentParser(description="E-Wallet Converter local web demo")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    with WalletServer(("127.0.0.1", args.port)) as server:
        print(f"Wallet preview: http://127.0.0.1:{server.server_port}/", flush=True)
        print("Simulation only. Each browser has its own in-memory wallet.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nWallet closed.")


if __name__ == "__main__":
    main()

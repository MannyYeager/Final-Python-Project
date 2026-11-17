"""Terminal interface for the educational e-wallet converter."""
import os
from wallet import Wallet

CURRENCIES = ("GHS", "USD", "GBP", "EURO", "CFA")


def clear():
    if os.isatty(1):
        os.system("cls" if os.name == "nt" else "clear")


def main():
    print("--- E-Wallet Converter ---")
    print("SIMULATION: fixed example rates; no real money or payment services.")
    user = input("Enter your name: ").strip() or "Guest"
    wallet = Wallet(user)
    while True:
        clear()
        print(f"\nWelcome {wallet.user} | Simulated balance: GHS {wallet.balance:.2f}")
        print("Fixed example rates | Session data is discarded on exit.")
        for number, currency in enumerate(CURRENCIES, 1):
            print(f"{number}. Deposit {currency}")
        for number, currency in enumerate(CURRENCIES, 6):
            print(f"{number}. Withdraw {currency}")
        print("11. Check balance (all currencies)\n12. Exit")
        choice = input("Enter choice (1-12): ").strip()
        if choice == "12":
            print("Thank you. Simulation ended.")
            return
        if choice == "11":
            print(wallet.check_balance())
        elif choice in {str(i) for i in range(1, 11)}:
            option = int(choice)
            currency = CURRENCIES[(option - 1) % 5]
            if option <= 5:
                amount = input(f"Enter amount in {currency}: ").strip()
                print(wallet.deposit(amount, currency))
            else:
                print("1. Withdraw all\n2. Withdraw a specific amount")
                mode = input("Choose either 1 or 2: ").strip()
                if mode == "1":
                    print(wallet.withdraw_all(currency))
                elif mode == "2":
                    amount = input(f"Enter amount in {currency}: ").strip()
                    print(wallet.withdrawal(amount, currency))
                else:
                    print("Invalid withdrawal option. Choose 1 or 2.")
        else:
            print("Invalid option. Choose a number from 1 to 12.")
        input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nSimulation ended.")

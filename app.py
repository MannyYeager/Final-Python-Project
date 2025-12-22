import os
from wallet import Wallet

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

print('-------------------------E-Wallet Converter-------------------------')

user = input("Enter your name: ")

wallet = Wallet(user)

clear()
print(f"Welcome {user}")
input("Please press enter to continue..........") 

while True:
    clear()
    print("\nChoose an option")
    print("1. Deposit GH₵.")
    print("2. Deposit USD.")
    print("3. Deposit GBP.")
    print("4. Deposit EURO.")
    print("5. Deposit CFA.")
    print("6. Withdraw GH₵.")
    print("7. Withdraw USD.")
    print("8. Withdraw GBP.")
    print("9. Withdraw EURO.")
    print("10. Withdraw CFA.")
    print("11. Check available balance(All currencies).")
    print("12. Exit.")
    
    choice = input("Enter choice (1-12): ")
    
    if choice == '1':
        clear()
        amount = float(input("Enter amount in GH₵: "))  
        clear()
        print(wallet.deposit(amount, "GH₵"))
        input("Please press enter to continue..........")
        
    elif choice == '2':
        clear()
        amount = float(input("Enter amount in USD: "))
        clear()
        print(wallet.deposit(amount, "USD"))
        input("Please press enter to continue..........") 
        
    elif choice == '3':
        clear()
        amount = float(input("Enter amount in GBP: "))
        clear()
        print(wallet.deposit(amount, "GBP"))
        input("Please press enter to continue..........") 
        
    elif choice == '4':
        clear()
        amount = float(input("Enter amount in EURO: "))
        clear()
        print(wallet.deposit(amount, "EURO"))
        input("Please press enter to continue..........") 
        
    elif choice == '5':
        clear()
        amount = float(input("Enter amount in CFA: "))
        clear()
        print(wallet.deposit(amount, "CFA"))
        input("Please press enter to continue..........") 
        
    elif choice == '6': 
        clear()
        print("1. Withdraw all")
        print("2. Withdraw a specific amount")
        sub_choice = input("Choose either 1 or 2: ")
        
        if sub_choice == '1':
            result = wallet.withdraw_all("GH₵")
            clear()
            print(result)
            input("Please press enter to continue..........")
        
        if sub_choice == '2':
            clear()
            amount = float(input("Enter amount in GH₵: "))
            print(wallet.withdrawal(amount, "GH₵"))
            input("Please press enter to continue..........")
        
    elif choice == '7':
        clear()
        print("1. Withdraw all")
        print("2. Withdraw a specific amount")
        sub_choice = input("Choose either 1 or 2: ")
        
        if sub_choice == '1':
            result = wallet.withdraw_all("USD")
            clear()
            print(result)
            input("Please press enter to continue..........")
        
        if sub_choice == '2':
            clear()
            amount = float(input("Enter amount in USD: "))
            print(wallet.withdrawal(amount, "USD"))
            input("Please press enter to continue..........")
        
    elif choice == '8':
        clear()
        print("1. Withdraw all")
        print("2. Withdraw a specific amount")
        sub_choice = input("Choose either 1 or 2: ")
        
        if sub_choice == '1':
            result = wallet.withdraw_all("GBP")
            clear()
            print(result)
            input("Please press enter to continue..........")
        
        if sub_choice == '2':
            clear()
            amount = float(input("Enter amount in GBP: "))
            print(wallet.withdrawal(amount, "GBP"))
            input("Please press enter to continue..........") 
        
    elif choice == '9': 
        clear()
        print("1. Withdraw all")
        print("2. Withdraw a specific amount")
        sub_choice = input("Choose either 1 or 2: ")
        
        if sub_choice == '1':
            result = wallet.withdraw_all("EURO")
            clear()
            print(result)
            input("Please press enter to continue..........")
        
        if sub_choice == '2':
            clear()
            amount = float(input("Enter amount in EURO: "))
            print(wallet.withdrawal(amount, "EURO"))
            input("Please press enter to continue..........")
        
    elif choice == '10':
        clear()
        print("1. Withdraw all")
        print("2. Withdraw a specific amount")
        sub_choice = input("Choose either 1 or 2: ")
        
        if sub_choice == '1':
            result = wallet.withdraw_all("CFA")
            clear()
            print(result)
            input("Please press enter to continue..........")
        
        if sub_choice == '2':
            clear()
            amount = float(input("Enter amount in CFA: "))
            print(wallet.withdrawal(amount, "CFA"))
            input("Please press enter to continue..........")  
    
    elif choice == '11':
        result =wallet.check_balance()
        clear()
        print(result)
        input("Please press enter to continue..........")
        
    elif choice == '12':
        print("Thank you.")
        break
    
    else:
        clear()
        print("Invalid Option, Try again.")   
        input("Please press enter to continue..........")          
        continue               
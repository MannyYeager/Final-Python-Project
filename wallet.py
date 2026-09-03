#Note: The base currency is "Cedis"
import rates as rs

class Wallet:
    def __init__(self, user):
        self.user = user
        self.balance = 0.0
        
    def deposit(self, amount, currency):
        if amount <= 0:
            return "The deposit amount must be greater than 0"
        
        elif currency == "GH₵":
            value = amount
            
        elif currency == "USD":
            value = amount * rs.USD
            
        elif currency == "GBP":
            value = amount * rs.GBP
            
        elif currency == "EURO":
            value = amount * rs.EURO
            
        elif currency == "CFA":
            value = amount * rs.CFA
        
        else:
            return "Invalid Currency"    
        
        self.balance += value
        
        return (
          f"\nDeposited currency : {currency}\n"
          f"Current amount : {amount}\n"
          f"Convert to ghs : {round(value, 2)}\n"
          f"Avaible new balance : {round(self.balance, 2)}"
        )  
        
        
        
    def withdrawal(self, amount, currency):
        if amount <= 0:
            return "The withdrawal amount must be greater than 0"  
        
        elif currency == "USD":
            converted_value = amount * rs.USD
            
        elif currency == "GBP":
            converted_value = amount * rs.GBP
            
        elif currency == "EURO":
            converted_value = amount * rs.EURO
            
        elif currency == "CFA":
            converted_value = amount * rs.CFA
            
        else: 
            return "Invalid Currency"
        
        if converted_value > self.balance:
            return "Insuficient Balance"
       
        self.balance -= converted_value                 
        
        return (
            f"\nWithdrawal Currency : {currency}\n"
            f"Current withdrawal : {amount}\n"
            f"Amount deducted : {round(converted_value, 2)}\n"
            f"New amount : {round(self.balance, 2)}"
        )
        
    def withdraw_all(self, currency):
        
        available_balance = self.balance
        withdrawal_amount = 0.0
        
        if available_balance <= 0:
            return "The withdrawal amount must be greater than 0"  
        
        elif currency == "GH₵":
            withdrawal_amount = self.balance
             
        elif currency == "USD":
            withdrawal_amount = self.balance / rs.USD
            
        elif currency == "GBP":
            withdrawal_amount = self.balance / rs.GBP
            
        elif currency == "EURO":
            withdrawal_amount = self.balance / rs.EURO
            
        elif currency == "CFA":
            withdrawal_amount = self.balance / rs.CFA               
        
        self.balance = 0.0
        
        return(
            f"\nWithdrawal currency: {currency}"
            f"\nWithdrawal Type : Full"
            f"\nWithdrawal Amount : {round(withdrawal_amount, 2)}"
            f"\nAvailable Balance : {self.balance}"
        )
        
    def check_balance(self):
        if self.balance <= 0:
            return "Your account balance is GH₵ 0.0"

        return (
            "----------------------Account Balance----------------------"
            f"\nGH₵ balance: ₵{round(self.balance, 2)}"
            f"\nUSD balance: ${round(self.balance / rs.USD, 2)}"
            f"\nGBP balance: £{round(self.balance / rs.GBP, 2)}"
            f"\nEURO balance: €{round(self.balance / rs.EURO, 2)}"
            f"\nCFA balance: {round(self.balance / rs.CFA, 2)}"
        )

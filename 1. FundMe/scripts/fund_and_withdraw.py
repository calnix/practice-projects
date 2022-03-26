from brownie import FundMe
from scripts.helpful_scripts import get_account
import pytest


def fund():
    fund_me = FundMe[-1]
    account = get_account()
    entrance_fee = fund_me.getEntranceFee()
    
    print(f"Current entry free is:{entrance_fee}") #you should get 2500001
    print("funding...")
    fund_me.fund({"from":account, "value": entrance_fee})
    print("Funded...")

def withdraw():
    fund_me = FundMe[-1]
    account = get_account()
  
    fund_me.withdraw({"from":account})
    print("withdrawed.....")



def main():
    fund()
    withdraw()
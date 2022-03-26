# test_fund_me.py
import pytest
from brownie import FundMe, accounts, network, exceptions
from multiprocessing.connection import wait
from scripts.fund_and_withdraw import fund 
from scripts.helpful_scripts import *
from scripts.deploy import deploy_fund_me

def test_fund_withdraw():
    account = get_account()
    fund_me = deploy_fund_me()
    print(f"THIS WORKS {fund_me.address}")
    entrance_fee = fund_me.getEntranceFee() + 100
    tx = fund_me.fund({"from": account, "value": entrance_fee})
    tx.wait(1)
    print(entrance_fee)
    assert fund_me.addressToAmountFunded(account.address) == entrance_fee
    tx2 = fund_me.withdraw({"from": account})
    tx2.wait(1)
    assert fund_me.addressToAmountFunded(account.address) == 0


def test_OwnerWithdraw():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
       pytest.skip("ONLY FOR LOCAL TESTING!")

    if len(FundMe) <= 0: 
        fund_me = deploy_fund_me()
    fund_me = FundMe[-1]

    bad_actor = accounts.add()  
    with pytest.raises(exceptions.VirtualMachineError):
        fund_me.withdraw({"from": bad_actor})
        
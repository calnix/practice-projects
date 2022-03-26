# current eth price = 2925 -> fee = 50/2925 = 0.017094
from brownie import network, accounts, config
from brownie import Lottery
from web3 import Web3 

def test_entranceFee():
    account = accounts[0]
    lottery = Lottery.deploy(config["networks"][network.show_active()]["ethusd_pricefeed"],{"from": account})
    
    #print(lottery.getEntranceFee())  # <Transaction '0xe8680aebd07a93cb5627574022da5be8cfd0250f65f413f9cc134c592115bda6'>
    #print("..........")
    assert lottery.getEntranceFee() > Web3.toWei(0.014, "ether")
    assert lottery.getEntranceFee() < Web3.toWei(0.020, "ether")






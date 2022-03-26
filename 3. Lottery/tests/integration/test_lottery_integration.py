from brownie import network
import pytest
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENV, fund_with_link, get_account
from scripts.deploy import deploy
import time

def test_pick_winner(): # rinkeby test
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy()
    account = get_account()
    lottery.startLottery({"from": account})
    #ready players
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 100})
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 100})
    #end lottery + fund LINK
    fund_with_link(lottery)
    lottery.endLottery({"from": account})

    # wait for chainlink node to respond
    time.sleep(60) 

    assert lottery.recentWinner() == account
    assert lottery.balance == 0




    
    


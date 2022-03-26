# current eth price = 2925 -> fee = 50/2925 = 0.017094
from abc import get_cache_token
from urllib import request
from brownie import network, accounts, config, exceptions
from brownie import Lottery

from scripts.deploy import deploy
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENV, get_account, fund_with_link, get_contract

from web3 import Web3
import pytest

# Unit testing on development network 
def test_get_entranceFee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    # Arrange
    lottery = deploy()
    # Act
    # ETH/USD set to 2000. therefore, entrance_fee = 0.025 ETH
    entrance_fee = lottery.getEntranceFee()
    expected_entrance_fee = Web3.toWei(50/2000, "ether")
    # Assert
    assert expected_entrance_fee == entrance_fee


# test require:
# 1 - cannot enter unless lottery is started
# 2 - can enter if Open.

def test_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy()
    #curr_state = lottery.lottery_state(); print(curr_state)
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})    

def test_start_and_enter():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy()
    
    #Arrange: Owner sets lottery_state to Open
    lottery.startLottery({"from": get_account()}) 
    # Act: test enter
    lottery.enter({"from":get_account(), "value": lottery.getEntranceFee()})
    # Assert: if account has been added into array as player
    assert lottery.players(0) == account

def test_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy()
    #Arrange - to test end, must start with Open
    lottery.startLottery({"from": get_account()}) 
    lottery.enter({"from":get_account(), "value": lottery.getEntranceFee()})
    
    # Before ending, must fund with LINK
    tx = fund_with_link(contract_address=lottery.address)
    tx.wait(1)

    # Assert
    lottery.endLottery({"from": get_account()})
    assert lottery.lottery_state() == 2 # 2 -> calculating winner state


def test_can_pick_winner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy()
    account = get_account()

    #Arrange -  Owner starts and joins, 
    lottery.startLottery({"from": account}) 
    lottery.enter({"from": account, "value": lottery.getEntranceFee()}) #index = 0 -> Owner
    #Some players join
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()}) 
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})

    
    # Before ending, must fund with LINK
    tx = fund_with_link(contract_address=lottery.address)
    tx.wait(1)
    # get randomness
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestID"]    #from emitted event, extract requestID
    STATIC_RNG = 888
    get_contract("vrf_coordinator").callBackWithRandomness(request_id, STATIC_RNG, lottery.address, {"from": account})

    # 888/3 = 296, r=0. therefore winner is players(0)
    # balance should be 0, as winnings are transferred to winner.
    starting_balance_of_account  = account.balance()
    balance_of_lottery = lottery.balance()

    assert lottery.recentWinner() == account
    assert lottery.balance() == 0 
    assert account.balance() == starting_balance_of_account + balance_of_lottery






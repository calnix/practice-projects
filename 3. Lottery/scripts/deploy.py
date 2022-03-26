from brownie import Lottery, network, config
from scripts.helpful_scripts import fund_with_link, get_account, get_contract 
import time

def deploy():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("ethusd_pricefeed").address, 
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],{"from":account}, 
        publish_source = config["networks"][network.show_active()].get("verify", False))
        # get verify key, if it doesnt exist - default to false.
    print(".....Deployed lottery!.....")
    return lottery

def start_lottery():
    account = get_account()
    lottery = Lottery[-1]

    staring_tx = lottery.startLottery({"from": account})
    staring_tx.wait(1)
    print(".....Lottery is started!.....")

def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    entry_fee = lottery.getEntranceFee() + 10000000
    enter_tx = lottery.enter({"from": account, "value": entry_fee})
    enter_tx.wait(1)
    print(".....WE HAVE ENTERED LOTTERY!.....")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # need to fund link before we end, to get randonmess to select winner
    tx = fund_with_link(contract_address=lottery.address)
    tx.wait(1)
    end_tx = lottery.endLottery({"from":account})
    end_tx.wait(1)
    print(".....Lottery is Ended!.....")
    time.sleep(60)                                  #wait for VRF coord to callback
    print(f"Recent winner is {lottery.recentWinner()}")

def main():
    deploy()
    start_lottery()
    enter_lottery()
    end_lottery()


    # there is no chainlink node for the VRF coordinator to call and get randomess
    # there is no chainlink node in our private ganache.
    # so VRF will return 0x0000000000000000000000000000000000000000
    # to simulate VRF properly, we have to deploy to the testnet (rinkeby)

    # before we do that, we want to make sure all other tests clear.
    # make sure everthign else is solid on development chain first. 
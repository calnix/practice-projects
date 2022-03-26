from brownie import accounts, network, config
from brownie import MockV3Aggregator

DECIMAL_PLACES = 8          #to resemble eth/usd price feed on mainnet aggregator
STARTING_PRICE = (2000*10**8)
LOCAL_BLOCKCHAIN_ENV = ["development", "ganache-local"]
FORKED_LOCAL_ENV = ["mainnet-fork", "mainnet-fork-dev"]

def get_account():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV or network.show_active() in FORKED_LOCAL_ENV:
        return accounts[0]                                  #use ganache generated account.
    else:
        return accounts.add(config["wallets"]["wallet1"])  #look in config.yaml


def deploy_mocks():
        print(f"The active network is {network.show_active()}")
        print("Deploying.....")
        if len(MockV3Aggregator) <= 0:
            MockV3Aggregator.deploy(DECIMAL_PLACES,STARTING_PRICE,{"from":get_account()})  #contract object 
        print(f"Mocks Deployed at: {MockV3Aggregator[-1].address}")
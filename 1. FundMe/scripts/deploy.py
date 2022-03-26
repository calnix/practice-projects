from brownie import FundMe
from brownie import network, config
from scripts.helpful_scripts import *
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENV

def deploy_fund_me():
    account = get_account()
    print(f"Deploying on .....{network.show_active()}")
    
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        price_feed_address = config["networks"][network.show_active()]["eth_usd_price_feed"]

    else: #deploy mock of price feed on internal chain: development
        deploy_mocks()
        price_feed_address = MockV3Aggregator[-1].address 

    fund_me = FundMe.deploy(price_feed_address,
    {"from": account}, 
    publish_source=config["networks"][network.show_active()].get("verify"))

    print(f"Contract deployed to: {fund_me.address}")
    return fund_me

def main():
    deploy_fund_me()
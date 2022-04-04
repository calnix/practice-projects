from brownie import network, config, interface
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3

# 0.1 ETH - 0.1*(10**18)
deposit_amount = Web3.toWei(0.1, "ether")


def get_lendingpool():
    # create lending_pool_addressess_provider contract object
    lending_pool_addressess_provider = interface.ILendingPoolAddressesProvider(config["networks"][network.show_active()]["lending_pool_addressess_provider"])
    # get lending pool address
    lending_pool_address = lending_pool_addressess_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def approve_erc20(amount, spender, erc20_address, account):
    print("....Approving ERC20 token...")
    # get ERC20 interface: https://github.com/PatrickAlphaC/aave_brownie_py_freecode/tree/main/interfaces
    # approve(address spender, uint256 value)
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("....Approved....")
    return tx


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited.")
    print(f"You have {total_debt_eth} worth of ETH borrowed.")
    print(f"You can borrow {available_borrow_eth} worth of ETH.")
    return (float(available_borrow_eth), float(total_debt_eth))


def get_token_price(price_feed_address):
    # use chainlink pricefeed
    token_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    price = token_eth_price_feed.latestRoundData()[1]  # price is index 1
    norm_price = Web3.fromWei(price, "ether")
    print(f"...DAI/ETH price is {norm_price}")
    return float(norm_price)


def main():
    account = get_account()
    deposit_token_address = config["networks"][network.show_active()]["weth_token"]
    # if no WETH, get_weth()
    ## local mainnet fork uses dummy accounts - do not come preloaded with WETH
    if network.show_active() in ["mainnet-fork"]:
        get_weth()

    # Get lending pool contract
    lending_pool = get_lendingpool()
    print(f"....Lending pool contract: {lending_pool.address}....")

    ## Approve before sending our ERC20(WETH) tokens: approve allowance of deposit_amount for Aave lendingPool contract
    approve_erc20(deposit_amount, lending_pool.address, deposit_token_address, account)

    # Deposit: deposit(address asset, uint256 amount, address onBehalfOf, uint16 referralCode)
    ## referralCode is deprecated - just pass a 0 as parameter
    print("....Depositing....")
    tx = lending_pool.deposit(deposit_token_address, deposit_amount, account.address, 0, {"from": account})
    tx.wait(1)  # wait one block
    print("....Deposited!....")

    # Borrow DAI
    ## how much can we borrow - pull account stats - getUserAccountData(address user)
    (borrowable_eth, total_debt_eth) = get_borrowable_data(lending_pool, account)
    
    # DAI in terms of ETH - how much DAI can we borrow?
    dai_eth_price = get_token_price(config["networks"][network.show_active()]["dai_eth_price_feed"])
    dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)  # use 90% of collateral: liquidation concerns
    print(f"...We will borrow {dai_to_borrow} DAI...")

    ## Borrow! call borrow() from lendingPool contract
    ## function borrow(address asset, uint256 amount, uint256 interestRateMode, uint16 referralCode, address onBehalfOf)
    # interestRateMode: 1 - stable | 2 - variable
    dai_address = config["networks"][network.show_active()]["dai_token_address"]
    borrow_tx = lending_pool.borrow(dai_address, Web3.toWei(dai_to_borrow, "ether"), 1, 0, account.address, {"from": account})
    borrow_tx.wait(1)
    print("...Borrowed!...")

    # Account Info
    get_borrowable_data(lending_pool, account)

    # Return DAI
    ## repay(address asset, uint256 amount, uint256 rateMode, address onBehalfOf)
    #(dai_in_wei, lending_pool, account)
    repay_all(Web3.toWei(dai_to_borrow, "ether"), lending_pool, account)
    get_borrowable_data(lending_pool, account)
    print("You just deposited, borrowed, and repayed with Aave, Brownie, and Chainlink!")


def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool.address,
        config["networks"][network.show_active()]["dai_token_address"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token_address"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("...REPAID....")

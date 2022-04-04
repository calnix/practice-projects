from brownie import config, network, interface
from scripts.helpful_scripts import get_account


def get_weth():
    """
    how to get Weth?
    deposit eth to WETH contract, it gives us ETH
    https://kovan.etherscan.io/token/0xd0a1e359811322d97991e03f863a0c30c2cf029c#writeContract

    to interact with this contract we need: address + ABI
    ABI: use interface, IWEth.sol,  from https://github.com/PatrickAlphaC/aave_brownie_py_freecode/tree/main/interfaces
    create IWeth.sol in interfaces folder -> copy and paste github code into it.

    """
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])

    # deposit 0.1 ETH, should get back 0.1 WETH
    tx = weth.deposit({"from": account, "value": 0.1 * 10**18})
    tx.wait(1)
    print("...Received 0.1WETH...")
    return tx


def main():
    get_weth()

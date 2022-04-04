from scripts.aave_borrow import (
    get_token_price,
    get_lendingpool,
    approve_erc20,
    get_account,
)
from brownie import config, network


def test_get_token_price():
    # Arrange / Act
    token_price = get_token_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    # Assert
    assert token_price > 0


def test_get_lending_pool():
    # Arrange / Act
    lending_pool = get_lendingpool()
    # Assert
    assert lending_pool is not None


def test_approve_erc20():
    # Arrange
    account = get_account()
    lending_pool = get_lendingpool()
    amount = 1000000000000000000  # 1
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    # Act
    tx = approve_erc20(amount, lending_pool, erc20_address, account)
    # Assert
    assert tx is not True

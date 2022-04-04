1. Swap some ETH for WETH 
2. Deposit some WETH into Avave
3. Borrow some asset with the collateral
    1. Challenge: Sell that borrowed asset (short selling).
4. Repay everything back

> avave testnet v3 is on rinkeby

## get_weth.py -> 1. Swap some ETH for WETH 
When you deposit ETH into AAVE, its a one step process;
- you are interacting with the WETHGateway contract. This contract swaps our ETH for WETH, the ERC20 version.
- interact with the WEthGateway contract directly using interface.


# Testing Approach:
Unit tests: Mainnet-fork (just fork ETH mainnet)
Integration test: Kovan (v2) / Rinkeby (v3)

If you are not working with oracles and don't need to mock off-chain responses, use a mainnet fork to run unit tests. 
(need mocks to simulate the off-chain to on-chain response)

** create mainnet-fork in brownie-config [weth_token:<mainnet address of Weth>]
Mainnet fork was added previously to brownie networks under the development category. 
- Will use ganache-cli to fork mainnet via alchemy.
- no persistency. 
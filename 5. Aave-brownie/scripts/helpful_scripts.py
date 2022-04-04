from brownie import network, accounts, config

LOCAL_BLOCKCHAIN_ENV = ["development", "ganache-local"]
FORKED_LOCAL_ENV = ["mainnet-fork", "mainnet-fork-dev"]


def get_account(index=None, id=None):
    # accounts[0]  -- ganache accounts
    # accounts.add("env")  -- private key from env file ->  accounts.add(config["wallets"]["wallet1"])
    # accounts.load("id") -- load from brownie accounts list
    if index:
        # if index was passed return ganache account
        return accounts[index]
    if id:
        return accounts.load(id)
    if (network.show_active() in LOCAL_BLOCKCHAIN_ENV or network.show_active() in FORKED_LOCAL_ENV):
        return accounts[0]  # use ganache generated account: since we forking into local env
    else:  # look in config.yaml
        return None
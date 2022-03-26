# for blockchain deplyment
# brownie run <scriptname.py>


#brownie has an accounts package
from brownie import accounts, config, SimpleStorage


#put all the deplyment logic in one fucntion:
def deploy_simple_storage():
    #local ganache accounts
    account = accounts[0]

    #import contract into script: from brownie import <name of contract>
    simple_storage = SimpleStorage.deploy({"from": account})

    #interact with smart contract, like remix
    stored_value = simple_storage.retrieve()  #view function, no need transaction - no need account
    print(stored_value)

    #updating state
    txn = simple_storage.store(3, {"from":account})
    txn.wait(1)
    updated_stored_value = simple_storage.retrieve()
    print(updated_stored_value)


def main():
    deploy_simple_storage()








    #use own account for testnet
    #add account to brownie: brownie accounts new <acc_name:freecodecamp-account>
    #account = accounts.load("freecodecamp-account"); print(account)

    #account env
    #account = accounts.add(config["wallets"]["wallet1"]); print(account)
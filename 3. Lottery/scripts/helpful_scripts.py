from brownie import network,accounts,config, Contract, interface
from brownie import MockV3Aggregator, VRFCoordinatorMock, LinkToken


LOCAL_BLOCKCHAIN_ENV = ["development", "ganache-local"]
FORKED_LOCAL_ENV = ["mainnet-fork", "mainnet-fork-dev"]

def get_account(index=None,id=None):
    # accounts[0]  -- ganache accounts
    # accounts.add("env")  -- private key from env file ->  accounts.add(config["wallets"]["wallet1"])
    # accounts.load("id") -- load from brownie accounts list 
    if index:
        # if index was passed return ganache account
        return accounts[index]
    
    if id:
        return accounts.load(id)

    if network.show_active() in LOCAL_BLOCKCHAIN_ENV or network.show_active() in FORKED_LOCAL_ENV:
        return accounts[0]                                  #use ganache generated account.  
      
    else: #look in config.yaml
        return accounts.add(config["wallets"]["wallet1"])  




#our shortname: Contract Name as per import
#contract_to_mock[ethusd_pricefeed] = MockV3Aggregator
#mocks are stored in contracts/test folder
contract_to_mock = {
    "ethusd_pricefeed": MockV3Aggregator,
    "link_token": LinkToken,
    "vrf_coordinator": VRFCoordinatorMock
    }

def get_contract(contract_name):
    """
    function will grab the mainnet/testnet contract addresses from the brownie config if defined.
    Otherwise, it will deploy a mock version of that contract, and return that mock contract address.
        Args:
            contract_name (string)

        Return:
            brownie.network.contract.ProjectContract: Most recently deployed version of this contract
    """
    contract_type = contract_to_mock[contract_name]
        # check which chain we on 
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:        #forks wont need mocks
        if len(contract_type) <= 0:                           #check if got prior deployment
            deploy_mocks()
        contract = contract_type[-1]                         #grab most recent
    else: 
        # get address from config - since we not in LOCAL_BLOCKCHAIN_
        # need abi of deployed contract so we can interact. 
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
        # contract_type.abi pulls abi from build/dependencies folder: AggregatorV3Interface.json
    return contract

DECIMALS = 8          #to resemble eth/usd price feed on mainnet aggregator
STARTING_PRICE = (2000*10**8)

def deploy_mocks(decimals = DECIMALS, start_price= STARTING_PRICE):
    account = get_account()
    print(f"The active network is {network.show_active()}")
    print("Deploying.....")
    MockV3Aggregator.deploy(decimals,start_price,{"from":account})  #contract object 
    link_token = LinkToken.deploy({"from":account})
    VRFCoordinatorMock.deploy(link_token.address,{"from":account})
    #print(f"Mocks Deployed at: {MockV3Aggregator[-1].address}")
    print(".....All Mocks Deployed!.....")

def fund_with_link(contract_address, account=None, link_token=None, amount=100000000000000000): #0.1 LINK
    account = account if account else get_account()     #account = account, if parameter was specified. else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    # send link to lottery contract, from our account
    tx = link_token.transfer(contract_address, amount, {"from": account})
    #link_token_contract = interface.LinkTokenInterface(link_token.address)
    #tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print(".....Contract Funded.....")
    return tx



# ====================================================================================================================
def get_account_old():
    # accounts[0]  -- ganache accounts
    # accounts.add("env")  -- private key from env file ->  accounts.add(config["wallets"]["wallet1"])
    # accounts.load("id") -- load from brownie accounts list 
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV or network.show_active() in FORKED_LOCAL_ENV:
        return accounts[0]                                  #use ganache generated account.
    
    else:#look in config.yaml
        return accounts.add(config["wallets"]["wallet1"])  
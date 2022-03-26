# Premise:

1. Users can enter lottery with ETH (based on min. fixed USD fee)
2. Admin decides when lottery is over  - (onlyOwner)
3. Lottery will select random winner -> Chainlink VRF

From Chainlink VRF, we will obtain an RNG that will be used to select the winner.

modulo to get index of winner:
   random number % players.length
   if 5 players, remainder = some value 0-4.
   which fits into the index range of all players.
   
> regardless of how large an RNG, the result of modulo operation will fall within the range of player index.

For more in-depth five into VRF see gitbooks: https://calnix.gitbook.io/solidity-lr/reference-contracts/vrfconsumerbase

Testing
1. Quick and dirty test to see if our priceFeeds are working fine:
    * use mainnet-fork, since pricefeed contract is deployed there.
    * current eth price = 2925 -> fee = 50/2925 = 0.017094
 
     
### Unit testing:

In unit testing we want to test every aspect of our code - each component tested piecemeal.
Individual require statements, lottery states, enter/end and so forth. With isolated testing we can quickly identify any snags/bugs in a large or complex codebase. 
To that end, this is carried out in the development network as opposed to a testnet for speed and quick repetitions.

Hence,
```
   if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
      pytest.skip()
```
We will be deploying mocks for unit testing. While we have a mock for VRF Coordinator, we need to simulate the response from the chainlink node.
Hence in test_can_pick_winner(),
```python
    # get randomness
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestID"]    #from emitted event, extract requestID
    STATIC_RNG = 888
    get_contract("vrf_coordinator").callBackWithRandomness(request_id, STATIC_RNG, lottery.address, {"from": account})
```
We expect to receive 888 as the RNG. Since, 888/3 = 296, with r=0, winner is players(0).


### Integration testing:
```python
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
```
Here we are testing by deploying onto a live testnet.
```python
brownie test -k test_pick_winner --network rinkeby -s
```
(-s) flag for verbosity 


## Test Deployment:

brownie run scripts/deploy.py --network kovan
Contract was deployed to [0x1767D6C99fBF98ae063dA81c1911aC9a9ed07C39](https://kovan.etherscan.io/address/0x1767D6C99fBF98ae063dA81c1911aC9a9ed07C39#readContract).

> if you are obtaining lastRandom as 0x0000000000000000000000000000000000000000, this is typically caused by a delay in RNG provision. The chainlink node on rinkeby takes at least 20 minutes (at time of writing) to return a random value. To avoid this we deployed on Kovan where it takes a couple of minutes to get the random value. 


# Other testing altervatives:

What if the required mocks for unit testing are not available?
1. Make your own mock
2. Fork mainnet into local blockchain environment


# Other notes:

If you need to return a value from a transaction to a client, you need to either 
1) store the value into your contract state and then call a constant function after the transaction is mined to retrieve the value in your client,
2) log via an event and setup a listener on your client.

> rmb, you cannot get the result of a function in solidity, as you would in python [ result = someFunction()]
> result would simply be the transaction hash.

# practice-projects

## 1. Simple Storage

store a number tagged to a specific person's name, utilising structs.

## 2.FundMe

- Smart contract that lets anyone deposit ETH into the contract
- Only the owner of the contract can withdraw the ETH
- Use Chainlink to pull ETH/USD price data from off-chain
- Deploy Mocks and Forks

## 3. Lottery
- Users can enter lottery with ETH (based on a fixed minimum USD fee)
- Admin decides when lottery is over  -> (onlyOwner)
- Lottery will select random winner -> obtain Randomness from Chainlink VRF

### For initial quick and dirty testing on pricefeeds, use mainet-fork, since pricefeed contract is already presently deployed there.
### At time of writing: ~ current eth price = 2925 -> fee = 50/2925 = 0.017094. 


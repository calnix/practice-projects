1. Users can enter lottery with ETH (based on USD fee)
2. Admin decides when lottery is over  - (onlyOwner)
3. Lottery will select random winner

Testing
1. Quick and dirty test to see if our priceFeeds are working fine:
    * use mainnet-fork, since pricefeed contract is deployed there.
    * current eth price = 2925 -> fee = 50/2925 = 0.017094



;;our implementation;;
1. intead of array, use mapping for players 
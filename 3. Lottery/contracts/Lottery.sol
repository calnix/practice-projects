//SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";


contract Lottery is VRFConsumerBase,Ownable { 
    
    address payable[] internal players;                          //track players
    uint public minfee_usd = 50 * (10**18);                     //make 18 dp

    AggregatorV3Interface public ethusd_pricefeed;             //init interface as state, for getter function

    enum LOTTERY_STATE {OPEN, CLOSED, CALCULATING_WINNER}     // 0-> Open state, 1 -> closed state, ...
    LOTTERY_STATE public lottery_state;                      //init LOTTERY_STATE is a class. 

    uint256 internal fee;
    bytes32 internal keyhash;                              //to identify the chainlink node

    address payable public recentWinner;
    uint public lastRandom;

    event RequestedRandomness(bytes32 requestID);

    constructor(address _pricefeedaddress, 
    address _vrfCoordinator, 
    address _link, 
    uint _fee, 
    bytes32 _keyhash) 
    public VRFConsumerBase(_vrfCoordinator, _link){
        ethusd_pricefeed = AggregatorV3Interface(_pricefeedaddress);
        lottery_state = LOTTERY_STATE.CLOSED;                           // can also, lottery_state = 1
        //VRF fee and hash
        fee = _fee;
        keyhash = _keyhash;
    }

    //users enter lottery
    function enter() public payable {
        require(lottery_state == LOTTERY_STATE.OPEN, "Lottery is not open!");
        //min $50
        require(msg.value >= getEntranceFee(), "Not enough ETH!");
        players.push(msg.sender);

    }
    
    //calc entrance fee in eth
    function getEntranceFee() public view returns(uint) {          
        //get eth/usd
        (,int price,,,) = ethusd_pricefeed.latestRoundData();
        uint eth_usd = uint(price)*(10**10);          //ETH/USD rate received in 8dp, multiply by 10**10 to make 18 dp

        // convert to eth ->  usd/ethPrice
        uint entranceFee = (minfee_usd*(10**18) / eth_usd);  //division will cancel out the dp, so mulitply back to retain precision.
        return entranceFee;
    }


    //admin to start lottery? 0r anyone to start -- public?
    function startLottery() public onlyOwner {
        require(lottery_state == LOTTERY_STATE.CLOSED, "Lottery must be close before it can be opened!");
        lottery_state = LOTTERY_STATE.OPEN;
    }


    //admin to end lottery - public?
    function endLottery() public onlyOwner {
       lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
       bytes32 requestId = requestRandomness(keyhash,fee);  //catch requestID 
       emit RequestedRandomness(requestId);
    }

       //receive randomn value - fulfillRandomness()
    function fulfillRandomness(bytes32 _requestId, uint _randomness) internal override {
        // internal so only VRF coordinator can call it.
        // override: in VRFConsumer, fulfillRandomness() is empty. meant to be overwritten.
        require(lottery_state == LOTTERY_STATE.CALCULATING_WINNER, "Lottery is not in calculation");
        require(_randomness > 0, "RNG not received");
        uint winner_index = _randomness % players.length;
        
        // make payment
        recentWinner = players[winner_index];
        recentWinner.transfer(address(this).balance);

        //reset lottery
        players = new address payable[](0);   //size 0
        lottery_state = LOTTERY_STATE.CLOSED;
        lastRandom = _randomness;

    }


}
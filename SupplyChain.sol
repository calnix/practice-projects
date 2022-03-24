//SPDX-License-Identifier: MIT
pragma solidity ^0.8.1;

contract Item {
    uint public priceInWei;
    uint public paidWei;
    uint public index;

    ItemManager parentContract;     //variable of type ItemManager -> contract object.
    
    // creation requires input of : price & index.
    constructor(ItemManager _parentContract, uint _priceInWei, uint _index) {
        priceInWei = _priceInWei;
        index = _index;
        parentContract = _parentContract;
    }

    receive() external payable {
        require(msg.value == priceInWei, "We don't support partial payments");
        require(paidWei == 0, "Item is already paid!");
        paidWei += msg.value;
        (bool success, ) = address(parentContract).call{value:msg.value}(abi.encodeWithSignature("triggerPayment(uint256)", index));
        require(success, "Delivery did not work");
    }

    fallback () external {

    }
}

contract ItemManager {
   
   enum itemState{
        Created, Paid, Delivered    //created - 0, paid -1,..
    }

    struct S_Item {
        Item _item;         //_item variable is contract object? by above logic
        string id;
        uint price;
        itemState state;
    }
    
    // to create a dataframe-like structure
    mapping(uint => S_Item) public item_list;
    uint item_index;
    
    event SupplyChainStep(uint _index, uint _state);

    function createItem(string memory _id, uint _price) public {
        Item item = new Item(this, _price, item_index);   //create new Item contract. this: the current contract, explicitly convertible to address
        item_list[item_index]._item = item;

        item_list[item_index].id = _id;
        item_list[item_index].price = _price;
        item_list[item_index].state = itemState.Created;

        emit SupplyChainStep(item_index, uint(item_list[item_index].state));
        item_index++;

    }

    function triggerPayment(uint _index) public payable {
        require(item_list[_index].price == msg.value, "please pay exact full amount");
        require(item_list[_index].state == itemState.Created,"Item is not available");
        item_list[_index].state = itemState.Paid;   //update state to paid
        // emit payment event
        emit SupplyChainStep(item_index, uint(item_list[item_index].state));
        
        
    }

    function triggerDeliver(uint _index) public {
        require(item_list[_index].state == itemState.Paid,"Item is not for delivery");
        item_list[_index].state == itemState.Delivered;

        // emit delivery
        emit SupplyChainStep(item_index, uint(item_list[item_index].state));
    }
}


// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleStorage{

    uint public favNum;
    
    struct People {
        uint favNum;
        string name;
    }
    
    /*
    declare person has People type. (like address, uint)
    assign people values of 2 & Patrick  --> People({})
    this is the same as --> uint public favNum = 5;
        People public person = People({favNum: 2, name: "Patrick"});
    */

    People[] public people;  
    mapping(string => uint) public name2num;

    function store(uint _num) public {
        favNum = _num;
    }
    
    function retrieve() public view returns(uint){
        return favNum;
    }

    function addPerson(uint _favnum, string memory _name) public {
        people.push(People({favNum: _favnum,name: _name}));
        name2num[_name] = _favnum;
    }

     
}
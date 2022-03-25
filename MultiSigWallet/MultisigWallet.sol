pragma solidity 0.5.0;
 
contract MultiSigWallet {
 
    /*
     * Data types and variables
     */ 
 
    uint constant public MAX_OWNER_COUNT = 10;
 
    event Confirmation(address indexed sender, uint indexed transactionId);
    event Submission(uint indexed transactionId);
    event Execution(uint indexed transactionId);
    event ExecutionFailure(uint indexed transactionId);
    event Deposit(address indexed sender, uint value);
    event NotEnoughBalance(uint curBalance, uint requestedBalance);
 
    // Mapping of Txn IDs to Transaction objects
    mapping (uint => Transaction) public transactions;
 
    // Mapping of Txn IDs to owners who already signed them
    mapping (uint => mapping (address => bool)) public signatures;
 
    mapping (address => bool) public isOwner;
 
    // all possible signers of each transaction
    address[] public owners;
 
    // minimum number of signatures required for execution of each transaction
    uint public minSignatures; 
    uint public transactionCount; 
 
    struct Transaction {
        // receiver of crypto-tokens (Ether) sent
        address destination; 
        // amount to sent from contract
        uint value;
        // bool to record if transaction has been executed
        bool executed;
    }
 
    /*
     * Modifiers serve as macros in C - they are substitued to the place of
     * usage, while placeholder "_" represents the body of the function that
     * "calls" them.
     *
     * kind of works like python @decorator
     * "passes" or "reverts"/fails depending on bool
     */
 
    // TASK: replace the body of this modifier to fit n-of-m multisig
 
    modifier checkValidSettings(uint ownerCount, uint _requiredSigs) {
        if(
            ownerCount > MAX_OWNER_COUNT
            || _requiredSigs == 0
            || _requiredSigs > ownerCount
            || ownerCount == 0
          ){
            revert("Validation of n-of-m multisig setting failed");
          }
        _;
    }
 
    modifier ownerExists(address owner) {
        if (!isOwner[owner])
            revert("Owner does not exist.");
        _;
    }
 
    modifier txnExists(uint transactionId) {
        if (transactions[transactionId].destination == address(0))
            revert("Transaction does not exist.");
        _;
    }
 
    modifier confirmed(uint transactionId, address owner) {
        if (!signatures[transactionId][owner])
            revert("Confirmation of transaction by an owner does not exist.");
        _;
    }
 
    modifier notConfirmed(uint transactionId, address owner) {
        if (signatures[transactionId][owner])
            revert("Transaction was already confirmed.");
        _;
    }    
 
    // TASK 1: write here a modifier what will protect against replay attacks,
    //         and call it at the correct place
 
    modifier txnNotExecuted(uint transactionId) {
        if (transactions[transactionId].executed)
            revert("Transaction already executed.");
        _;
    }
 
    /**
     * Public functions - functions can be called by anybody, so access control
     * must be implemented within their bodies
     */
 
    // @dev Fallback function -- allows to deposit Ether by anybody just by
    // using value to the address of the contract
    // 'msg.value' holds the amount of Ether sent in the current transaction
    // and 'msg.sender' is the address of the sender of a transaction
 
    function() external payable {
        if (msg.value > 0){
            // emiting of the event is stored at the blockchain as well.
            // So, UI knows that Ether was deposited.
            emit Deposit(msg.sender, msg.value);
        }
    }
 
    // @dev Constructor of n-of-m multisig wallet. It sets initial owners
    // (i.e., signers) and minimal required number of signatures.
    // @param _owners List of owners.
    // @param _requiredSigs - the minimal number of required signatures.
 
    constructor(address[] memory _owners, uint _requiredSigs) public
        checkValidSettings(_owners.length, _requiredSigs)
    {        
        // TASK 2: Modify this constructor to fit n-of-m scheme, i.e., an
 
 
        for(uint i = 0; i < _owners.length; i++){
            checkNotNull(_owners[i]);
            for (uint j = i+1; j < _owners.length; j++){
                if(_owners[i] == _owners[j]){
                    revert("A repeated owner passed.");
                }
            }
        }
 
        // save owners (m) and the minimum number of signatures (n)
        for(uint i=0; i<_owners.length; i++){
            isOwner[_owners[i]] = true;
        }
        owners = _owners;
        minSignatures = _requiredSigs;
    }
 
 
    /// @dev Allows an owner to submit and confirm a transaction.
    /// @param destination Transaction target address.
    /// @param value Transaction ether value.
    /// @return Returns transaction ID.
 
    function submitTransaction(address destination, uint value) 
        public returns (uint transactionId)
    {
        transactionId = addTransaction(destination, value);
        confirmTransaction(transactionId);
        return transactionId;
    }
 
    /// @dev Allows an owner to confirm a transaction.
    /// @param transactionId Transaction ID.
    function confirmTransaction(uint transactionId) public
        ownerExists(msg.sender)
        txnExists(transactionId)
        notConfirmed(transactionId, msg.sender)
    {
        signatures[transactionId][msg.sender] = true;
        emit Confirmation(msg.sender, transactionId);
        executeTransaction(transactionId);
    }
 
    /// @dev Allows anyone to execute a confirmed transaction.
    /// @param transactionId Transaction ID.
    function executeTransaction(uint transactionId) 
        public
        // check for replay
        txnNotExecuted(transactionId)
    {
        // TASK 3: check whether the contract has enough balance and if not
        //         emit a new event called
        //         NotEnoughBalance(curBalance, requestedBalance)
        if (isTxConfirmed(transactionId)) {
            Transaction storage txn = transactions[transactionId];          
 
            uint curBalance = address(this).balance;
            uint requestedBalance = txn.value;
 
            if (requestedBalance > curBalance) {
                emit NotEnoughBalance(curBalance, requestedBalance);              
            }
 
            // Implicit conversions from address payable to address are
            // allowed, whereas conversions from address to address payable
            // are not possible (the only way to perform such a conversion is
            // by using an intermediate conversion to uint160).
            if (address(uint160(txn.destination)).send(txn.value)){
                txn.executed = true;
                // sending the Ether to destination address
                emit Execution(transactionId);              
            }
            else {
                emit ExecutionFailure(transactionId);                
            }
        }
    }
 
    // @dev Returns the confirmation status of a transaction.
    // @param transactionId -- Transaction ID.
    // @return Confirmation status: true means that TX can be executed;
    //      false - TX cannot be exectued as there are not enough signatures
 
    function isTxConfirmed(uint transactionId) public view returns (bool)
    {
        uint count = 0;
        for (uint i = 0 ; i < owners.length ; i++) {
            if (signatures[transactionId][owners[i]]){
                count += 1;
            }
            if (count >= minSignatures){
                return true;   
            }                
        }
        return false;
    }
 
    /*
     * Internal functions - called only from inside of the smart contract
     */
 
    function checkNotNull(address _address) internal pure {
        if (_address == address(0x0)){
            revert("Null address.");        
        }            
    }
 
    // @dev Adds a new transaction to the transaction mapping,
    //      if transaction does not exist yet.
    // @param destination Transaction target address.
    // @param value Transaction ether value.
    // @return Returns transaction ID.
 
    function addTransaction(address destination, uint value) internal
        returns (uint transactionId)
    {
        checkNotNull(destination);
        transactionId = transactionCount;
        transactions[transactionId] = Transaction({
            destination: destination,
            value: value,
            executed: false
        });
        transactionCount += 1;
        emit Submission(transactionId);
        return transactionId;
    }
 
    /*
     *  Public functions for DAPP client (i.e., simulated by tests)
     */
 
    /// @dev Returns number of signatures of a transaction.
    /// @param transactionId Transaction ID.
    /// @return Number of signatures.
 
    function getSignatureCount(uint transactionId) public view
        returns (uint count)
    {
        for (uint i = 0; i < owners.length; i++)
            if (signatures[transactionId][owners[i]]){
                count += 1;
            }       
        return count;         
    }
 
    /// @dev Returns total number of transactions
 
    function getTransactionCount() public view returns (uint)
    {
        return transactionCount;
    }
 
    /// @dev Returns list of all owners.
    /// @return List of owner addresses.
 
    function getOwners()
        public view returns (address[] memory)
    {
        return owners;
    }
 
    // TASK 4: write a public read-only (not modifying the state) function
    //         that retrieves addresses of owners who signed a passed
    //         transaction
 
    /// @dev Returns array with owners that confirmed a transaction.
    /// @param transactionId Transaction ID.
    /// @return Returns array of owner addresses.
 
    function getOwnersWhoSignedTx(uint transactionId)
        public view returns (address[] memory)
    {
        address[] memory signedOwners = new address[](
            getSignatureCount(transactionId)
            );
        uint cursor = 0;
        for (uint i = 0; i < owners.length; i++) {
            if (signatures[transactionId][owners[i]]){
                signedOwners[cursor] = owners[i];
                cursor += 1;
            }
        }
        return signedOwners;
    }
}
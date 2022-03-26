# Simple-Shared-Wallet

Simple wallet implementation wherein someone could use it to manage payouts of allowances.
For example, a parent disembursing monthly allowance to their children.

# Objectives:

1. Have an on-chain wallet smart contract.
2. Wallet contract can store funds and let users withdraw again.
3. You can also give "allowance" to other, specific user-addresses.
4. Restrict the functions to specific user-roles (owner, user)
5. Re-Use existing smart contracts which are already audited - Ownable.sol

#file name must start with test_

from brownie import SimpleStorage, accounts


def test_deploy():
    # Arrange - setup
    account = accounts[0]
    
    # Act
    simple_storage = SimpleStorage.deploy({"from": account})
    starting_value = simple_storage.retrieve()
    expected_value = 0
    
    # Assert
    assert expected_value == starting_value


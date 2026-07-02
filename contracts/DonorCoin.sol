// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract DonorCoin is ERC20 {
    address public admin;
    uint256 public totalMinted; 

    modifier onlyOwner() {
        require(msg.sender == admin, "Not authorized: Only Admin can mint");
        _;
    }

    constructor() ERC20("Donor Coin", "DNR") {
        admin = msg.sender;
    }

    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
        totalMinted += amount;
    }

    function transferOwnership(address newAdmin) public onlyOwner {
        require(newAdmin != address(0), "Invalid address");
        admin = newAdmin;
    }
}


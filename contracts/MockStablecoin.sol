// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
 * @title MockStablecoin
 * @dev Mock ERC-20 stablecoin for testing and development
 * In production, this would be replaced with USDC, USDT, or DAI
 */
contract MockStablecoin is ERC20 {
    constructor() ERC20("Mock USD Stablecoin", "MUSD") {
        // Mint initial supply for testing
        _mint(msg.sender, 1000000 * 10**decimals());
    }
    
    /**
     * @dev Mint tokens (for testing purposes)
     */
    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
    
    /**
     * @dev Faucet function for easy testing
     */
    function faucet() external {
        _mint(msg.sender, 1000 * 10**decimals());
    }
}



// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./BondToken.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title BondPlatform
 * @dev Factory contract for creating and managing multiple bond tokens
 */
contract BondPlatform is Ownable {
    // Array of all bond token addresses
    address[] public bonds;
    
    // Mapping from bond ID to bond token address
    mapping(uint256 => address) public bondTokens;
    
    // Mapping from bond token address to bond ID
    mapping(address => uint256) public bondIds;
    
    // Stablecoin address (shared across all bonds)
    address public stablecoinAddress;
    
    // Events
    event BondCreated(
        uint256 indexed bondId,
        address indexed bondToken,
        string bondName,
        string issuer
    );
    
    constructor(address _stablecoinAddress) {
        stablecoinAddress = _stablecoinAddress;
    }
    
    /**
     * @dev Create a new bond token
     * @param _bondName Name of the bond
     * @param _issuer Government entity issuing the bond
     * @param _faceValue Total face value of the bond
     * @param _couponRate Annual interest rate in basis points (e.g., 500 = 5%)
     * @param _maturityDate Unix timestamp of maturity
     * @return bondId The ID of the newly created bond
     * @return bondTokenAddress The address of the bond token contract
     */
    function createBond(
        string memory _bondName,
        string memory _issuer,
        uint256 _faceValue,
        uint256 _couponRate,
        uint256 _maturityDate
    ) external onlyOwner returns (uint256 bondId, address bondTokenAddress) {
        // Create new bond token
        BondToken newBond = new BondToken(
            _bondName,
            _issuer,
            _faceValue,
            _couponRate,
            _maturityDate,
            stablecoinAddress
        );
        
        bondTokenAddress = address(newBond);
        bondId = bonds.length;
        
        // Store bond information
        bonds.push(bondTokenAddress);
        bondTokens[bondId] = bondTokenAddress;
        bondIds[bondTokenAddress] = bondId;
        
        emit BondCreated(bondId, bondTokenAddress, _bondName, _issuer);
        
        return (bondId, bondTokenAddress);
    }
    
    /**
     * @dev Get total number of bonds
     */
    function getBondCount() external view returns (uint256) {
        return bonds.length;
    }
    
    /**
     * @dev Get all bond addresses
     */
    function getAllBonds() external view returns (address[] memory) {
        return bonds;
    }
    
    /**
     * @dev Get bond token address by ID
     */
    function getBondToken(uint256 bondId) external view returns (address) {
        require(bondId < bonds.length, "Bond ID does not exist");
        return bondTokens[bondId];
    }
}



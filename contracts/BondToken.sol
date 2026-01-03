// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title BondToken
 * @dev ERC-20 compatible token representing fractional ownership of government bonds
 * Each token represents proportional ownership of an underlying government bond
 */
contract BondToken is ERC20, Ownable, ReentrancyGuard {
    // Bond metadata
    struct BondInfo {
        string bondName;
        string issuer;           // Government entity
        uint256 faceValue;        // Total face value of the bond
        uint256 couponRate;       // Annual interest rate (in basis points, e.g., 500 = 5%)
        uint256 maturityDate;     // Unix timestamp of maturity
        uint256 issueDate;        // Unix timestamp of issue
        uint256 lastInterestPayment; // Last time interest was paid
        uint256 totalSupply;      // Total tokens minted
        bool isActive;            // Whether bond is still accepting investments
    }

    BondInfo public bondInfo;
    
    // Stablecoin address for payments
    IERC20 public stablecoin;
    
    // Mapping to track user investments
    mapping(address => uint256) public investments;
    
    // Mapping to track claimed interest per user
    mapping(address => uint256) public claimedInterest;
    
    // Events
    event InterestPaid(address indexed investor, uint256 amount);
    event PrincipalRedeemed(address indexed investor, uint256 amount);
    event InvestmentMade(address indexed investor, uint256 stablecoinAmount, uint256 tokensMinted);
    
    constructor(
        string memory _bondName,
        string memory _issuer,
        uint256 _faceValue,
        uint256 _couponRate,
        uint256 _maturityDate,
        address _stablecoinAddress
    ) ERC20(_bondName, string(abi.encodePacked("BOND-", _bondName))) {
        bondInfo = BondInfo({
            bondName: _bondName,
            issuer: _issuer,
            faceValue: _faceValue,
            couponRate: _couponRate,
            maturityDate: _maturityDate,
            issueDate: block.timestamp,
            lastInterestPayment: block.timestamp,
            totalSupply: 0,
            isActive: true
        });
        
        stablecoin = IERC20(_stablecoinAddress);
    }
    
    /**
     * @dev Invest in the bond by purchasing tokens with stablecoins
     * @param stablecoinAmount Amount of stablecoins to invest
     */
    function invest(uint256 stablecoinAmount) external nonReentrant {
        require(bondInfo.isActive, "Bond is no longer accepting investments");
        require(block.timestamp < bondInfo.maturityDate, "Bond has matured");
        require(stablecoinAmount > 0, "Investment amount must be greater than 0");
        
        // Transfer stablecoins from investor to contract
        require(
            stablecoin.transferFrom(msg.sender, address(this), stablecoinAmount),
            "Stablecoin transfer failed"
        );
        
        // Calculate tokens to mint (1:1 ratio with stablecoin, can be adjusted)
        uint256 tokensToMint = stablecoinAmount;
        
        // Mint tokens to investor
        _mint(msg.sender, tokensToMint);
        
        // Update investment tracking
        investments[msg.sender] += stablecoinAmount;
        bondInfo.totalSupply += tokensToMint;
        
        emit InvestmentMade(msg.sender, stablecoinAmount, tokensToMint);
    }
    
    /**
     * @dev Calculate accrued interest for an investor
     * @param investor Address of the investor
     * @return Accrued interest amount in stablecoins
     */
    function calculateAccruedInterest(address investor) public view returns (uint256) {
        uint256 balance = balanceOf(investor);
        if (balance == 0) return 0;
        
        // Calculate time elapsed since last payment (in seconds)
        uint256 timeElapsed = block.timestamp - bondInfo.lastInterestPayment;
        
        // Calculate annual interest: balance * couponRate / 10000
        // Then prorate for time elapsed: annualInterest * timeElapsed / 365 days
        uint256 annualInterest = (balance * bondInfo.couponRate) / 10000;
        uint256 accruedInterest = (annualInterest * timeElapsed) / 365 days;
        
        return accruedInterest;
    }
    
    /**
     * @dev Claim accrued interest payments
     */
    function claimInterest() external nonReentrant {
        require(balanceOf(msg.sender) > 0, "No bond tokens held");
        
        uint256 interestAmount = calculateAccruedInterest(msg.sender);
        require(interestAmount > 0, "No interest to claim");
        
        // Update last interest payment time
        bondInfo.lastInterestPayment = block.timestamp;
        
        // Track claimed interest
        claimedInterest[msg.sender] += interestAmount;
        
        // Transfer interest in stablecoins
        require(
            stablecoin.transfer(msg.sender, interestAmount),
            "Interest transfer failed"
        );
        
        emit InterestPaid(msg.sender, interestAmount);
    }
    
    /**
     * @dev Redeem principal at maturity
     * Investors can redeem their tokens for the face value proportion
     */
    function redeem() external nonReentrant {
        require(block.timestamp >= bondInfo.maturityDate, "Bond has not matured yet");
        require(balanceOf(msg.sender) > 0, "No tokens to redeem");
        
        uint256 tokenBalance = balanceOf(msg.sender);
        uint256 redemptionAmount = tokenBalance; // 1:1 redemption with stablecoins
        
        // Burn tokens
        _burn(msg.sender, tokenBalance);
        
        // Transfer principal in stablecoins
        require(
            stablecoin.transfer(msg.sender, redemptionAmount),
            "Redemption transfer failed"
        );
        
        emit PrincipalRedeemed(msg.sender, redemptionAmount);
    }
    
    /**
     * @dev Get bond information
     */
    function getBondInfo() external view returns (
        string memory bondName,
        string memory issuer,
        uint256 faceValue,
        uint256 couponRate,
        uint256 maturityDate,
        uint256 issueDate,
        uint256 totalSupply,
        bool isActive
    ) {
        return (
            bondInfo.bondName,
            bondInfo.issuer,
            bondInfo.faceValue,
            bondInfo.couponRate,
            bondInfo.maturityDate,
            bondInfo.issueDate,
            bondInfo.totalSupply,
            bondInfo.isActive
        );
    }
    
    /**
     * @dev Close bond to new investments (owner only)
     */
    function closeBond() external onlyOwner {
        bondInfo.isActive = false;
    }
}


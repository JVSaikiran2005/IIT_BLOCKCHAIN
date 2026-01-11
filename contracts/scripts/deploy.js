/**
 * Deployment script for Bond Platform contracts
 * Run with: npx hardhat run scripts/deploy.js --network localhost
 */

const hre = require("hardhat");

async function main() {
    console.log("Deploying Bond Platform contracts...");

    // Get signers
    const [deployer] = await hre.ethers.getSigners();
    console.log("Deploying contracts with account:", deployer.address);
    console.log("Account balance:", (await deployer.provider.getBalance(deployer.address)).toString());

    // Deploy Mock Stablecoin
    console.log("\n1. Deploying Mock Stablecoin...");
    const MockStablecoin = await hre.ethers.getContractFactory("MockStablecoin");
    const stablecoin = await MockStablecoin.deploy();
    await stablecoin.waitForDeployment();
    const stablecoinAddress = await stablecoin.getAddress();
    console.log("Mock Stablecoin deployed to:", stablecoinAddress);

    // Deploy Bond Platform
    console.log("\n2. Deploying Bond Platform...");
    const BondPlatform = await hre.ethers.getContractFactory("BondPlatform");
    const platform = await BondPlatform.deploy(stablecoinAddress);
    await platform.waitForDeployment();
    const platformAddress = await platform.getAddress();
    console.log("Bond Platform deployed to:", platformAddress);

    // Create sample bonds
    console.log("\n3. Creating sample bonds...");
    
    const oneYear = 365 * 24 * 60 * 60;
    const tenYears = 10 * oneYear;
    const fiveYears = 5 * oneYear;
    const threeYears = 3 * oneYear;
    
    const now = Math.floor(Date.now() / 1000);
    
    // US Treasury 10-Year Bond (4.5% coupon)
    const tx1 = await platform.createBond(
        "US Treasury 10-Year Bond",
        "United States Treasury",
        hre.ethers.parseEther("1000000"), // $1M face value
        450, // 4.5% = 450 basis points
        now + tenYears
    );
    await tx1.wait();
    console.log("Created US Treasury 10-Year Bond");

    // UK Gilt 5-Year Bond (4.0% coupon)
    const tx2 = await platform.createBond(
        "UK Gilt 5-Year Bond",
        "UK Debt Management Office",
        hre.ethers.parseEther("500000"), // £500K face value
        400, // 4.0% = 400 basis points
        now + fiveYears
    );
    await tx2.wait();
    console.log("Created UK Gilt 5-Year Bond");

    // German Bund 3-Year Bond (3.5% coupon)
    const tx3 = await platform.createBond(
        "German Bund 3-Year Bond",
        "German Finance Agency",
        hre.ethers.parseEther("750000"), // €750K face value
        350, // 3.5% = 350 basis points
        now + threeYears
    );
    await tx3.wait();
    console.log("Created German Bund 3-Year Bond");

    console.log("\n✅ Deployment complete!");
    console.log("\nContract Addresses:");
    console.log("Stablecoin:", stablecoinAddress);
    console.log("Platform:", platformAddress);
    console.log("\nSave these addresses to your .env file:");
    console.log(`STABLECOIN_CONTRACT_ADDRESS=${stablecoinAddress}`);
    console.log(`BOND_PLATFORM_CONTRACT_ADDRESS=${platformAddress}`);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });



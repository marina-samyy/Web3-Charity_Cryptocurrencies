// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @dev 
 */
interface IDonorCoin {
    function mint(address to, uint256 amount) external;
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function transferOwnership(address newAdmin) external;
}

contract CharityCore {
    address public admin;
    bool public paused;
    IDonorCoin public donorCoin;

    struct Campaign {
        string name;
        uint256 goal;
        uint256 raised;
        bool active;
    }

    Campaign[] public campaigns;
    mapping(address => string) public userNames;
    mapping(address => bool) public hasRegistered;


    event CampaignAdded(uint256 indexed id, string name, uint256 goal);
    event CampaignUpdated(uint256 indexed id, string name, uint256 goal);
    event DonationReceived(address indexed donor, uint256 indexed campaignId, uint256 amount);
    event UserRegistered(address indexed user, string name);
    event SystemPaused();
    event SystemResumed();
    event AdminChanged(address indexed oldAdmin, address indexed newAdmin);


    modifier onlyOwner() {
        require(msg.sender == admin, "Access Control: Admin only");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "System is currently paused (Emergency Stop)");
        _;
    }

    constructor(address _donorCoinAddress) {
        admin = msg.sender;
        paused = false;
        donorCoin = IDonorCoin(_donorCoinAddress);
    }


    function getAdmin() public view returns (address) {
        return admin;
    }

    function addCampaign(string memory _name, uint256 _goal) public onlyOwner {
        require(bytes(_name).length > 0, "Name cannot be empty");
        campaigns.push(Campaign(_name, _goal, 0, true));
        emit CampaignAdded(campaigns.length - 1, _name, _goal);
    }

    function batchAdminOperations(string[] memory names, uint256[] memory goals) external onlyOwner {
        require(names.length == goals.length, "Arrays length mismatch");
        for (uint256 i = 0; i < names.length; i++) {
            require(bytes(names[i]).length > 0, "Invalid name in batch");
            require(goals[i] > 0, "Goal must be greater than 0");
            
            addCampaign(names[i], goals[i]);
        }
    }

    function mintDonorCoin(address _to, uint256 _amount) external onlyOwner {
        donorCoin.mint(_to, _amount);
    }

    function pause() external onlyOwner {
        paused = true;
        emit SystemPaused();
    }

    function resume() external onlyOwner {
        paused = false;
        emit SystemResumed();
    }

    function transferOwnership(address newAdmin) external onlyOwner {
        require(newAdmin != address(0), "Invalid address");
        address oldAdmin = admin;
        admin = newAdmin;
        
        try donorCoin.transferOwnership(newAdmin) {} catch {}
        
        emit AdminChanged(oldAdmin, newAdmin);
    }



    function registerUser(string memory _name) external {
        require(bytes(_name).length > 0, "Name cannot be empty");
        userNames[msg.sender] = _name;
        hasRegistered[msg.sender] = true;
        emit UserRegistered(msg.sender, _name);
    }

    function donate(uint256 _campaignId, uint256 _amount) external whenNotPaused {
        require(_campaignId < campaigns.length, "Campaign doesn't exist");
        require(campaigns[_campaignId].active, "Campaign is inactive");
        
        Campaign storage campaign = campaigns[_campaignId];


        require(campaign.raised + _amount <= campaign.goal, "Amount exceeds remaining goal!");

        bool success = donorCoin.transferFrom(msg.sender, address(this), _amount);
        require(success, "Token transfer failed");

        campaign.raised += _amount;

        if (campaign.raised == campaign.goal) {
            campaign.active = false;
        }
        
        emit DonationReceived(msg.sender, _campaignId, _amount);
    }


    function getCampaignsCount() public view returns (uint256) {
        return campaigns.length;
    }

    function getCampaignDetails(uint256 _id) public view returns (string memory, uint256, uint256, bool) {
        Campaign memory c = campaigns[_id];
        return (c.name, c.goal, c.raised, c.active);
    }
}

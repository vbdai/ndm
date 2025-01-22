// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "erc721a/contracts/ERC721A.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract AssetAgreement is ERC721A, AccessControl {
    /**
     * There are two roles,
     * MARKET_ROLE: granted to the Market Contract
     * OWNER_ROLE: granted to the Agreement Owner
     */
    bytes32 public constant MARKET_ROLE = keccak256("MARKET_ROLE");
    bytes32 public constant OWNER_ROLE = keccak256("OWNER_ROLE");

    /**
     * Owner Royalty Fee Percentage. Value between 0 and 1 ether
     */
    uint256 public ownerRoyalty = 0;

    /**
     * Wallet address of original data owner for this Agreement
     */
    address public owner;

    /**
     * Market Contract address
     */
    address public market;

    /**
     * Stores information regarding each individual minted asset
     */
    struct DataAsset {
        uint256 price; // sale price of asset
        bytes32 assetHash; // hash of asset
        bool forSale; // asset for sale flag
        bool resaleAllowed; // whether this asset is allowed for resale
    }


    /*
     * Maps an asset Token ID to a DataAsset structure
     */
    mapping(uint256 => DataAsset) mintedAssets;

    /*
     * Maps Asset Hash to Token ID
     */
    mapping(bytes32 => uint256) hashRecord;

    constructor(
        string memory _name,
        string memory _symbol,
        address _owner,
        address _market
    ) ERC721A(_name, _symbol) {
        owner = _owner;
        market = _market;

        //grant roles to agreement owner and market contract
        _grantRole(OWNER_ROLE, owner);
        _grantRole(MARKET_ROLE, market);
    }

    function supportsInterface(
        bytes4 interfaceId
    ) public view override(ERC721A, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }

    function getNextTokenId() public view returns (uint256) {
        return _nextTokenId();
    }

    function fetchAssetMetaData(
        uint256 _tokenId
    ) public view returns (uint256, bytes32, bool, bool) {
        require(_exists(_tokenId), "Token ID does not exist.");

        uint256 price = mintedAssets[_tokenId].price;
        bytes32 assetHash = mintedAssets[_tokenId].assetHash;
        bool forSale = mintedAssets[_tokenId].forSale;
        bool resaleAllowed = mintedAssets[_tokenId].resaleAllowed;

        return (price, assetHash, forSale, resaleAllowed);
    }

    /**
     * Returns the original data owner's wallet address
     */
    function getOwner() public view returns (address) {
        return owner;
    }

    /**
     * Returns the current original data owner's Royalty Fee Percentage.
     * This value is between 0 and 1.
     */
    function getOwnerRoyalty() public view returns (uint256) {
        return ownerRoyalty;
    }

    /**
     * Updates the original data owner's Royalty Fee Percentage.
     *
     * Can only be called by the Owner.
     *
     * @param _royalty Must be between 0 and 1 ether.
     */
    function updateOwnerRoyalty(uint256 _royalty) public onlyRole(OWNER_ROLE) {
        require(
            _royalty >= 0 && _royalty <= 1 ether,
            "Royalty must be between 0 and 1 ether"
        );
        ownerRoyalty = _royalty;
    }

    /**
     * Returns the Market Address that this Agreement is attached to
     */
    function getMarketAddress() public view returns (address) {
        return market;
    }

    /**
     * Finds the current owner of an asset from the Watermarked Image hash
     *
     * @param _hash 256 bit hash of watermarked asset
     */
    function getOwnerOfAssetFromHash(
        bytes32 _hash
    ) public view returns (address, uint256) {
        uint256 tokenID = hashRecord[_hash];

        require(_exists(tokenID), "Asset Token ID does not exist");

        require(mintedAssets[tokenID].assetHash == _hash, "Asset Hash does not exist");

        return (ownerOf(tokenID), tokenID);
    }

    /**
     * Returns the sale price of an asset
     *
     * @param _tokenId the Token ID of the asset
     */
    function priceOf(uint256 _tokenId) public view returns (uint256) {
        require(_exists(_tokenId), "Asset Token ID does not exist.");

        return mintedAssets[_tokenId].price;
    }

    /**
     * Updates the price of an asset
     *
     * @param _tokenId the Token ID of the asset
     * @param _price the price of the asset
     */
    function updatePrice(
        uint256 _tokenId,
        uint256 _price
    ) public onlyRole(MARKET_ROLE) {
        require(_exists(_tokenId), "Token ID does not exist");

        mintedAssets[_tokenId].price = _price;
    }

    /**
     * Update the hash of the asset. Used by market when a buyer purchases the
     * asset.
     *
     * Can only be called the Market.
     *
     * @param _tokenId Token ID of asset to update
     * @param _hash Hash of Watermarked Asset
     */
    function updateHash(
        uint256 _tokenId,
        bytes32 _hash
    ) public onlyRole(MARKET_ROLE) {
        require(_exists(_tokenId), "Token ID does not exist");

        hashRecord[_hash] = _tokenId;
        mintedAssets[_tokenId].assetHash = _hash; 
    }

    /**
     * Updates the Market Contract address.
     *
     * This ensures that the previous address no longer has permission to access
     * this contract and the new Market Contract address takes it's place.
     *
     * Can only be called by the Owner.
     *
     * @param _market new Market Contract address
     */
    function updateMarketAddress(address _market) public onlyRole(OWNER_ROLE) {
        // remove the old market address from the MARKET_ROLE and revoke
        // approvals
        _revokeRole(MARKET_ROLE, market);
        setApprovalForAll(market, false);

        // update the market address
        market = _market;

        // grant the new market address the MARKET_ROLE and approvals
        _grantRole(MARKET_ROLE, market);
        setApprovalForAll(market, true);
    }

    /**
     * Checks whether the specified asset is for sale
     *
     * @param _tokenId the Token ID of the asset
     */
    function isForSale(uint256 _tokenId) public view returns (bool) {
        require(_exists(_tokenId), "Token ID does not exist");

        return mintedAssets[_tokenId].forSale;
    }

    /**
     * Checks whether the specified asset can be resold after purchase
     *
     * @param _tokenId the Token ID of the asset
     */
    function isResaleAllowed(uint256 _tokenId) public view returns (bool) {
        require(_exists(_tokenId), "Token ID does not exist");

        return mintedAssets[_tokenId].resaleAllowed;
    }

    /**
     * Updates the sale status of an asset
     *
     * Can only be called by the Market.
     *
     * @param _tokenId the Token ID of the asset
     * @param _status the new sale status
     */
    function updateSaleStatus(
        uint256 _tokenId,
        bool _status
    ) public onlyRole(MARKET_ROLE) {
        require(_exists(_tokenId), "Token ID does not exist");

        if (_status) {
            require(
                isResaleAllowed(_tokenId),
                "Cannot change sale status of this asset."
            );
        }

        mintedAssets[_tokenId].forSale = _status;
    }

    /**
     * Updates the resale allowed flag for an asset
     *
     * Can only be called by the Owner
     *
     * @param _tokenId the Token ID of the asset
     * @param _status the new resale allowed status
     */
    function updateAllowResaleStatus(
        uint256 _tokenId,
        bool _status
    ) public onlyRole(OWNER_ROLE) {
        require(_exists(_tokenId), "Token ID does not exist");

        // original data owner must own this asset, you cannot change the resale
        // permission of an asset after it has been sold
        require(
            ownerOf(_tokenId) == msg.sender,
            "You must own this asset to change it's resale status"
        );

        mintedAssets[_tokenId].resaleAllowed = _status;
    }

    /**
     * Mints an asset with a new Token ID
     *
     * Can only be called by the Owner.
     *
     * @param _prices the sale prices of the assets O(N)
     */
    function mint(
        uint256[] memory _prices,
        bool[] memory _resaleAllowed
    ) public onlyRole(OWNER_ROLE) {
        require(
            _prices.length == _resaleAllowed.length,
            "Prices and Resale Permission array must be same length!"
        );

        uint256 startTokenID = _nextTokenId();

        _mint(msg.sender, _prices.length);

        uint256 endTokenID = _nextTokenId();

        for (uint256 i = startTokenID; i < endTokenID; i++) {
            mintedAssets[i].price = _prices[i - startTokenID];
            mintedAssets[i].forSale = true;
            mintedAssets[i].resaleAllowed = _resaleAllowed[i - startTokenID];
        }
    }

    /**
     * Returns the Asset Token URI
     *
     * @param _tokenId the Token ID of the asset
     */
    function tokenURI(
        uint256 _tokenId
    ) public view override returns (string memory) {
        require(_exists(_tokenId), "Asset Token ID does not exist.");
        return "https://www.example.com?id={id}";
    }
}

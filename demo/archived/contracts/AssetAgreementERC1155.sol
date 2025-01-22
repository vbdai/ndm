// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract AssetAgreement is ERC1155, AccessControl {
    bytes32 public constant MARKET_ROLE = keccak256("MARKET_ROLE");
    bytes32 public constant OWNER_ROLE = keccak256("OWNER_ROLE");

    uint256 public tokenId = 1;
    address owner;
    address market;

    struct DataAsset {
        uint256 price;
        bytes32 assetHash;
        bool forSale;
    }

    mapping(uint256 => DataAsset) mintedAssets;
    mapping(bytes32 => uint256) hashRecord;

    constructor(
        address _owner,
        address _market
    ) ERC1155("https://www.example.com?id={id}") {
        owner = _owner;
        market = _market;

        _grantRole(OWNER_ROLE, owner);
        _grantRole(MARKET_ROLE, market);
    }

    function supportsInterface(
        bytes4 interfaceId
    ) public view override(ERC1155, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }

    function getOwner() public view returns (address) {
        return owner;
    }

    function getMarketAddress() public view returns (address) {
        return market;
    }

    function priceOf(uint256 _tokenId) public view returns (uint256) {
        require(_tokenId < _tokenId, "Asset Token ID does not exist.");

        return mintedAssets[_tokenId].price;
    }

    function updateHash(
        uint256 _tokenId,
        bytes32 _hash
    ) public onlyRole(MARKET_ROLE) returns (bool) {
        hashRecord[_hash] = _tokenId;
        return true;
    }

    function updateMarketAddress(
        address _market
    ) public onlyRole(MARKET_ROLE) returns (bool) {
        _revokeRole(MARKET_ROLE, market);
        market = _market;
        _grantRole(MARKET_ROLE, market);
        return true;
    }

    function isForSale(uint256 _tokenId) public view returns (bool) {
        return mintedAssets[_tokenId].forSale;
    }

    function updateSaleStatus(
        uint256 _tokenId,
        bool _status
    ) public onlyRole(MARKET_ROLE) {
        mintedAssets[_tokenId].forSale = _status;
    }

    function mintBatch(
        uint256[] memory _ids,
        uint256[] memory _amounts,
        uint256[] memory _prices
    ) public returns (bool) {
        require(msg.sender == owner, "Only owner can mint asset");

        require(
            _ids.length == _prices.length && _prices.length == _amounts.length,
            "ID, Amounts and Prices array must all be the same length"
        );

        _mintBatch(msg.sender, _ids, _amounts, "");

        for (uint256 i = 0; i < _ids.length; i++) {
            uint256 id = _ids[i];

            if (mintedAssets[id].price != 0) {
                continue;
            }

            mintedAssets[id].price = _prices[i];
        }

        return true;
    }

    /**
     * @dev return tokenURI
     */
    function tokenURI(uint256 _tokenId) public view returns (string memory) {
        return uri(_tokenId);
    }
}

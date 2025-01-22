// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "erc721a/contracts/IERC721A.sol";

interface IAssetAgreement is IERC721A {
    function getOwner() external view returns (address);

    function getOwnerRoyalty() external view returns (uint256);

    function updateOwnerRoyalty(uint256 _royalty) external;

    function getMarketAddress() external view returns (address);

    function getOwnerOfAssetFromHash(
        bytes32 _hash
    ) external view returns (address, uint256);

    function priceOf(uint256 _tokenId) external view returns (uint256);

    function updatePrice(uint256 _tokenId, uint256 _price) external;

    function updateHash(uint256 _tokenId, bytes32 _hash) external;

    function updateMarketAddress(address _market) external;

    function isForSale(uint256 _tokenId) external view returns (bool);

    function isResaleAllowed(uint256 _tokenId) external view returns (bool);

    function updateSaleStatus(uint256 _tokenId, bool _status) external;

    function updateAllowResaleStatus(uint256 _tokenId, bool _status) external;

    function mint(
        uint256[] memory _prices,
        bool[] memory _resaleAllowed
    ) external;

    function tokenURI(uint256 _tokenId) external view returns (string memory);
}

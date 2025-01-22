pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC1155/IERC1155.sol";

interface IAssetAgreement is IERC1155 {
    function agreementOwner() external view returns (address);

    function verifyAgreement(
        uint256 _tokenId,
        address _buyer
    ) external view returns (bool);

    function priceOf(uint256 _tokenId) external view returns (uint256);

    function hashOf(uint256 _tokenId) external view returns (string memory);

    function mintBatch(
        uint256[] memory _ids,
        uint256[] memory _amounts,
        uint256[] memory _prices,
        string[] memory _assetHashes
    ) external returns (bool);

    function mint(
        uint256 _id,
        uint256 _amount,
        uint256 _price,
        string memory _assetHash
    ) external returns (bool);

    /**
     * @dev return tokenURI
     */
    function tokenURI(uint256 _tokenId) external view returns (string memory);
}

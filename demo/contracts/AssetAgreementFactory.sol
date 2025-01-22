// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "./AssetAgreement.sol";

contract AssetAgreementFactory {
    event NewContract(address contractAddress);

    function createNewAssetAgreement(
        string memory _name,
        string memory _symbol,
        address _market
    ) public {
        AssetAgreement agreement = new AssetAgreement(
            _name,
            _symbol,
            msg.sender,
            _market
        );

        emit NewContract(address(agreement));
    }
}

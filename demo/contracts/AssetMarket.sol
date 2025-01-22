// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;
import "./IAssetAgreement.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract AssetMarket is Ownable {
    bool internal locked = false;

    uint256 marketRoyalty = 0;

    event Purchase(address from, address to, uint256 tokenId, uint256 price);

    modifier noReEntrancy() {
        require(!locked, "Re-entrancy not allowed");
        locked = true;
        _;
        locked = false;
    }

    /**
     * Traceability: Returns the transaction associated with the agreement and
     * respective hash of the watermarked image.
     *
     * @param _agreement the Asset Agreeement Address
     * @param _hash the hash of the watermarked image
     */
    function getAssetSaleRecord(
        address _agreement,
        bytes32 _hash
    ) public view returns (address, uint256) {
        IAssetAgreement agreement = IAssetAgreement(_agreement);
        return agreement.getOwnerOfAssetFromHash(_hash);
    }

    /**
     * Updates the hash of an asset for an agreement.
     *
     * Can only be called by Market.
     *
     * @param _agreement the Asset Agreeement Address
     * @param _tokenId the Token ID of the asset
     * @param _hash the hash of the watermarked image
     */
    function updateHash(
        address _agreement,
        uint256 _tokenId,
        bytes32 _hash
    ) public noReEntrancy onlyOwner {
        IAssetAgreement agreementContract = IAssetAgreement(_agreement);
        agreementContract.updateHash(_tokenId, _hash);
    }

    /**
     * Updates the Market Royalty
     *
     * Can only be called by Market.
     *
     * @param _newRoyalty the new Royalty Percentage Fee
     */
    function updateMarketRoyalty(uint256 _newRoyalty) public onlyOwner {
        require(
            0 <= _newRoyalty && _newRoyalty <= 1 ether,
            "Royalty Fee percentage must be between 0 and 1"
        );

        marketRoyalty = _newRoyalty;
    }

    /**
     * Withdraws all royalty fees to a specified account
     *
     * @param _to wallet address to send funds to
     */
    function withdrawRoyalty(address _to) public onlyOwner {
        payable(_to).transfer(address(this).balance);
    }

    /**
     * Update the sale status of an asset for an agreement
     *
     * @param _agreement the Asset Agreeement Address
     * @param _tokenId the Token ID of the asset
     * @param _status the new sale status
     */
    function updateSaleStatus(
        address _agreement,
        uint256 _tokenId,
        bool _status
    ) public noReEntrancy {
        IAssetAgreement agreementContract = IAssetAgreement(_agreement);

        // ensure that sender owns this Asset
        require(
            msg.sender == agreementContract.ownerOf(_tokenId),
            "Only Asset Owner can modify sale status"
        );

        agreementContract.updateSaleStatus(_tokenId, _status);
    }

    /**
     * Updates the price of an asset
     *
     * @param _agreement the Asset Agreeement Address
     * @param _tokenId the Token ID of the asset
     * @param _price the new price
     */
    function updatePrice(
        address _agreement,
        uint256 _tokenId,
        uint256 _price
    ) public noReEntrancy {
        IAssetAgreement agreementContract = IAssetAgreement(_agreement);

        // ensure that sender owns this Asset
        require(
            msg.sender == agreementContract.ownerOf(_tokenId),
            "Only Asset Owner can set price of asset"
        );

        // set new price
        agreementContract.updatePrice(_tokenId, _price);
    }

    /**
     * Processes the payment, ensuring Royalty Fees are paid to respective
     * parties
     *
     * @param _originalOwner the original data owner of the asset
     * @param _seller the party who is currently selling this asset
     * @param _ownerRoyalty the royalty fee percentage of the owners
     */
    function processPayment(
        address _originalOwner,
        address _seller,
        uint256 _ownerRoyalty
    ) private {
        // ensure owner's royalty fee percentage is between 0 and 1
        require(
            0 <= _ownerRoyalty && _ownerRoyalty <= 1 ether,
            "Owner royalty must be between 0 and 1 ether."
        );

        // compute market royalty
        uint256 marketCut = (msg.value * marketRoyalty) / 1 ether;

        // funds remaining after Market takes it's cut
        uint256 remaining = msg.value - marketCut;

        // for sales from original owner, we just transfer remaining funds
        // Otherwise, we compute the owner's cut from their royalty percentage
        if (_originalOwner == _seller) {
            payable(_originalOwner).transfer(remaining);
        } else {
            uint256 ownerCut = (remaining * _ownerRoyalty) / 1 ether;
            payable(_originalOwner).transfer(ownerCut);
            payable(_seller).transfer(remaining - ownerCut);
        }
    }

    /**
     * Purchase an asset
     *
     * @param _agreement Owner's Asset Agreement contract address
     * @param _tokenId Token ID of asset
     */
    function purchase(
        address _agreement,
        uint256 _tokenId
    ) public payable noReEntrancy {
        IAssetAgreement agreementContract = IAssetAgreement(_agreement);

        uint256 price = agreementContract.priceOf(_tokenId);

        // ensure buyer paid the correct price for the asset
        require(msg.value >= price, "Not enough ETH!");

        // ensure that the asset is for sale
        require(agreementContract.isForSale(_tokenId), "Asset is not for sale");

        address assetOwner = agreementContract.ownerOf(_tokenId);

        // transfer the asset from owner to buyer
        agreementContract.transferFrom(assetOwner, msg.sender, _tokenId);
        agreementContract.updateSaleStatus(_tokenId, false);

        // pay respective parties
        processPayment(
            agreementContract.getOwner(),
            assetOwner,
            agreementContract.getOwnerRoyalty()
        );

        emit Purchase(assetOwner, msg.sender, _tokenId, price);
    }
}

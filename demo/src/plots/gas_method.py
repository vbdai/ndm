from contract_local import AssetMarket, AssetFactory, AssetAgreement
from web3 import Web3
from json import dumps
from Crypto.Random import get_random_bytes
if __name__ == "__main__":
    LOCAL_ETH_ENDPOINT = "http://127.0.0.1:8545/"

    w3 = Web3(Web3.HTTPProvider(LOCAL_ETH_ENDPOINT))

    account = w3.eth.accounts[0]
    w3.eth.default_account = account

    market_address, market_gas = AssetMarket.deploy(
        LOCAL_ETH_ENDPOINT, account)
    factory_address, factory_gas = AssetFactory.deploy(
        LOCAL_ETH_ENDPOINT, account, market_address)

    factory = AssetFactory(LOCAL_ETH_ENDPOINT, factory_address, account)
    agreement_address, agreement_gas = factory.deploy_asset_agreement(
        "ASSET", "ASSET", market_address)
    agreement = AssetAgreement(LOCAL_ETH_ENDPOINT, agreement_address, account)
    market = AssetMarket(LOCAL_ETH_ENDPOINT, market_address, account)

    agreement_data = dict()
    agreement_data["AssetAgreement::mint"] = agreement.mint([0.01], [
                                                            True]).gasUsed
    agreement_data["AssetAgreement::updateMarketAddress"] = agreement.update_market_address(
        market_address).gasUsed
    agreement_data["AssetAgreement::updateOwnerRoyalty"] = agreement.update_owner_royalty(
        0.01).gasUsed
    agreement_data["AssetAgreement::updateAllowResaleStatus"] = agreement.update_allow_resale_status(
        0, True).gasUsed

    market_data = dict()
    market_data["AssetMarket::updateMarketRoyalty"] = market.update_market_royalty(
        0.02).gasUsed
    market_data["AssetMarket::updatePrice"] = market.update_price(
        agreement_address, 0, 0.02).gasUsed
    market_data["AssetMarket::purchase"] = market.purchase(
        agreement_address, 0, 0.02).gasUsed
    market_data["AssetMarket::updateSaleStatus"] = market.update_sale_status(
        agreement_address, 0, True).gasUsed
    market_data["AssetMarket::updateMarketRoyalty"] = market.update_market_royalty(
        0.02).gasUsed
    market_data["AssetMarket::updateHash"] = market.update_hash(
        agreement_address, 0, get_random_bytes(32)).gasUsed
    market_data["AssetMarket::withdrawRoyalty"] = market.withdraw_royalty(
        account).gasUsed

    approval_gas = agreement.set_approval_for_all(market_address, True).gasUsed

    import matplotlib.pyplot as plt
    from json import loads

    fig = plt.figure(figsize=(9, 6))
    plt.rc("font", size=14)
    plt.bar(list(map(lambda r: r.split("::")[1], agreement_data.keys())), list(
        agreement_data.values()), width=0.1, label="Asset Agreement Contract")
    plt.bar(list(map(lambda r: r.split("::")[1], market_data.keys())), list(
        market_data.values()), width=0.1, label="Asset Market Contract")
    plt.legend()
    plt.subplots_adjust(bottom=0.3, left=0.15)
    plt.xlabel("Smart Contract Method")
    plt.ylabel("Gas Consumption")
    plt.xticks(rotation=25, ha="right")
    plt.grid()
    plt.ticklabel_format(useOffset=False, style='sci',
                         axis='y', useMathText=True)
    plt.savefig("sc_method_gas.png")

    fig = plt.figure(figsize=(10, 8))
    plt.rc("font", size=16)
    plt.bar(["Market Contract", "Factory Contract", "Agreement Contract"], [
            market_gas, factory_gas, agreement_gas + approval_gas])
    plt.tight_layout(pad=2.3)
    # plt.xlabel("Contract Name", labelpad=10)
    plt.ylabel("Gas Consumption")
    plt.ticklabel_format(useOffset=False, style='sci',
                         axis='y', useMathText=True)
    plt.savefig("deploy_gas.png")

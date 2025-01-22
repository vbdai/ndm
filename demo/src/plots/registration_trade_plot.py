from contract_local import AssetMarket, AssetFactory, AssetAgreement
from web3 import Web3
from json import dumps
from Crypto.Random import get_random_bytes
import matplotlib.pyplot as plt
from json import loads

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

    mint_gas = agreement.mint([0.01], [True]).gasUsed
    approval_gas = agreement.set_approval_for_all(market_address, True).gasUsed
    purchase_gas = market.purchase(agreement_address, 0, 0.01).gasUsed
    update_gas = market.update_hash(
        agreement_address, 0, bytes([1 for _ in range(8)])).gasUsed

    agreement.set_approval_for_all(market_address, True)
    update_sale_status_gas = market.update_sale_status(
        agreement_address, 0, True).gasUsed

    plt.figure(figsize=(10, 8))
    plt.rc("font", size=16)
    print([mint_gas, purchase_gas + update_gas,
          purchase_gas + update_gas + update_sale_status_gas])
    plt.bar(["Data Registration", "Data Trade", "Data Resell"], [
            mint_gas, purchase_gas + update_gas, purchase_gas + update_gas + update_sale_status_gas])
    plt.tight_layout(pad=2.3)
    plt.subplots_adjust(bottom=0.15, left=0.15)
    plt.ylabel("Gas Consumption")
    # plt.xticks(rotation=25, ha="right")
    plt.ticklabel_format(axis="y", useMathText=True, scilimits=(0, 0))
    plt.savefig("registration_trade_gas.png")

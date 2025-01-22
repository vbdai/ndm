import matplotlib.pyplot as plt
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

    plt.bar(["Market Contract", "Factory Contract", "Agreement Contract"], [
            market_gas, factory_gas, agreement_gas])
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.1, left=0.1)
    plt.ylabel("Gas Consumption")
    plt.ticklabel_format(axis="y", useMathText=True, scilimits=(0, 0))
    plt.savefig("deploy_gas.png")

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

    a = agreement.mint([0.01], [True]).gasUsed
    b = agreement.mint([0.01, 0.01], [True, True]).gasUsed
    m = b - a
    b = a - m
    print("y = %dx + %d" % (m, b))

    import matplotlib.pyplot as plt
    import numpy as np

    fig = plt.figure(figsize=(8, 6))
    plt.rc("font", size=14)

    x = np.linspace(1, 101, 105)
    y = 14031 * x + 127299

    plt.plot(x, y, label="y = %dx + %d" % (m, b))

    plt.tight_layout()
    plt.subplots_adjust(left=0.1, bottom=0.1)
    plt.xlabel("Number of Assets")
    plt.ylabel("Gas Consumption")
    plt.xticks(np.arange(0, 101, 5))
    plt.grid()
    plt.legend()
    plt.savefig("batchmint.png")

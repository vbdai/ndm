from json import loads
from web3 import Web3
from web3.gas_strategies.time_based import medium_gas_price_strategy

PROVIDER_CACHE: 'dict[str, Web3]' = dict()


def get_web3_provider(endpoint):

    if endpoint not in PROVIDER_CACHE or not PROVIDER_CACHE[endpoint].isConnected():
        PROVIDER_CACHE[endpoint] = Web3(Web3.HTTPProvider(
            endpoint, request_kwargs={'verify': False}))
        # PROVIDER_CACHE[endpoint].eth.set_gas_price_strategy(medium_gas_price_strategy)
    return PROVIDER_CACHE[endpoint]


def get_abi(filename):

    abi_file = open(filename, "r")
    data = loads(abi_file.read())["abi"]
    abi_file.close()
    return data


def get_bytecode(filename):
    bytecode_file = open(filename, "r")
    data = loads(bytecode_file.read())["bytecode"]
    bytecode_file.close()
    return data


def get_market_abi():

    return get_abi("artifacts/contracts/AssetMarket.sol/AssetMarket.json")


def get_market_bytecode():

    return get_bytecode("artifacts/contracts/AssetMarket.sol/AssetMarket.json")


def get_factory_bytecode():

    return get_bytecode("artifacts/contracts/AssetAgreementFactory.sol/AssetAgreementFactory.json")


def get_factory_abi():

    return get_abi("artifacts/contracts/AssetAgreementFactory.sol/AssetAgreementFactory.json")


def get_agreement_abi():

    return get_abi("artifacts/contracts/AssetAgreement.sol/AssetAgreement.json")


def get_agreement_bytecode():

    return get_bytecode("artifacts/contracts/AssetAgreement.sol/AssetAgreement.json")


def get_agreement_erc1155_abi():

    return get_abi("artifacts/contracts/AssetAgreementERC1155.sol/AssetAgreement.json")


def get_agreement_erc1155_bytecode():

    return get_bytecode("artifacts/contracts/AssetAgreementERC1155.sol/AssetAgreement.json")


def get_Agreement_contract(endpoint: str, address: str, account: str):
    w3 = get_web3_provider(endpoint)
    w3.eth.default_account = account
    return w3.eth.contract(address=address, abi=get_agreement_abi())


def get_Agreement_ERC1155_contract(endpoint: str, address: str, account: str):
    w3 = get_web3_provider(endpoint)
    w3.eth.default_account = account
    return w3.eth.contract(address=address, abi=get_agreement_erc1155_abi())


def get_AssetFactory_contract(endpoint: str, address: str, account: str):
    w3 = get_web3_provider(endpoint)
    w3.eth.default_account = account
    return w3.eth.contract(address=address, abi=get_factory_abi())


def get_Market_contract(endpoint: str, address: str, account: str):

    w3 = get_web3_provider(endpoint)
    w3.eth.default_account = account

    return w3.eth.contract(address=address, abi=get_market_abi())

from json import loads
from provider import get_web3_provider
from Crypto.Util.strxor import strxor


def xor_cipher(data: bytes, key: bytes):

    xor_key = key * (len(data)//len(key)) + key[:len(data) % len(key)]

    return strxor(data, xor_key)


def get_market_abi():
    market_abi_file = open(
        "artifacts/contracts/AssetMarket.sol/AssetMarket.json", "r")
    market_abi = loads(market_abi_file.read())["abi"]

    return market_abi


def get_market_bytecode():
    market_abi_file = open(
        "artifacts/contracts/AssetMarket.sol/AssetMarket.json", "r")
    market_bytecode = loads(market_abi_file.read())["bytecode"]

    return market_bytecode


def get_factory_bytecode():
    factory_bytecode_file = open(
        "artifacts/contracts/AssetAgreementFactory.sol/AssetAgreementFactory.json", "r")
    factory_bytecode = loads(factory_bytecode_file.read())["bytecode"]

    return factory_bytecode


def get_factory_abi():
    factory_abi_file = open(
        "artifacts/contracts/AssetAgreementFactory.sol/AssetAgreementFactory.json", "r")
    factory_abi = loads(factory_abi_file.read())["abi"]

    return factory_abi


def get_agreement_abi():
    agreement_abi_file = open(
        "artifacts/contracts/AssetAgreement.sol/AssetAgreement.json", "r")
    agreement_abi = loads(agreement_abi_file.read())["abi"]

    return agreement_abi


def get_agreement_bytecode():
    agreement_bytecode_file = open(
        "artifacts/contracts/AssetAgreement.sol/AssetAgreement.json", "r")
    agreement_bytecode = loads(agreement_bytecode_file.read())["bytecode"]

    return agreement_bytecode


def get_Agreement_contract(endpoint: str, address: str, account: str):
    w3 = get_web3_provider(endpoint)
    w3.eth.default_account = account
    return w3.eth.contract(address=address, abi=get_agreement_abi())


def get_AssetFactory_contract(endpoint: str, address: str, account: str):
    w3 = get_web3_provider(endpoint)
    w3.eth.default_account = account
    return w3.eth.contract(address=address, abi=get_factory_abi())


def get_Market_contract(endpoint: str, address: str, account: str):

    w3 = get_web3_provider(endpoint)
    w3.eth.default_account = account

    return w3.eth.contract(address=address, abi=get_market_abi())

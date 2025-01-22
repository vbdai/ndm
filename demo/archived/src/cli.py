from functools import reduce
from tempfile import NamedTemporaryFile
from urllib3.connection import HTTPConnection
import socket
from json import dumps
from base64 import b64decode, b64encode
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from shutil import move
from os.path import join, realpath, basename
from glob import glob
import csv
from ssl_watermarking.main_multibit import Watermark
from argparse import ArgumentParser
from cli_utils import get_web3_provider, get_factory_abi, get_factory_bytecode, get_agreement_erc1155_abi, get_agreement_erc1155_bytecode, get_market_abi, get_market_bytecode, get_AssetFactory_contract, get_Market_contract, get_Agreement_contract, get_Agreement_ERC1155_contract
from time import time
from web3 import Web3
import os
os.environ["PYTHONWARNINGS"] = "ignore:Unverified HTTPS request"


LOCAL_ETH_ENDPOINT = "http://127.0.0.1:8545/"
LOCAL_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
GOERLI_TEST_ACCOUNT_PRIVATE_KEY = "0320072181e1ba70ecd8b9ac11500cda0d1b7c9a1c73d9e2ef59b76524f16e02"
INFURA_GOERLI_ENDPOINT = "https://goerli.infura.io/v3/123f44c9b3ed4475abfe6a19d8af33c6"
ALCHEMY_GOERLI_ENDPOINT = "https://eth-goerli.g.alchemy.com/v2/fTYyXArUCpY8yDBdvMgi9CTtQHNQdvjC"
ALCHEMY_TEST_ACCOUNT_PRIVATE_KEY = "ca29dd62b1dddb3a95936f13e044612f6b4665f64ee83acadcdd2e2c686f7d19"

NONCE = None

DATA = {
    "factory": {
        "gas": 0,
        "time": 0
    },
    "market": {
        "gas": 0,
        "time": 0,
    },
    "agreement": {
        "gas": 0,
        "time": 0
    },
    "agreement_erc1155": {
        "gas": 0,
        "time": 0
    },
    "data": []
}


ENDPOINT = LOCAL_ETH_ENDPOINT
PRIVATE_KEY = LOCAL_PRIVATE_KEY


def encrypt_image(img_location: str, short_hash: str = ""):

    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CFB)

    data = None
    with open(img_location, "rb") as f:
        data = f.read()

    data = cipher.encrypt(data)

    with open(img_location, "wb") as f:
        f.write(data)

    with open("key_%s.json" % short_hash, "w") as f:
        f.write(dumps({
            "key": b64encode(key).decode('utf-8'),
            "iv": b64encode(cipher.iv).decode('utf-8')
        }))

    return key, cipher.iv


def decrypt_image(img_location: str, key: bytes, iv: bytes):

    img_data = open(img_location, "rb").read()

    cipher = AES.new(key, AES.MODE_CFB, iv=iv)

    return cipher.decrypt(img_data)


class Contract:

    W3_PROVIDER = get_web3_provider(ENDPOINT)

    def __init__(self, w3_endpoint: str) -> None:
        self.w3 = Contract.W3_PROVIDER

    @staticmethod
    def sendTransaction(endpoint: str, tx):

        global NONCE

        w3 = Contract.W3_PROVIDER
        account = w3.eth.account.privateKeyToAccount(
            PRIVATE_KEY)
        w3.eth.default_account = account.address

        if NONCE is None:
            NONCE = w3.eth.get_transaction_count(account.address)
        NONCE += 1
        tx["nonce"] = NONCE

        tx["gasPrice"] = Web3.to_wei(20, "gwei")

        signed = w3.eth.account.signTransaction(
            tx, PRIVATE_KEY)

        tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)

        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return tx_receipt


class AssetFactory(Contract):

    def __init__(self, http_endpoint: str, factory_address: str, owner_address: str) -> None:
        super().__init__(http_endpoint)
        self.http_endpoint = http_endpoint
        self.owner_address = owner_address
        self.factory_contract = get_AssetFactory_contract(
            http_endpoint, factory_address, owner_address)

    def deploy_asset_agreement(self, market_address: str) -> str:

        tx = self.factory_contract.functions.createNewAssetAgreement(
            market_address).buildTransaction()

        tx_receipt = self.sendTransaction(self.http_endpoint, tx)
        DATA["agreement"]["gas"] = tx_receipt.gasUsed

        data = self.factory_contract.events.NewContract().process_receipt(tx_receipt)

        contract_address = data[0]["args"]["contractAddress"]

        return contract_address

    @staticmethod
    def deploy(http_endpoint: str, owner_address: str):
        w3 = Contract.W3_PROVIDER
        w3.eth.default_account = owner_address

        w3_contract = w3.eth.contract(
            abi=get_factory_abi(), bytecode=get_factory_bytecode())

        print("Deploying Asset Factory Contract with wallet: %s" %
              w3.eth.default_account)

        tx = w3_contract.constructor().buildTransaction()

        tx_receipt = Contract.sendTransaction(http_endpoint, tx)

        DATA["factory"]["gas"] = tx_receipt.gasUsed

        return tx_receipt.contractAddress


class AssetMarket(Contract):

    def __init__(self, http_endpoint: str, market_address: str, buyer_address: str) -> None:
        super().__init__(http_endpoint)
        self.http_endpoint = http_endpoint
        self.buyer = buyer_address
        self.market_address = market_address
        self.market_contract = get_Market_contract(
            http_endpoint, market_address, buyer_address)

    @staticmethod
    def deploy(http_endpoint: str, wallet_address: str):
        w3 = Contract.W3_PROVIDER
        w3.eth.default_account = wallet_address

        w3_contract = w3.eth.contract(
            abi=get_market_abi(), bytecode=get_market_bytecode())

        print("Deploying Asset Market Contract with wallet: %s" %
              w3.eth.default_account)

        tx = w3_contract.constructor().buildTransaction()
        tx_receipt = Contract.sendTransaction(http_endpoint, tx)

        DATA["market"]["gas"] = tx_receipt.gasUsed

        return tx_receipt.contractAddress

    def get_asset_sale_record(self, agreement_address: str, hash: bytes):
        record = self.market_contract.functions.getAssetSaleRecord(
            agreement_address, hash).call()
        return record

    def update_hash(self, agreement_address: str, tokenID: int, hash: bytes):
        tx = self.market_contract.functions.updateHash(
            agreement_address, tokenID, hash).buildTransaction()
        self.sendTransaction(self.http_endpoint, tx)

    def purchase_asset(self, agreement_address: str, tokenID: int, price: float):
        wei_price = Web3.to_wei(price, "ether")
        tx = self.market_contract.functions.purchase(
            agreement_address, tokenID).buildTransaction({"value": wei_price})
        return self.sendTransaction(self.http_endpoint, tx)


class AssetAgreementERC1155(Contract):

    def __init__(self, w3_endpoint: str, agreement_address: str, owner_address: str) -> None:
        super().__init__(w3_endpoint)
        self.http_endpoint = w3_endpoint
        self.agreement_address = agreement_address
        self.agreement_contract = get_Agreement_ERC1155_contract(
            w3_endpoint, agreement_address, owner_address)

    @staticmethod
    def deploy(http_endpoint: str, owner_address: str):

        w3 = Contract.W3_PROVIDER

        w3.eth.default_account = owner_address

        w3_contract = w3.eth.contract(
            abi=get_agreement_erc1155_abi(), bytecode=get_agreement_erc1155_bytecode())

        tx = w3_contract.constructor(owner_address).buildTransaction()

        tx_receipt = Contract.sendTransaction(http_endpoint, tx)
        DATA["agreement_erc1155"]["gas"] = tx_receipt.gasUsed

        return tx_receipt.contractAddress

    def mintBatch(self, ids: 'list[int]', amounts: 'list[int]', prices: 'list[float]', uris: 'list[str]'):

        prices = list(map(lambda r: Web3.to_wei(r, "ether"), prices))

        tx = self.agreement_contract.functions.mintBatch(
            ids, amounts, prices, uris).buildTransaction()

        tx_receipt = Contract.sendTransaction(self.http_endpoint, tx)

        return tx_receipt


class AssetAgreement(Contract):

    def __init__(self, http_endpoint: str, agreement_address: str, owner_address: str) -> None:
        super().__init__(http_endpoint)
        self.endpoint = http_endpoint
        self.agreement_contract = get_Agreement_contract(
            http_endpoint, agreement_address, owner_address)

    def price_of(self, tokenID: int):
        value = self.agreement_contract.functions.priceOf(tokenID).call()
        value = Web3.from_wei(value, "ether")

        return float(value)

    def set_approval_for_all(self, operator: str, approved: bool):
        tx = self.agreement_contract.functions.setApprovalForAll(
            operator, approved).buildTransaction()

        self.sendTransaction(self.endpoint, tx)

    def get_owner_of_asset_from_hash(self, hash: bytes):
        address = self.agreement_contract.functions.getOwnerOfAssetFromHash(
            hash).call()
        return address

    def mint_asset(self, URI: str, price: float, market_address: str):

        wei = Web3.to_wei(price, "ether")

        # mint the new NFT
        tx = self.agreement_contract.functions.mint(
            URI, wei).buildTransaction()
        tx_receipt = self.sendTransaction(self.endpoint, tx)
        self.set_approval_for_all(market_address, True)

        return tx_receipt

    def token_uri(self, tokenID: int):

        uri = self.agreement_contract.functions.tokenURI(tokenID).call()

        return uri


class CLI:

    def __init__(self, http_endpoint: str) -> None:

        self.endpoint = http_endpoint

        self.watermark = Watermark()

        self.web3 = Contract.W3_PROVIDER
        self.web3.eth.default_account = self.get_wallet_address()

        start = time()
        self.factory_address = AssetFactory.deploy(
            self.endpoint, self.get_wallet_address())
        end = time()

        DATA["factory"]["time"] = end - start

        self.factory = AssetFactory(
            self.endpoint, self.factory_address, self.get_wallet_address())

        start = time()
        self.market_address = AssetMarket.deploy(
            self.endpoint, self.get_wallet_address())
        end = time()

        DATA["market"]["time"] = end - start

        self.market = AssetMarket(
            self.endpoint, self.market_address, self.get_wallet_address())

        print("Market Deploy Time Taken: %f" % (end - start))

        start = time()
        self.agreement_address = self.factory.deploy_asset_agreement(
            self.market_address)
        end = time()
        DATA["agreement"]["time"] = end - start

        self.agreement = AssetAgreement(
            self.endpoint, self.agreement_address, self.get_wallet_address())

        start = time()
        self.agreement_erc1155_address = AssetAgreementERC1155.deploy(
            self.endpoint, self.get_wallet_address())
        end = time()

        self.agreement_erc1155 = AssetAgreementERC1155(
            self.endpoint, self.agreement_erc1155_address, self.get_wallet_address())
        DATA["agreement_erc1155"]["time"] = end - start

    def get_wallet_address(self):

        if self.endpoint == INFURA_GOERLI_ENDPOINT:
            account = self.web3.eth.account.privateKeyToAccount(
                GOERLI_TEST_ACCOUNT_PRIVATE_KEY)
            return account.address

        return self.web3.eth.accounts[0]

    def copy_image(self, img_filepath: str):

        img_ext = img_filepath.split(".")[-1]

        temp = NamedTemporaryFile("wb", delete=False, suffix="." + img_ext)

        temp.write(open(img_filepath, "rb").read())

        temp.close()

        return temp.name

    def watermark_image(self, img_filepath: str):

        img_copy = self.copy_image(img_filepath)

        self.watermark.watermark_image(img_copy)

        img_dir = "/".join(img_filepath.split("/")[:-1])

        img_name, img_ext = basename(img_filepath).split(".")

        new_path = join(img_dir, "%s_out.%s" % (img_name, img_ext))

        move(img_copy, new_path)

    def extract_watermark(self, img_filepath: str):
        return self.watermark.extract_watermark(img_filepath)

    def average_of(data: 'list[dict]', key: str):

        values = map(lambda r: r[key], data)

        return sum(values)/len(values)

    def measure_batch_mint(self, N: int):

        ids = [i for i in range(N)]
        amounts = [1 for _ in range(N)]
        prices = [0.02 for _ in range(N)]
        uris = ["x" * 32 for _ in range(N)]

        start = time()
        receipt = self.agreement_erc1155.mintBatch(ids, amounts, prices, uris)
        end = time()
        erc1155_time = end - start
        erc1155_gas = receipt.gasUsed

        return (erc1155_time, erc1155_gas)

    def tx_transfers(self):

        receipt = self.agreement.mint_asset("Hello", 0.01, self.market_address)

        data = self.agreement.agreement_contract.events.NewTokenId().process_receipt(receipt)
        self.agreement.set_approval_for_all(self.market_address, True)
        id = data[0]["args"]["tokenId"]

        self.market.purchase_asset(self.agreement_address, id, 0.01)

        return self.agreement.agreement_contract.events.Transfer.get_logs()

    def batch_mint_performance(self, limit: int):
        data = []
        single_mint_data = []

        for r in range(limit):
            print("Processing Single Mint #%d..." % r)
            start = time()
            receipt = self.agreement.mint_asset(
                "x" * 32, 0.02, self.market_address)
            end = time()

            erc721_gas = receipt.gasUsed
            erc721_time = end - start

            single_mint_data.append((erc721_time, erc721_gas))

        for r in range(5, limit + 1, 5):
            print("Processing Batch Mint #%d..." % (r // 5))

            (time_1155, gas_1155) = self.measure_batch_mint(r)

            (time_721, gas_721) = reduce(lambda accum, v: (
                accum[0] + v[0], accum[1] + v[1]), single_mint_data[:r], (0, 0))

            data.append({
                "num_assets": r,
                "erc721": {
                    "gas": gas_721,
                    "time": time_721
                },
                "erc1155": {
                    "gas": gas_1155,
                    "time": time_1155
                }
            })

        open("batch_mint_performance.json", "w").write(dumps(data))

    def demo_performance(self, files: 'list[str]', metrics: 'list[str]'):

        for f in files:
            data = dict()
            encrypt_key = None
            encrypt_iv = None
            tokenId = -1

            data["filename"] = f

            if "mint" in metrics or "mint+purchase" in metrics:

                start = time()
                receipt = self.agreement.mint_asset(
                    "HelloWorld", 0.01, self.market_address)
                end = time()

                tx_data = self.agreement.agreement_contract.events.NewTokenId().process_receipt(receipt)
                self.agreement.set_approval_for_all(self.market_address, True)

                tokenId = tx_data[0]["args"]["tokenId"]

                data["mint_time"] = end - start
                data["mint_gas"] = receipt.gasUsed

            if "embedwatermark" or "embed+extractwatermark" in metrics:
                start = time()
                self.watermark_image(f)
                end = time()
                data["embedwatermark_time"] = end - start

            if "embed+extractwatermark" in metrics:
                start = time()
                self.extract_watermark(f)
                end = time()
                data["extractwatermark_time"] = end - start

            if "encrypt" in metrics or "encrypt+decrypt" in metrics:
                start = time()
                encrypt_key, encrypt_iv = encrypt_image(f)
                end = time()
                data["encrypt_time"] = end - start

            if "mint+purchase" in metrics:
                start = time()
                receipt = self.market.purchase_asset(
                    self.agreement_address, tokenId, 0.01)
                end = time()
                data["purchase_time"] = end - start
                data["purchase_gas"] = receipt.gasUsed

            if "encrypt+decrypt" in metrics:
                start = time()
                decrypt_image(f, encrypt_key, encrypt_iv)
                end = time()
                data["decrypt_time"] = end - start

            DATA["data"].append(data)

        open("metrics.json", "w").write(dumps(DATA))


if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument("-i", action="store", type=str,
                        help="Input directory. Creates directory if not exists")
    parser.add_argument("--metrics", type=str, nargs="+", choices=[
                        "embedwatermark", "embed+extractwatermark", "mint", "mint+purchase", "encrypt", "encrypt+decrypt"])

    args = parser.parse_args()

    cli = CLI(ENDPOINT)

    # files = glob(join(args.i, "*"))

    print(cli.tx_transfers())

    # cli.batch_mint_performance(1)

    # cli.demo_performance(files, args.metrics)

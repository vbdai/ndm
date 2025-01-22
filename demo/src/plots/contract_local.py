from web3 import Web3
from json import loads

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


class Contract:

    PRIVATE_KEY: str = None
    W3_PROVIDER: Web3 = None
    NONCE: int = None

    def __init__(self, w3_endpoint: str) -> None:
        self.endpoint = w3_endpoint
        self.w3 = get_web3_provider(w3_endpoint)

    def set_web3_provider(endpoint: str):
        Contract.W3_PROVIDER = get_web3_provider(endpoint)

        if Contract.PRIVATE_KEY is not None:
            Contract.W3_PROVIDER.eth.default_account = Contract.W3_PROVIDER.eth.account.from_key(
                Contract.PRIVATE_KEY)

    @staticmethod
    def send_contract_call(call, value: float = None):

        if Contract.PRIVATE_KEY is not None:

            txn = call.buildTransaction() if value is None else call.buildTransaction({
                "value": Web3.to_wei(value, "ether")})

            account_address = Contract.W3_PROVIDER.eth.account.from_key(
                Contract.PRIVATE_KEY).address

            if Contract.NONCE is None:
                Contract.NONCE = Contract.W3_PROVIDER.eth.get_transaction_count(
                    account_address)
            else:
                Contract.NONCE += 1

            txn["nonce"] = Contract.NONCE

            signed_txn = Contract.W3_PROVIDER.eth.account.sign_transaction(
                txn, Contract.PRIVATE_KEY)
            return Contract.W3_PROVIDER.eth.send_raw_transaction(signed_txn.rawTransaction)
        else:

            return call.transact({'value': Web3.to_wei(value, "ether")}) if value is not None else call.transact()

    @staticmethod
    def set_private_key(key: str):
        Contract.PRIVATE_KEY = key

    def get_wallet_address(self, default=None):

        if Contract.PRIVATE_KEY is None:

            return self.w3.eth.accounts[0] if default is None else default

        account = self.w3.eth.account.from_key(Contract.PRIVATE_KEY)
        self.w3.eth.default_account = account.address

        return account.address


class AssetFactory(Contract):

    def __init__(self, http_endpoint: str, factory_address: str, owner_address: str = None) -> None:
        super().__init__(http_endpoint)
        self.owner_address = self.get_wallet_address(default=owner_address)
        self.factory_contract = get_AssetFactory_contract(
            http_endpoint, factory_address, self.get_wallet_address(default=owner_address))

    def deploy_asset_agreement(self, name: str, symbol: str, market_address: str = None) -> str:

        tx_hash = Contract.send_contract_call(self.factory_contract.functions.createNewAssetAgreement(name, symbol,
                                                                                                      market_address))
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(
            tx_hash, timeout=600)

        data = self.factory_contract.events.NewContract().process_receipt(tx_receipt)

        contract_address = data[0]["args"]["contractAddress"]

        return contract_address, tx_receipt.gasUsed

    @staticmethod
    def deploy(http_endpoint: str, owner_address: str, market_address: str):
        w3 = Web3(Web3.HTTPProvider(http_endpoint))
        w3.eth.default_account = owner_address

        w3_contract = w3.eth.contract(
            abi=get_factory_abi(), bytecode=get_factory_bytecode())

        tx_hash = Contract.send_contract_call(
            w3_contract.constructor(market_address))

        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)

        return tx_receipt.contractAddress, tx_receipt.gasUsed


class AssetMarket(Contract):

    def __init__(self, http_endpoint: str, market_address: str, buyer_address: str = None) -> None:
        super().__init__(http_endpoint)
        self.address = market_address
        self.buyer = self.get_wallet_address(default=buyer_address)
        self.market_contract = get_Market_contract(
            http_endpoint, market_address, self.buyer)

    @staticmethod
    def deploy(http_endpoint: str, wallet_address: str = None):
        w3 = get_web3_provider(http_endpoint)
        w3.eth.default_account = wallet_address

        w3_contract = w3.eth.contract(
            abi=get_market_abi(), bytecode=get_market_bytecode())

        tx_hash = Contract.send_contract_call(w3_contract.constructor())

        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)

        return tx_receipt.contractAddress, tx_receipt.gasUsed

    def get_asset_sale_record(self, agreement_address: str, hash: bytes):
        return self.market_contract.functions.getAssetSaleRecord(agreement_address, hash).call()

    def update_hash(self, agreement_address: str, tokenID: int, hash: bytes):
        tx_hash = Contract.send_contract_call(self.market_contract.functions.updateHash(
            agreement_address, tokenID, hash))
        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)

    def update_market_royalty(self, royalty: float):

        v = Web3.to_wei(royalty, "ether")

        tx_hash = Contract.send_contract_call(self.market_contract.functions.updateMarketRoyalty(
            v))
        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)

    def withdraw_royalty(self, address: str):

        tx_hash = Contract.send_contract_call(self.market_contract.functions.withdrawRoyalty(
            address))

        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)

    def update_sale_status(self, agreement: str, tokenID: int, status: bool):
        tx_hash = Contract.send_contract_call(self.market_contract.functions.updateSaleStatus(
            agreement,  tokenID, status))

        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)

    def update_price(self, agreement: str, tokenID: int, price: float):
        v = Web3.to_wei(price, "ether")
        tx_hash = Contract.send_contract_call(self.market_contract.functions.updatePrice(
            agreement, tokenID, v))
        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)

    def purchase(self, agreement_address: str, tokenID: int, price: float):
        tx_hash = Contract.send_contract_call(self.market_contract.functions.purchase(
            agreement_address, tokenID), price)
        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)


class AssetAgreement(Contract):

    def __init__(self, http_endpoint: str, agreement_address: str, owner_address: str = None) -> None:
        super().__init__(http_endpoint)
        self.agreement_contract = get_Agreement_contract(
            http_endpoint, agreement_address, self.get_wallet_address(default=owner_address))

    def get_owner(self):
        return self.agreement_contract.functions.getOwner().call()

    def get_owner_royalty(self):
        return self.agreement_contract.functions.getOwnerRoyalty().call()

    def update_owner_royalty(self, royalty: float):

        v = Web3.to_wei(royalty, "ether")

        tx_hash = Contract.send_contract_call(self.agreement_contract.functions.updateOwnerRoyalty(
            v))

        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)

    def get_market_address(self):

        return self.agreement_contract.functions.getMarketAddress().call()

    def get_owner_of_asset_from_hash(self, hash: bytes):
        address = self.agreement_contract.functions.getOwnerOfAssetFromHash(
            hash).call()
        return address

    def price_of(self, tokenID: int):
        value = self.agreement_contract.functions.priceOf(tokenID).call()
        value = Web3.from_wei(value, "ether")
        return float(value)

    def update_market_address(self, address: str):

        tx_hash = Contract.send_contract_call(self.agreement_contract.functions.updateMarketAddress(
            address))
        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)

    def is_for_sale(self, tokenID: int):

        return self.agreement_contract.functions.isForSale(tokenID).call()

    def is_resale_allowed(self, tokenID: int):

        return self.agreement_contract.functions.isResaleAllowed(tokenID).call()

    def update_sale_status(self, tokenID: int, status: bool):

        tx_hash = Contract.send_contract_call(self.agreement_contract.functions.updateSaleStatus(
            tokenID, status))

        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)

    def update_allow_resale_status(self, tokenID: int, status: bool):
        tx_hash = Contract.send_contract_call(self.agreement_contract.functions.updateAllowResaleStatus(
            tokenID, status))

        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)

    def mint(self, prices: 'list[float]', resaleAllowed: 'list[bool]'):
        v = list(map(lambda r: Web3.to_wei(r, "ether"), prices))
        tx_hash = Contract.send_contract_call(self.agreement_contract.functions.mint(
            v, resaleAllowed))

        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)

    def set_approval_for_all(self, operator: str, approved: bool):
        tx_hash = Contract.send_contract_call(self.agreement_contract.functions.setApprovalForAll(
            operator, approved))
        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)

    def token_uri(self, tokenID: int):

        uri = self.agreement_contract.functions.tokenURI(tokenID).call()

        return uri

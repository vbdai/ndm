import streamlit as st
from utils import get_web3_provider
from database import Database
from constants import LOCAL_ENDPOINT
from contract import AssetFactory, AssetMarket


class OwnerRegistration:

    OWNER_DB = Database("owner.json")

    def __init__(self, factory_address: str, market_address: str) -> None:
        self.web3 = get_web3_provider(LOCAL_ENDPOINT)
        self.factory_address = factory_address
        self.market_address = market_address
        self.ownerdb = OwnerRegistration.OWNER_DB

    def register_owner(self, name: str, address: str):

        owners = self.ownerdb.read("owners")
        max_id = self.ownerdb.read("max_id")

        if max_id is None:
            max_id = 0

        if owners is None:
            owners = []

        factory = AssetFactory(LOCAL_ENDPOINT, self.factory_address, address)
        agreement = factory.deploy_asset_agreement(self.market_address)
        owners.append({
            "id": max_id,
            "name": name,
            "address": address,
            "agreement": agreement
        })

        self.ownerdb.write("owners", owners)
        self.ownerdb.write("max_id", max_id + 1)

        with st.expander("Log"):
            st.write("1. Added owner information to Marketplace Database")
            # st.write("2. Called AssetFactory Contract to deploy new asset agreeement")
            st.write(
                "2. New asset contract deployed for owner. Address: %s" % agreement)

    @staticmethod
    def get_owner_with_prop(key, value):

        for o in OwnerRegistration.get_owners():
            if key in o and o[key] == value:
                return o

        return None

    @staticmethod
    def get_owners():
        owners = OwnerRegistration.OWNER_DB.read("owners")

        return [] if owners is None else owners

    @staticmethod
    def find_owner_with_name(name):
        return OwnerRegistration.get_owner_with_prop("name", name)

    def _get_web3_accounts(self) -> 'list[str]':
        return self.web3.eth.accounts

    def render(self):
        st.write("## Owner Registration")
        st.write("New owners can register on our Marketplace")
        with st.form("owner-register-form", clear_on_submit=True):
            name = st.text_input("Name")

            address = st.text_input("Wallet Address")

            submit = st.form_submit_button("Register")

            if len(name) == 0 or len(address) == 0:
                return

            if not submit:
                return

            address = address.strip(" \n\t\r")

            self.register_owner(name, address)

            st.write("%s has been added!" % name)

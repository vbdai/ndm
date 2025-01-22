import streamlit as st
from utils import get_web3_provider
from database import Database
from constants import LOCAL_ENDPOINT


class BuyerRegistration:

    BUYER_DB = Database("buyer.json")

    def __init__(self) -> None:
        self.web3 = get_web3_provider(LOCAL_ENDPOINT)

        self.buyerdb = BuyerRegistration.BUYER_DB

    def register_buyer(self, name: str, address: str):

        buyers = self.buyerdb.read("buyers")
        max_id = self.buyerdb.read("max_id")

        if max_id is None:
            max_id = 0

        if buyers is None:
            buyers = []

        buyers.append({
            "id": max_id,
            "name": name,
            "address": address
        })

        self.buyerdb.write("buyers", buyers)
        self.buyerdb.write("max_id", max_id + 1)

    @staticmethod
    def get_buyers():
        buyers = BuyerRegistration.BUYER_DB.read("buyers")

        return [] if buyers is None else buyers

    @staticmethod
    def get_buyer_with_prop(key, value):

        for b in BuyerRegistration.get_buyers():

            if key in b and b[key] == value:
                return b

        return None

    def _get_web3_accounts(self) -> 'list[str]':

        return self.web3.eth.accounts

    def render(self):
        st.write("## Buyer Registration")
        st.write("New buyers can register on our Marketplace")
        with st.form("buyer-register-form", clear_on_submit=True):
            name = st.text_input("Name")

            address = st.text_input("Wallet Address")

            submit = st.form_submit_button("Register")

            if len(name) == 0 or len(address) == 0:
                return

            if not submit:
                return

            address = address.strip(" \n\r\t")

            self.register_buyer(name, address)

            st.write("%s has been added!" % name)

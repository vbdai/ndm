import streamlit as st
from web3 import Web3


def get_web3_provider(w3_endpoint):

    if "W3_PROVIDER" not in st.session_state:
        st.session_state["W3_PROVIDER"] = Web3(Web3.HTTPProvider(w3_endpoint))

    provider: Web3 = st.session_state["W3_PROVIDER"]

    if not provider.is_connected():
        provider = Web3(Web3.HTTPProvider(w3_endpoint))
        st.session_state["W3_PROVIDER"] = provider

    return provider

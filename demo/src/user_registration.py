import streamlit as st
from constants import LOCAL_ENDPOINT
from contract import get_web3_provider
from db import get_demo_db


class UserRegistration:

    def __init__(self) -> None:
        self.web3 = get_web3_provider(LOCAL_ENDPOINT)

    @staticmethod
    def register_user(name: str, address: str):

        con = get_demo_db()

        res = con.execute(
            "SELECT COUNT(*) FROM users WHERE uname = ? OR wallet = ?", [name, address])

        n, = res.fetchone()

        if n > 0:
            return False

        con.execute("INSERT INTO users (uname, wallet) VALUES (?, ?)", [
                    name, address])
        con.commit()
        con.close()
        return True

    @staticmethod
    def render():
        st.write("## User Registration")
        st.write("New users can register on our Marketplace")
        with st.form("user-register-form", clear_on_submit=True):
            name = st.text_input("Name")

            address = st.text_input("Wallet Address")

            submit = st.form_submit_button("Register")

            if len(name) == 0 or len(address) == 0:
                return

            if not submit:
                return

            address = address.strip(" \n\t\r")

            if UserRegistration.register_user(name, address):

                st.write("%s has been added!" % name)
            else:
                st.write("Name or Wallet Address already in use!")

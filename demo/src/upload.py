import streamlit as st
from os.path import basename, join
from uuid import uuid4
from contract import AssetAgreement, AssetFactory
from constants import LOCAL_ENDPOINT
from db import get_demo_db


class Upload:

    def __init__(self, factory_address: str, market_address: str) -> None:
        self.market_address = market_address
        self.factory_address = factory_address

    def render(self):
        st.write("## Publish Asset")
        st.write("Owners publish the asset they would like to sell to Marketplace")
        con = get_demo_db()

        with st.form("asset-upload"):

            res = con.execute("SELECT uname FROM users")

            owner = st.selectbox("Owner", options=map(
                lambda r: r[0], res.fetchall()))

            asset = st.file_uploader("Asset")
            price = st.number_input("Price (ETH)", min_value=0.0, step=0.01)
            resale = st.checkbox("Resale Allowed")
            submit = st.form_submit_button("Publish")

            if owner is None:
                return

            if not submit or asset is None:
                return

            data = asset.getvalue()
            filename = basename(asset.name)
            ext = filename.split(".")[-1]

            new_file_name = uuid4().hex + "." + ext

            new_file_location = join("images", new_file_name)

            with open(new_file_location, "wb") as f:
                f.write(data)

            res = con.execute(
                "SELECT id, wallet, agreement FROM users WHERE uname = ?", [owner])

            owner_id, owner_wallet, owner_agreement = res.fetchone()

            if owner_agreement is None:
                owner_agreement = AssetFactory(LOCAL_ENDPOINT, self.factory_address, owner_wallet).deploy_asset_agreement(
                    "ASSET", "ASSET", self.market_address)[0]
                agreement = AssetAgreement(
                    LOCAL_ENDPOINT, owner_agreement, owner_wallet)
                agreement.set_approval_for_all(self.market_address, True)

                con.execute("UPDATE users SET agreement = ? WHERE id = ?", [
                            owner_agreement, owner_id])
                con.commit()

            agreement = AssetAgreement(
                LOCAL_ENDPOINT, owner_agreement, owner_wallet)

            token_id = agreement.get_next_token_id()
            agreement.mint([price], [resale])

            res = con.execute("INSERT INTO assets (owner_id, filepath, token_id) VALUES (?, ?, ?)", [
                              owner_id, new_file_location, token_id])
            con.commit()
            st.write("Asset %s has been uploaded with Token ID: %d" %
                     (asset.name, token_id))
            with st.expander("Publish Log"):

                st.write("1. Find/Publish Owner's Asset Agreement contract: %s" %
                         owner_agreement)
                st.write("2. Encrypted Asset with Market Public Key")
                st.write("3. Upload Asset to Data Storage Server")
                st.write("4. Minting Asset... Token ID: %d" % token_id)
                st.write(
                    "5. Approve Market Address to transfer assets on behalf of owner")
        con.close()

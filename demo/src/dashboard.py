import streamlit as st
from upload import Upload
from contract import AssetAgreement, AssetMarket
from PIL import Image
from constants import LOCAL_ENDPOINT
from web3 import Web3
from db import get_demo_db


class Dashboard:

    def __init__(self, market_address: str) -> None:
        self.market_address = market_address

    def render(self):
        st.write("## Dashboard")
        st.write("View Purchased Assets")

        con = get_demo_db()
        res = con.execute("SELECT uname FROM users")
        user = st.selectbox("User", map(lambda r: r[0], res.fetchall()))

        res = con.execute(
            "SELECT users.wallet FROM users WHERE users.uname = ?", [user])

        if (d := res.fetchone()) is None:
            con.close()
            return

        selected_user_wallet, = d

        res = con.execute(
            "SELECT users.uname, users.agreement, assets.filepath, assets.token_id FROM users LEFT JOIN assets ON users.id = assets.owner_id")
        images = res.fetchall()

        for i, (user_name, user_agreement, asset_filepath, asset_token_id) in enumerate(images):

            if user_agreement is None:
                continue

            agreement = AssetAgreement(
                LOCAL_ENDPOINT, user_agreement, selected_user_wallet)

            price, assetHash, forSale, resaleAllowed = agreement.fetch_asset_metadata(
                asset_token_id)

            if selected_user_wallet != agreement.owner_of(asset_token_id):
                continue

            pil_img = Image.open(asset_filepath)

            pil_img = pil_img.resize((pil_img.width//4, pil_img.height//4))

            st.image(pil_img, "Original Owner: %s. Price (%f ETH). Resale: %r. For Sale: %r" % (
                user_name, Web3.from_wei(price, "ether"), resaleAllowed, forSale))

            sale_status = st.button(
                "Toggle Sale Status", disabled=not resaleAllowed, key=i)

            if sale_status:

                new_sale_status = not forSale
                market = AssetMarket(
                    LOCAL_ENDPOINT, self.market_address, selected_user_wallet)

                market.update_sale_status(
                    user_agreement, asset_token_id, new_sale_status)
                agreement = AssetAgreement(
                    LOCAL_ENDPOINT, user_agreement, selected_user_wallet)
                agreement.set_approval_for_all(self.market_address, True)

                with st.expander("Log"):
                    st.write("Updated For Sale status of Token %d to %r" %
                             (asset_token_id, new_sale_status))

        con.close()

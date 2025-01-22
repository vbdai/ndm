from upload import Upload
import streamlit as st
from PIL import Image
from contract import AssetMarket, AssetAgreement, get_web3_provider
from constants import LOCAL_ENDPOINT
from ssl_watermarking.main_multibit import Watermark
from tempfile import NamedTemporaryFile
from Crypto.Hash import SHA256
from web3 import Web3
from db import get_demo_db


class Market:

    def __init__(self, market_address: str) -> None:
        self.market_address = market_address
        self.manager_address = get_web3_provider(
            LOCAL_ENDPOINT).eth.accounts[0]

    def on_image_buy(self, agreement_address: str, token_id: int, buyer_id: int):

        con = get_demo_db()

        agreement = AssetAgreement(
            LOCAL_ENDPOINT, agreement_address, self.manager_address)

        asset_price = agreement.price_of(token_id)
        seller_address = agreement.owner_of(token_id)

        res = con.execute(
            "SELECT id FROM users WHERE wallet = ?", [seller_address])
        seller_id, = res.fetchone()

        wm_image = NamedTemporaryFile(
            "wb", suffix=".png", delete=False)

        img_hash = None
        img_hash_hex = None

        res = con.execute(
            "SELECT assets.filepath FROM users LEFT JOIN assets ON users.id = assets.owner_id WHERE users.agreement = ? AND assets.token_id = ?", [agreement_address, token_id])

        img_location, = res.fetchone()

        with open(img_location, "rb") as f:
            data = f.read()
            wm_image.write(data)
            cipher = SHA256.new(data)
            cipher.update(bytes([seller_id, buyer_id]))
            img_hash = cipher.digest()
            img_hash_hex = cipher.hexdigest()

        wm_file_name = wm_image.name
        wm_image.close()

        wm = Watermark()

        wm.set_watermark(seller_id, buyer_id)
        wm.watermark_image(wm_file_name)

        asset_market_manager = AssetMarket(
            LOCAL_ENDPOINT, self.market_address, self.manager_address)

        asset_market_manager.update_hash(
            agreement_address, token_id, img_hash)
        
        res = con.execute("SELECT wallet FROM users WHERE id = ?", [buyer_id])
        buyer_wallet_address, = res.fetchone()

        asset_market = AssetMarket(
            LOCAL_ENDPOINT, self.market_address, buyer_wallet_address)
        asset_market.purchase(
            agreement_address, token_id, asset_price)

        with st.expander("Log"):
            st.write("1. Asset Decryption with Market key")
            st.write("2. Finished watermarking file with watermark text: %d, %d" %
                     (seller_id, buyer_id))
            st.write("3. Computed Watermarked Image Hash: %s" % img_hash_hex)
            st.write("5. Added Asset Hash on Smart Contract to: %s" %
                     img_hash_hex)
            st.write("6. Transferred Asset from Owner account to Buyer account. Price: %f, Token ID: %d" % (
                asset_price, token_id))
            st.write(
                "7. Updated link on Smart Contract to point to encrypted asset")

        with open(wm_file_name, "rb") as f:
            st.download_button("Verify Signature and Download Asset",
                               f, file_name=wm_file_name)

        con.close()

    def render(self):
        st.write("## Trade")
        st.write(
            "Every owner's published asset appears on this page and buyers can buy whichever one they wish")

        con = get_demo_db()

        res = con.execute("SELECT uname FROM users")
        users = res.fetchall()

        buyer = st.selectbox("Buyer", map(
            lambda r: r[0], users))
        c1, c2 = st.columns(2)

        res = con.execute("SELECT id FROM users WHERE uname = ?", [buyer])

        if (d := res.fetchone()) is None:
            con.close()
            return

        buyer_id, = d

        res = con.execute(
            "SELECT * FROM users INNER JOIN assets ON users.id = assets.owner_id")

        data = res.fetchall()

        i = 0

        for (_, owner_name, owner_wallet, owner_agreement, _, _, asset_filepath, asset_token_id) in data:

            c = [c1, c2][i % 2]

            agreement = AssetAgreement(
                LOCAL_ENDPOINT, owner_agreement, owner_wallet)

            seller_address = agreement.owner_of(asset_token_id)

            res = con.execute(
                "SELECT uname FROM users WHERE wallet = ?", [seller_address])
            data = res.fetchone()

            seller_name, = data

            price, _, forSale, resaleAllowed = agreement.fetch_asset_metadata(
                asset_token_id)

            if not forSale:
                continue

            pil_img = Image.open(asset_filepath)

            pil_img = pil_img.resize((pil_img.width//4, pil_img.height//4))

            c.image(pil_img, "Original Owner: %s. Seller: %s. Price (%f ETH). Resale: %r" % (
                owner_name, seller_name, Web3.from_wei(price, "ether"), resaleAllowed))

            buy = c.button("Buy", key=asset_filepath)

            i += 1

            if buy:
                self.on_image_buy(owner_agreement, asset_token_id, buyer_id)

        con.close()

import streamlit as st
from tempfile import NamedTemporaryFile
from os.path import basename
from ssl_watermarking.main_multibit import Watermark
from Crypto.Hash import SHA256
from contract import AssetMarket
from constants import LOCAL_ENDPOINT
from db import get_demo_db


class ExtractWatermark:

    def __init__(self, market_address: str):

        self.market_address = market_address

    def render_extract_watermark(self):

        st.write("## Identifiability (Detectability): Asset Watermark Extraction")
        st.write("If a watermarked asset is leaked, we can extract the watermark text to find the owner and buyer ID which can then be mapped to their original identity")

        with st.form("extract-wm-form"):
            asset = st.file_uploader("Upload Watermarked Asset")

            upload = st.form_submit_button("Extract Watermark")

            if asset is None or not upload:
                return

            ext = basename(asset.name).split(".")[-1]

            f = NamedTemporaryFile("wb", suffix="." + ext, delete=False)
            f.write(asset.getvalue())
            f.close()
            wm = Watermark()
            try:
                oid, bid = wm.extract_watermark(f.name)
                pair = self.process_watermark(oid, bid)
                st.write("Extracted Watermark: Owner = %s, Buyer = %s " % pair)
            except:
                st.write(
                    "Watermark was corrupted: Owner ID = %d, Buyer ID = %d" % (oid, bid))

        with st.expander("Log"):
            st.write("1. Extract watermark from image")
            st.write("2. Match watermark IDs to Owner and Buyer datbase")

    def process_watermark(self, owner_id, buyer_id):

        con = get_demo_db()
        res = con.execute("SELECT a.uname, b.uname FROM users AS a INNER JOIN users AS b ON a.id = ? AND b.id = ?", [
                          owner_id, buyer_id])

        data = res.fetchone()
        con.close()

        return data

    def render_recovery(self):

        st.write("## Traceability: Asset Transaction Proof")
        st.write(
            """
        The proof of ownership and the history of ownership can be view on the 
        blockchain using tokenID and the owner ID. In case token ID is not 
        available, we can find the ownership records using the original asset 
        and the IDs.
        """)
        con = get_demo_db()
        with st.form("recovery"):

            res = con.execute("SELECT uname FROM users")

            users = list(map(lambda r: r[0], res.fetchall()))

            original_owner = st.selectbox("Original Owner", options=users)
            asset = st.file_uploader("Upload Original Asset")
            owner = st.selectbox("Seller", options=users)
            buyer = st.selectbox("Buyer", options=users)

            upload = st.form_submit_button("Upload")

            if asset is None or not upload:
                con.close()
                return

            res = con.execute("SELECT a.agreement, b.id, b.wallet, c.id FROM users AS a INNER JOIN users AS b INNER JOIN users as c ON a.uname = ? AND b.uname = ? AND c.uname = ?", [
                              original_owner, owner, buyer])

            owner_agreement, seller_id, seller_wallet, buyer_id = res.fetchone()

            cipher = SHA256.new(asset.getvalue())
            cipher.update(bytes([seller_id, buyer_id]))
            img_hash = cipher.digest()
            img_hash_hex = cipher.hexdigest()

            market = AssetMarket(
                LOCAL_ENDPOINT, self.market_address, seller_wallet)
            try:
                record = market.get_asset_sale_record(
                    owner_agreement, img_hash)
                st.write("Owner Address: %s, Buyer Address: %s, Token ID: %d" %
                        (seller_wallet, record[0], record[1]))
            except:
                st.write("Sale Record does not exist")


            with st.expander("Log"):
                st.write("1. Compute hash of image")
                st.write("2. Find sale record with hash: %s" %
                            (img_hash_hex))
        con.close()

    def render(self):
        self.render_extract_watermark()
        self.render_recovery()

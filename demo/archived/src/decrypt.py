from Crypto.Cipher import AES
from json import loads
from base64 import b64decode
from sys import argv
import streamlit as st
from tempfile import NamedTemporaryFile
from PIL import Image
from io import BytesIO
from glob import glob
from os.path import exists, basename


def decrypt_image(img_data: bytes, key: bytes, iv: bytes):

    cipher = AES.new(key, AES.MODE_CFB, iv=iv)

    return cipher.decrypt(img_data)


def main():
    st.write("# Buyer Decryption Tool")
    st.write("When a buyer receives their encrypted watermarked asset, they can use their AES symmetric key agreed upon earlier to decrypt the watermarked asset. In a production setting, this would happen completely on the buyer's local machine and does not involve the marketplace. For the purposes of this demo, we have a tool for your convenience.")

    key_files = glob("key_*.json")
    names = []

    for f in key_files:

        fname = basename(f)

        names.append(fname.split(".")[0].split("_")[1])

    st.write("**FOR DEMO PURPOSES ONLY** you may download the list of buyer keys currently stored on the server")
    selected_name = st.selectbox("Image Hash", options=names)

    if selected_name is not None:
        with open("key_%s.json" % selected_name, "r") as f:
            st.download_button("Download", f.read(),
                               file_name="key_%s.json" % selected_name)

    with st.form("decrypt"):
        img_file = st.file_uploader("Encrypted Asset")
        key_file = st.file_uploader("Key")

        submit = st.form_submit_button("Decrypt")

        if not submit:
            return

        if img_file is None or key_file is None:
            return

        key_data = loads(key_file.getvalue())

        key = b64decode(key_data["key"])
        iv = b64decode(key_data["iv"])

        data = decrypt_image(img_file.getvalue(), key, iv)

        img_file.close()
        key_file.close()

        download_file = NamedTemporaryFile("wb", delete=False)
        download_file.write(data)

    st.image(Image.open(BytesIO(data)))

    st.download_button("Download Decrypted Asset",
                       data, file_name=img_file.name)


if __name__ == "__main__":
    main()

import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json

load_dotenv()

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))

################################################################################
# Load_Contract Function
################################################################################


@st.cache_resource
def load_contract():

    # Load the contract ABI
    with open(Path('C:/Users/0xdaom/Desktop/contracts/compiled/artregistry_abi.json')) as f:
        contract_abi = json.load(f)

    # Set the contract address (this is the address of the deployed contract)
    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    # Get the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=contract_abi
    )

    return contract


# Load the contract
contract = load_contract()

################################################################################
# Helper functions to pin files and json to Pinata
################################################################################


def pin_artwork(artwork_name, artwork_file):
    # Pin the file to IPFS with Pinata
    ipfs_file_hash = pin_file_to_ipfs(artwork_file.getvalue())

    # Build a token metadata file for the artwork
    token_json = {
        "name": artwork_name,
        "image": ipfs_file_hash
    }
    json_data = convert_data_to_json(token_json)

    # Pin the json to IPFS with Pinata
    json_ipfs_hash = pin_json_to_ipfs(json_data)

    return json_ipfs_hash, token_json

st.title("Art Registry System")
st.write("Choose an account to get started")
accounts = w3.eth.accounts
address = st.selectbox("Select Account", options=accounts)
st.markdown("---")

################################################################################
# Register New Artwork
################################################################################
st.markdown("## Register New Artwork")
artwork_name = st.text_input("Enter the name of the artwork")
artist_name = st.text_input("Enter the artist name")


# Use the Streamlit `file_uploader` function create the list of digital image file types(jpg, jpeg, or png) that will be uploaded to Pinata.
file = st.file_uploader("Upload Artwork", type=["jpg", "jpeg", "png"])

if st.button("Register Artwork"):
    # Use the `pin_artwork` helper function to pin the file to IPFS
    artwork_ipfs_hash, token_json = pin_artwork(artwork_name, file)

    artwork_uri = f"ipfs://{artwork_ipfs_hash}"

    tx_hash = contract.functions.registerArtwork(
        address,
        artwork_name,
        artist_name,
        artwork_uri,
        token_json['image']
    ).transact({'from': address, 'gas': 1000000})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))
    st.write("You can view the pinned metadata file with the following IPFS Gateway Link")
    st.markdown(f"[Artwork IPFS Gateway Link](https://ipfs.io/ipfs/{artwork_ipfs_hash})")
    st.markdown(f"[Artwork IPFS Image Link](https://ipfs.io/ipfs/{token_json['image']})")

st.markdown("---")


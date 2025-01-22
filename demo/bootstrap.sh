#!/bin/bash

# compile smart contracts
npx hardhat compile

# remove any left over assets from watermarking
rm -rf src/ssl_watermarking/input/0/*
rm -rf src/ssl_watermarking/output/imgs/*
rm -rf images/*

# empty contents of contracts list
> contracts.json

if ! [ -f src/ssl_watermarking/normlayers/out2048_yfcc_orig.pth ]; then
    echo "Did not detect out2048_yfcc_orig.pth. Downloading fresh copy to src/ssl_watermarking/normlayers..."

    mkdir -p src/ssl_watermarking/normlayers
    wget --no-check-certificate https://dl.fbaipublicfiles.com/ssl_watermarking/out2048_yfcc_orig.pth -P src/ssl_watermarking/normlayers
fi

if ! [ -f src/ssl_watermarking/models/dino_r50_plus.pth ]; then
    echo "Did not detect dino_r50_plus.pth. Downloading fresh copy to src/ssl_watermarking/models..."
    mkdir -p src/ssl_watermarking/models
    wget --no-check-certificate https://dl.fbaipublicfiles.com/ssl_watermarking/dino_r50_plus.pth -P src/ssl_watermarking/models
fi

# remove the current database and create new one from schema
rm -f src/db/demo.db
sqlite3 src/db/demo.db < src/db/schema.sql

# seed the database with test data
sqlite3 src/db/demo.db < src/db/seed.sql

# start a eth node
npx hardhat node &

# replace this process with main app
exec streamlit run src/app.py
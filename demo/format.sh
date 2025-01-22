for f in $(find . -iname *.py -not -path "./src/ssl_watermarking*")
do
    echo "Formatting ${f}"
    autopep8 --in-place ${f}
done
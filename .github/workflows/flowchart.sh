echo "Starting transpilation."
cd src

FILES=$(find . -type f -name "*.py" | cut -c 3-)
echo $FILES

for FILE in $FILES; do
    if [ -f $FILE ]; then
        OUTPUT="docs/$(echo $FILE | tr "/." "_").html"
        echo "Transpiling ${FILE} to ${OUTPUT}."
        python3 -m pyflowchart $FILE -o $OUTPUT
    fi
done
#!/bin/bash
echo "Installing libraries to lib/ folder."
rm -rf lib/app
pip install -r requirements.txt -t lib
echo "Copying source folder to lib/ to make it available in lib path."
cp -rf ./app lib/app
echo "Invoking lambda function with args $1 lib location, $2 lambda function name, $3 lambda file location, $4 event json path."
python-lambda-local -l $1 -f $2 $3 $4
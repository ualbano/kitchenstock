#!/bin/bash

mkdir -p static/js

URL="https://unpkg.com/html5-qrcode@2.3.9/minified/html5-qrcode.min.js"

echo "Downloading html5-qrcode..."
curl -sSL $URL -o static/js/html5-qrcode.min.js

if [ $? -eq 0 ]; then
	echo "html5-qrcode successfully downloaded to static/js/html5-qrcode.min.js"
else
	echo "Download failed. Exiting."
	exit 1
fi

echo "Starting Flask app with uvicorn..."
uv run app.py --reload --host 0.0.0.0 --port 5000

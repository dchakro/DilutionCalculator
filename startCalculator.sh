#!/bin/bash

# A script to activate a venv, start the Dash app,
# and open it in Safari.

echo "--- Starting Dilution Calculator Dashboard ---"

# Check if the .env file exists and load it
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found. Please create one with VENV_PATH and APP_DIR."
    exit 1
fi

# 1. Activate the Python virtual environment
# 'eval echo' is used to correctly expand the '~' from the .env file
source $(eval echo $VENV_PATH)
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment from path: $VENV_PATH"
    exit 1
fi
echo "Virtual environment activated."

# 2. Change to the application's directory
cd "$(eval echo $APP_DIR)"
if [ $? -ne 0 ]; then
    echo "Error: Failed to change directory to: $APP_DIR"
    exit 1
fi
echo "Navigated to the project directory."

# 3. Start the Dash app in the background and redirect its output
echo "Launching the app..."
python3 -u DilutionCalc.py &> server.log &
SERVER_PID=$!

# 4. Wait a couple of seconds for the server to start up
sleep 3

# 5. Extract the URL from the log file and open it
URL=$(grep "Dash is running on" server.log | awk '{print $5}')

if [ -n "$URL" ]; then
    echo "Server started successfully. Found URL: $URL"
    # open -a "Google Chrome" "$URL"
     /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --app="$URL"
else
    echo "Could not find the server URL. Here's the log:"
    cat server.log
fi

# Clean up the log file
rm server.log

# 6. Bring the server process to the foreground
echo "Bringing server process to the foreground."
echo "Press Ctrl+C to shut down the server."
wait $SERVER_PID
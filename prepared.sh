# delete venv, create venv, activate venv, download requirements.txt

if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "You are currently in a virtual environment: $VIRTUAL_ENV. Deleting $VIRTUAL_ENV ..."
    rm -rf "$VIRTUAL_ENV"
fi

VENV_NAME="venv"

echo "Creating new virtual environment..."
python3 -m venv "$VENV_NAME"

echo "Activating new virtual environment..."
source "$VENV_NAME/bin/activate"

if [ -f "requirements.txt" ]; then
    echo "Downloading dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt file not found. Please ensure it is in the current directory."
fi

echo "Setup complete."

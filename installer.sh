#!/bin/bash

# Function to check if Python is installed and install Python 3.11 if not
install_python() {
    if ! command -v python3.11 &> /dev/null
    then
        echo "Python 3.11 is not installed. Installing..."
        sudo apt update
        sudo apt install -y python3.11 python3.11-venv python3.11-dev
        sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
        sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1
    else
        echo "Python 3.11 is already installed."
    fi
}

install_python

if ! command -v pip &> /dev/null
then
    echo "pip is not installed. Installing..."
    python -m ensurepip --upgrade
fi

echo "Running the Python installer script..."


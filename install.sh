#!/bin/bash

# install.sh - Installation script for Ardra Tool

# Function to install Go
install_go() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get install -y golang-go
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install go
    else
        echo "Unsupported OS. Please install Go manually."
        exit 1
    fi
}

# Function to install httprobe
install_httprobe() {
    go install github.com/tomnomnom/httprobe@latest
    echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.bash_profile
    source ~/.bash_profile
}

# Function to install findomain
install_findomain() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        wget https://github.com/Edu4rdSHL/findomain/releases/latest/download/findomain-linux -O findomain
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        wget https://github.com/Edu4rdSHL/findomain/releases/latest/download/findomain-macos -O findomain
    else
        echo "Unsupported OS. Please install findomain manually."
        exit 1
    fi
    chmod +x findomain
    sudo mv findomain /usr/local/bin/
}

# Function to install subfinder
install_subfinder() {
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.bash_profile
    source ~/.bash_profile
}

# Function to install Python dependencies
install_python_dependencies() {
    if ! command -v pip3 &> /dev/null; then
        echo "pip3 not found. Installing pip3..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get install -y python3-pip
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install python3
        else
            echo "Unsupported OS. Please install pip3 manually."
            exit 1
        fi
    fi

    pip3 install -r requirements.txt
}

# Function to clone Ardra repository (Assuming it's hosted on GitHub)
clone_ardra() {
    if [ -d "Ardra" ]; then
        echo "Ardra directory already exists. Skipping clone."
    else
        git clone https://github.com/yourusername/ardra.git
        cd ardra || exit
    fi
}

# Update package lists for Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get update
elif [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew update
fi

# Install Go if not installed
if ! command -v go &> /dev/null; then
    echo "Go not found. Installing Go..."
    install_go
else
    echo "Go is already installed."
fi

# Install httprobe if not installed
if ! command -v httprobe &> /dev/null; then
    echo "Installing httprobe..."
    install_httprobe
else
    echo "httprobe is already installed."
fi

# Install findomain if not installed
if ! command -v findomain &> /dev/null; then
    echo "Installing findomain..."
    install_findomain
else
    echo "findomain is already installed."
fi

# Install subfinder if not installed
if ! command -v subfinder &> /dev/null; then
    echo "Installing subfinder..."
    install_subfinder
else
    echo "subfinder is already installed."
fi

# Clone Ardra repository
clone_ardra

# Install Python dependencies
echo "Installing Python dependencies..."
install_python_dependencies

echo "All required tools are installed and ready to use."


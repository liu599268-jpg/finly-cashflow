#!/bin/bash

echo "========================================"
echo "  GitHub CLI Installation Script"
echo "========================================"
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "📦 Homebrew not found. Installing Homebrew first..."
    echo ""
    echo "This will require your administrator password."
    echo ""

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Homebrew installed successfully!"
        echo ""

        # Add Homebrew to PATH (for Apple Silicon Macs)
        if [ -f "/opt/homebrew/bin/brew" ]; then
            echo "Adding Homebrew to PATH..."
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    else
        echo ""
        echo "❌ Homebrew installation failed."
        echo "Please install manually from: https://brew.sh"
        exit 1
    fi
else
    echo "✅ Homebrew is already installed"
    echo ""
fi

# Install GitHub CLI
echo "📦 Installing GitHub CLI..."
echo ""

brew install gh

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "  ✅ GitHub CLI installed successfully!"
    echo "========================================"
    echo ""

    # Verify installation
    gh --version
    echo ""

    echo "Next steps:"
    echo "  1. Authenticate with GitHub:"
    echo "     gh auth login"
    echo ""
    echo "  2. Follow the prompts to login"
    echo ""
    echo "  3. Then you can use gh commands like:"
    echo "     gh repo view"
    echo "     gh issue list"
    echo "     gh pr list"
    echo ""
else
    echo ""
    echo "❌ GitHub CLI installation failed."
    echo "Please try manually:"
    echo "  brew install gh"
    exit 1
fi

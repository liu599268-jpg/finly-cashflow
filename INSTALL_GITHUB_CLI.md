# Installing GitHub CLI (gh)

GitHub CLI is a powerful command-line tool that lets you interact with GitHub directly from your terminal.

---

## 🚀 Quick Installation (Recommended)

### Option 1: Run the Automated Script

I've created an installation script for you:

```bash
cd /Users/lhr/Desktop/Finly-prototype
bash install_github_cli.sh
```

This script will:
1. Check if Homebrew is installed
2. Install Homebrew if needed
3. Install GitHub CLI
4. Verify the installation

**Note:** You'll need to enter your Mac password when prompted.

---

## 📦 Manual Installation Methods

### Option 2: Install via Homebrew (Recommended)

**Step 1: Install Homebrew** (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation, if you're on Apple Silicon (M1/M2/M3 Mac):
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**Step 2: Install GitHub CLI**

```bash
brew install gh
```

**Step 3: Verify Installation**

```bash
gh --version
```

You should see something like: `gh version 2.x.x`

---

### Option 3: Download Installer Package

If you prefer not to use Homebrew:

1. **Download the installer:**
   - Go to: https://github.com/cli/cli/releases/latest
   - Download the `.pkg` file for macOS
   - Example: `gh_2.x.x_macOS_amd64.pkg` (Intel) or `gh_2.x.x_macOS_arm64.pkg` (Apple Silicon)

2. **Run the installer:**
   - Double-click the downloaded `.pkg` file
   - Follow the installation wizard
   - Enter your password when prompted

3. **Verify installation:**
   ```bash
   gh --version
   ```

---

### Option 4: Install via MacPorts

If you use MacPorts instead of Homebrew:

```bash
sudo port install gh
```

---

## 🔐 Authenticate with GitHub

After installation, authenticate with your GitHub account:

```bash
gh auth login
```

**Follow the prompts:**

1. **What account do you want to log into?**
   - Select: `GitHub.com`

2. **What is your preferred protocol for Git operations?**
   - Select: `HTTPS` (recommended)

3. **Authenticate Git with your GitHub credentials?**
   - Select: `Yes`

4. **How would you like to authenticate?**
   - Select: `Login with a web browser` (easiest)
   - Or: `Paste an authentication token`

5. **Copy the one-time code** shown and press Enter
   - Your browser will open
   - Log in to GitHub if needed
   - Paste the code when prompted
   - Authorize GitHub CLI

**Success!** You'll see: `✓ Logged in as liu599268-jpg`

---

## ✅ Verify Authentication

Check if you're logged in:

```bash
gh auth status
```

You should see:
```
github.com
  ✓ Logged in to github.com as liu599268-jpg
  ✓ Git operations for github.com configured to use https protocol.
  ✓ Token: *******************
```

---

## 🎯 Useful GitHub CLI Commands

Once installed and authenticated, you can use:

### Repository Commands
```bash
# View your Finly repository
gh repo view liu599268-jpg/finly-cashflow

# Create a new repository (alternative to web interface)
gh repo create finly-cashflow --public --description "Cash flow forecasting"

# Clone a repository
gh repo clone liu599268-jpg/finly-cashflow

# List your repositories
gh repo list
```

### Issue Commands
```bash
# List issues
gh issue list

# Create an issue
gh issue create --title "Bug: Something broke" --body "Description here"

# View an issue
gh issue view 1
```

### Pull Request Commands
```bash
# Create a pull request
gh pr create --title "New feature" --body "Description"

# List pull requests
gh pr list

# View a pull request
gh pr view 1

# Merge a pull request
gh pr merge 1
```

### Workflow Commands
```bash
# View GitHub Actions workflows
gh workflow list

# Run a workflow
gh workflow run workflow-name

# View workflow runs
gh run list
```

---

## 🔧 Troubleshooting

### "command not found: brew"

Homebrew is not installed. Install it first:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### "command not found: gh" (after Homebrew installation)

On Apple Silicon Macs, add Homebrew to your PATH:
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
source ~/.zprofile
```

On Intel Macs:
```bash
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
source ~/.zprofile
```

### "Permission denied"

You need administrator access. Run with `sudo`:
```bash
sudo brew install gh
```

### Authentication fails

Try re-authenticating:
```bash
gh auth logout
gh auth login
```

---

## 📚 Alternative: Use Git + GitHub Web

If you prefer not to install GitHub CLI, you can still use Git with GitHub:

**Push code:**
```bash
git push -u origin main
```

**Manage repository:**
- Use GitHub website: https://github.com/liu599268-jpg/finly-cashflow

**Benefits of GitHub CLI:**
- Faster workflow
- No switching to browser
- Script automation
- Better CI/CD integration

---

## 🎓 Learning Resources

**Official Documentation:**
- GitHub CLI Manual: https://cli.github.com/manual/
- Installation Guide: https://github.com/cli/cli#installation

**Quick Start:**
```bash
# Get help
gh --help

# Get help for specific command
gh repo --help

# Interactive tutorial
gh help
```

---

## ✨ Quick Reference

After installation, here's what you can do:

```bash
# Check version
gh --version

# Login
gh auth login

# Check login status
gh auth status

# View repository
gh repo view

# Create repository
gh repo create

# Clone repository
gh repo clone owner/repo

# List repositories
gh repo list

# Create issue
gh issue create

# Create pull request
gh pr create
```

---

## 🚀 Next Steps After Installation

1. **Install GitHub CLI:**
   ```bash
   bash install_github_cli.sh
   ```

2. **Authenticate:**
   ```bash
   gh auth login
   ```

3. **Use with your Finly project:**
   ```bash
   cd /Users/lhr/Desktop/Finly-prototype
   gh repo view
   ```

4. **Optional: Create repository via CLI:**
   ```bash
   gh repo create finly-cashflow --public --source=. --push
   ```

---

**Ready to install? Run:**
```bash
cd /Users/lhr/Desktop/Finly-prototype
bash install_github_cli.sh
```

Or install Homebrew + GitHub CLI manually following Option 2 above.

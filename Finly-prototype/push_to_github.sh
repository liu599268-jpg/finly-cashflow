#!/bin/bash

echo "========================================"
echo "  Pushing Finly to GitHub"
echo "========================================"
echo ""
echo "Repository: https://github.com/liu599268-jpg/finly-cashflow"
echo ""
echo "Pushing code to GitHub..."
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "  ✅ Successfully pushed to GitHub!"
    echo "========================================"
    echo ""
    echo "Your repository is now live at:"
    echo "https://github.com/liu599268-jpg/finly-cashflow"
    echo ""
    echo "Next steps:"
    echo "  1. Visit your repository"
    echo "  2. Add topics: cash-flow-forecasting, quickbooks, machine-learning, etc."
    echo "  3. Star your repository ⭐"
    echo ""
else
    echo ""
    echo "========================================"
    echo "  ❌ Push failed"
    echo "========================================"
    echo ""
    echo "Make sure you've created the repository first:"
    echo "  1. Go to: https://github.com/new"
    echo "  2. Repository name: finly-cashflow"
    echo "  3. Make it public (or private)"
    echo "  4. DO NOT initialize with README"
    echo "  5. Click 'Create repository'"
    echo ""
    echo "Then run this script again:"
    echo "  bash push_to_github.sh"
    echo ""
fi

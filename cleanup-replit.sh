#!/bin/bash

# Script to clean up Replit-specific files and directories
# Run this after verifying the standalone setup works

echo "======================================"
echo "Replit Cleanup Script"
echo "======================================"
echo ""
echo "This script will remove Replit-specific files and directories."
echo "Make sure you've verified the standalone setup works first!"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo "Starting cleanup..."

# Remove ReplitCore directory
if [ -d "ReplitCore" ]; then
    echo "Removing ReplitCore directory..."
    rm -rf ReplitCore
    echo "✓ ReplitCore removed"
fi

# Remove .replit file if exists at root
if [ -f ".replit" ]; then
    echo "Removing .replit file..."
    rm .replit
    echo "✓ .replit removed"
fi

# Remove replit.nix if exists
if [ -f "replit.nix" ]; then
    echo "Removing replit.nix file..."
    rm replit.nix
    echo "✓ replit.nix removed"
fi

# Remove .config directory if exists
if [ -d ".config" ]; then
    echo "Removing .config directory..."
    rm -rf .config
    echo "✓ .config removed"
fi

# Remove uv.lock if exists (Replit package manager)
if [ -f "uv.lock" ]; then
    echo "Removing uv.lock..."
    rm uv.lock
    echo "✓ uv.lock removed"
fi

# Remove replit.md if exists
if [ -f "replit.md" ]; then
    echo "Removing replit.md..."
    rm replit.md
    echo "✓ replit.md removed"
fi

# Remove old package.json backup
if [ -f "package.json.frontend-backup" ]; then
    echo "Removing package.json.frontend-backup..."
    rm package.json.frontend-backup
    echo "✓ Backup removed"
fi

# Remove pyproject.toml (Replit-specific)
if [ -f "pyproject.toml" ]; then
    echo "Removing pyproject.toml..."
    rm pyproject.toml
    echo "✓ pyproject.toml removed"
fi

# Remove GunPowder-Splash.zip if exists
if [ -f "GunPowder-Splash.zip" ]; then
    echo "Removing GunPowder-Splash.zip..."
    rm GunPowder-Splash.zip
    echo "✓ Archive removed"
fi

# Remove attached_assets if exists
if [ -d "attached_assets" ]; then
    echo "Removing attached_assets directory..."
    rm -rf attached_assets
    echo "✓ attached_assets removed"
fi

echo ""
echo "======================================"
echo "Cleanup Complete!"
echo "======================================"
echo ""
echo "Removed Replit-specific files and directories."
echo "Your standalone repository is now clean."
echo ""
echo "You can now initialize a git repository:"
echo "  git init"
echo "  git add ."
echo "  git commit -m 'Initial commit: Gunpowder Splash standalone'"
echo ""


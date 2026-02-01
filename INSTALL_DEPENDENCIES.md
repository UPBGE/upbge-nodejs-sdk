# SDK Dependencies Installation

This document explains how to install Node.js for the SDK (when not using the pre-packaged bundle).

## Prerequisites

- Internet access to download binaries
- Tools to extract archives (7-Zip, tar, etc.)

## Option 1: Manual installation

### Install Node.js

#### Windows
1. Download Node.js LTS (v20.x or v22.x) from https://nodejs.org/
2. Download the "Windows Binary (.zip)" build for x64
3. Extract the ZIP file
4. Copy `node.exe` to `runtime/windows/node.exe`

#### Linux
1. Download Node.js LTS from https://nodejs.org/
2. Download the "Linux Binary (x64)" build (.tar.xz)
3. Extract: `tar -xf node-v*.tar.xz`
4. Copy the `node` binary to `runtime/linux/node-linux64`
5. Make it executable: `chmod +x runtime/linux/node-linux64`

#### macOS
1. Download Node.js LTS from https://nodejs.org/
2. Download the "macOS Binary (x64)" build (.tar.gz)
3. Extract: `tar -xzf node-v*.tar.gz`
4. Copy the `node` binary to `runtime/macos/node-osx`
5. Make it executable: `chmod +x runtime/macos/node-osx`

## Option 2: Download script

Use the SDK script to download Node.js:

```bash
python scripts/download_dependencies.py
```

## Verification

After installing, confirm the file exists:

- `runtime/windows/node.exe` (Windows)
- `runtime/linux/node-linux64` (Linux)
- `runtime/macos/node-osx` (macOS)

## Notes

- Use Node.js LTS versions for stability
- Binaries must be executable (Linux/macOS)

# Scripts Directory

This directory contains automation and verification scripts for the DevSecOps pipeline.

## Quick Start Scripts
- `quick-start.ps1` - Windows PowerShell setup script
- `quick-start.sh` - Linux/Mac bash setup script

## Verification Scripts
- `verify-pipeline-fixed.py` - Main pipeline verification script
- `verify-pipeline.py` - Original verification script

## Utility Scripts
- `*.bat` - Windows batch files for various tasks
- `*fixed*` - Updated/fixed versions of scripts

## Usage

```bash
# Run pipeline verification
python verify-pipeline-fixed.py

# Quick setup (Windows)
.\quick-start.ps1

# Quick setup (Linux/Mac)
chmod +x quick-start.sh && ./quick-start.sh
```

#!/bin/bash
echo "Starting DexterOptiClean..."

# Check if running as root/admin
if [ "$EUID" -eq 0 ]; then
    echo "Running with administrator privileges."
else
    echo "Standard user privileges detected."
fi

# Start the application
python app.py "$@"
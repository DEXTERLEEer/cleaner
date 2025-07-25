#!/bin/bash

echo "Installing DexterOptiClean dependencies..."
pip install flask>=3.1.1 psutil>=7.0.0

echo "Setup complete! To run the application:"
echo "1. Navigate to the DexterOptiClean directory:"
echo "   cd DexterOptiClean"
echo "2. Run the application:"
echo "   python app.py"
echo "3. Open your web browser and go to: http://localhost:7000"
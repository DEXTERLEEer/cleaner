# DexterOptiClean - PC Cleaner Application

## Overview
DexterOptiClean is a PC cleaning and optimization application built with Flask. It provides a web interface for cleaning temporary files, browser caches, and other system junk files to free up disk space and potentially improve system performance.

## Recent Improvements
1. **Fixed Cross-Platform Compatibility**: The application now works properly on both Windows and Linux systems
2. **Simplified User Experience**: Replaced the "Scan System" button with a "Clean All" button that performs cleaning in one step
3. **Improved Error Handling**: Better error handling and user feedback throughout the application

## Features
- System cleaning (temporary files, browser cache, system logs)
- System monitoring (CPU, memory, disk usage)
- Duplicate file detection
- Administrative operations for system-level cleaning
- Detailed cleaning logs

## How to Run the Application

### Prerequisites
- Python 3.11+
- Flask 3.1.1+
- psutil 7.0.0+

### Installation
1. Clone the repository:
   ```
   git clone https://github.com/DEXTERLEEer/cleaner.git
   ```

2. Install dependencies:
   ```
   pip install flask>=3.1.1 psutil>=7.0.0
   ```

3. Navigate to the application directory:
   ```
   cd cleaner/DexterOptiClean
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Access the web interface at `http://localhost:7000`

## Usage
1. Open the application in your web browser
2. View system statistics on the dashboard
3. Click the "Clean All" button to clean all temporary files, browser caches, and system logs
4. Alternatively, use the category-specific cleaning options for more targeted cleaning
5. View the cleaning results and freed space

## Technical Details
- **Backend**: Python with Flask web framework
- **System Interaction**: psutil library for system monitoring
- **Frontend**: HTML/CSS/JavaScript

## Notes
- The application requires appropriate permissions to clean certain system files
- Administrative privileges may be required for some operations
- The application is designed to work on both Windows and Linux systems
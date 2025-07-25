# DEXTER PC Optimizer

## Overview

DEXTER PC Optimizer is a comprehensive system cleaning and optimization tool built with Flask and vanilla JavaScript. The application provides a desktop-like experience in the browser with capabilities for system monitoring, file cleaning, duplicate detection, and administrative privilege management. It features a modern dark-themed UI with purple accents and supports both Windows and Unix-like operating systems.

## User Preferences

Preferred communication style: Simple, everyday language.
User requirement: Focus on actual PC cleaning functionality, not simulation - clean real files and clear actual system data.

## System Architecture

### Frontend Architecture
- **Technology**: Vanilla JavaScript with Bootstrap 5 for UI components
- **Design Pattern**: Single Page Application (SPA) with tab-based navigation
- **Styling**: CSS3 with custom variables for theming, dark mode interface
- **User Experience**: Desktop-like interface with custom title bar, splash screen, and window controls
- **State Management**: Client-side state management through JavaScript classes

### Backend Architecture
- **Framework**: Flask (Python) with RESTful API design
- **Pattern**: Modular architecture with separated concerns
- **Core Modules**:
  - `PCCleaner`: File cleaning and categorization
  - `SystemMonitor`: Real-time system statistics
  - `AdminUtils`: Privilege elevation management
  - `DuplicateFinder`: File deduplication based on content hashing

## Key Components

### Core Modules

1. **PCCleaner** (`core/cleaner.py`)
   - Handles temporary file cleanup
   - Browser cache management
   - System log cleanup
   - Categorized file scanning with progress callbacks

2. **SystemMonitor** (`core/system_monitor.py`)
   - Real-time CPU, memory, and disk usage monitoring
   - Cross-platform system statistics
   - Temperature monitoring (where available)
   - System uptime and load average tracking

3. **AdminUtils** (`core/admin_utils.py`)
   - Cross-platform privilege checking
   - Administrative elevation requests
   - UAC integration for Windows
   - Sudo integration for Unix systems

4. **DuplicateFinder** (`core/duplicate_finder.py`)
   - Content-based duplicate detection using SHA-256 hashing
   - Size-based pre-filtering for performance
   - Support for multiple file types (images, videos, documents, etc.)
   - Efficient two-pass scanning algorithm

### Frontend Components

1. **Main Application Interface**
   - Tab-based navigation system
   - Real-time system status display
   - Progress tracking for scan operations
   - File selection and management interface

2. **Responsive Design**
   - Bootstrap-based responsive layout
   - Custom CSS with CSS variables for theming
   - Font Awesome icons for visual elements
   - Smooth transitions and animations

## Data Flow

1. **System Monitoring Flow**:
   - Backend continuously monitors system resources
   - Frontend polls `/api/system-status` endpoint
   - Real-time updates displayed in dashboard

2. **File Scanning Flow**:
   - User initiates scan via frontend
   - Backend performs categorized file scanning
   - Progress updates sent to frontend via polling
   - Results displayed in selectable file list

3. **Cleaning Flow**:
   - User selects files for cleaning
   - Frontend sends selected files to backend
   - Backend performs safe file removal
   - Confirmation and results returned to frontend

4. **Duplicate Detection Flow**:
   - User specifies directory for scanning
   - Backend performs two-pass duplicate detection
   - Results grouped by hash and presented to user
   - User selects duplicates for removal

## External Dependencies

### Python Dependencies
- **Flask**: Web framework for backend API
- **Cross-platform modules**: `os`, `platform`, `subprocess` for system interactions
- **Security**: Built-in security features, configurable secret key

### Frontend Dependencies
- **Bootstrap 5**: UI framework for responsive design
- **Font Awesome 6**: Icon library for visual elements
- **No heavy JavaScript frameworks**: Vanilla JS for lightweight performance

### System Dependencies
- **Platform-specific APIs**: Windows UAC, Unix sudo for privilege elevation
- **System utilities**: Platform-specific commands for system monitoring
- **File system access**: Direct file system operations for cleaning and scanning

## Deployment Strategy

### Development Environment
- Flask development server for local testing
- Static file serving through Flask
- Environment variable configuration for secrets

### Production Considerations
- **Security**: Admin privilege management with proper UAC/sudo integration
- **Performance**: Efficient file scanning with progress callbacks
- **Cross-platform**: Support for Windows and Unix-like systems
- **Error Handling**: Comprehensive exception handling throughout application

### Configuration
- Environment-based secret key management
- Configurable scan directories and file types
- Adjustable system monitoring intervals
- Platform-specific optimization paths

The application is designed to be self-contained with minimal external dependencies, focusing on core system optimization functionality while maintaining a professional desktop application appearance and feel within a web browser environment.
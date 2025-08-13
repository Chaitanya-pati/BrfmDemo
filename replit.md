# Wheat Processing Management System

## Overview

This is a comprehensive Flask-based web application designed to manage the complete wheat processing workflow from vehicle entry to final product dispatch. The system handles supplier management, inventory tracking, quality control, production planning, and sales dispatch operations for a wheat processing facility.

The application manages the entire wheat processing pipeline: vehicles arriving with wheat from suppliers, quality testing and categorization, weight measurement, storage in godowns, pre-cleaning processes, production planning and execution, and final product dispatch to customers.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web application with SQLAlchemy ORM for database operations
- **Database**: SQLite for development with PostgreSQL support via environment configuration
- **File Handling**: Local file system storage with configurable upload directory and 16MB size limits
- **Scheduling**: APScheduler for background tasks and cleaning reminders
- **Session Management**: Flask sessions with configurable secret keys

### Frontend Architecture
- **UI Framework**: Bootstrap 5 with dark theme for consistent styling
- **JavaScript**: Vanilla JavaScript with Bootstrap components for interactivity
- **Templates**: Jinja2 templating engine with modular template inheritance
- **File Uploads**: Multi-format support (images, PDFs, documents) with preview functionality

### Data Storage Design
- **Supplier Management**: Master data for suppliers with contact information and vehicle relationships
- **Inventory System**: Multi-level storage hierarchy with godowns (categorized by type: mill, low mill, hd) and pre-cleaning bins with capacity tracking
- **Production Workflow**: Order management system with planning stages, job tracking, and percentage-based material allocation
- **Quality Control**: Sample testing with categorization and approval workflows
- **Equipment Maintenance**: Cleaning schedules for processing machines with photo documentation requirements

### Authentication & Authorization
- Basic session-based authentication using Flask sessions
- No complex user management system implemented - designed for internal facility use
- File access protection through controlled upload/download endpoints

### Processing Workflow Management
- **Vehicle Processing**: Sequential workflow from entry → quality check → weight measurement → unloading
- **Inventory Tracking**: Real-time stock levels across godowns and pre-cleaning bins with capacity utilization
- **Production Planning**: Multi-stage planning system with percentage-based material sourcing from different bins
- **Quality Assurance**: Sample-based testing with category assignment and approval gates
- **Equipment Monitoring**: Time-based cleaning schedules with reminder notifications and photo documentation

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web application framework with SQLAlchemy extension for ORM
- **APScheduler**: Background task scheduling for cleaning reminders and maintenance alerts
- **Werkzeug**: WSGI utilities including secure filename handling and proxy fix middleware

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme variant served via CDN
- **Font Awesome 6**: Icon library for consistent UI iconography
- **Bootstrap JavaScript**: Interactive components (tabs, tooltips, modals, forms)

### File Processing
- **Local File System**: Upload directory management with automatic directory creation
- **File Type Validation**: Support for images (PNG, JPG, JPEG, GIF), documents (PDF, DOC, DOCX)
- **Secure File Handling**: Werkzeug secure filename processing for uploaded files

### Database Support
- **SQLite**: Default development database with automatic file creation
- **PostgreSQL**: Production-ready database support via DATABASE_URL environment variable
- **Connection Pooling**: Configured with pool recycling and pre-ping for reliability

### Development Tools
- **Debug Mode**: Flask debug mode for development with hot reloading
- **Logging**: Python logging configuration for debugging and monitoring
- **Static File Serving**: Flask static file handling for CSS, JavaScript, and uploaded files
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-01-09

### Added

- Email verification system for user registration
- Verification token model and database table
- SMTP email service integration
- Environment variables for SMTP configuration
- User verification status tracking
- New endpoint for email verification

### Changed

- Renamed project from fastapi-todo-app to fastapi-auth
- Updated project structure documentation
- Enhanced user registration workflow to include email verification
- Modified User model to include verification status

### Removed

- Todo-related functionality
- Unnecessary database schema checks

## [0.3.0] - 2024-12-17

### Added

- Next.js 15.1.0 and next-auth v5 integration support
- Comprehensive Git workflow guidelines
- Frontend integration documentation
- JWT token rotation mechanism
- Enhanced security measures for authentication

### Changed

- Updated project documentation structure
- Enhanced API endpoint documentation
- Improved error handling for authentication flows
- Standardized commit message format

### Security

- Implemented secure token rotation
- Enhanced password hashing configuration
- Added additional security headers

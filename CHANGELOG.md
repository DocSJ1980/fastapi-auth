# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-12-09

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

## [0.2.1] - 2024-12-17

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

## [0.2.4] - 2024-12-17

### Added
- Password reset endpoint with token verification
- Custom timezone-aware datetime handling for tokens
- New endpoint `/user/reset-password` for password reset
- ResetPasswordRequest schema for password reset validation

### Changed
- Updated forgot password email template with new frontend URL
- Enhanced token handling with proper timezone support
- Improved password reset workflow security
- Added automatic cleanup of expired reset tokens

### Security
- Implemented timezone-aware token expiration
- Added automatic cleanup of existing tokens on new request
- Enhanced password reset token validation

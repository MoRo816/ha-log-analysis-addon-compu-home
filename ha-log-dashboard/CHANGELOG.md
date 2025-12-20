# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-12-20

### Changed
- **BREAKING**: Switched from reading log files to using systemd journal
- Log retrieval now uses `journalctl` to read Home Assistant logs from systemd journal
- Updated API endpoints to support journal-based log reading with filtering

### Added
- New `JournalReader` class for interfacing with systemd journal
- Support for time-based log filtering (`since` and `until` parameters)
- Journal access permissions in AppArmor profile
- systemd package added to Docker container
- Improved error handling for journal access failures

### Fixed
- Log reading functionality now works with systems where log files are no longer available

## [1.0.0] - 2025-12-20

### Added
- Initial release of Log Analysis Dashboard add-on
- Web-based dashboard for viewing and managing issues
- Filtering by integration, status, severity, and date range
- Issue detail view with full context and recommendations
- Issue management (status updates, notes, resolution tracking)
- REST API for programmatic access
- Data persistence across restarts
- Responsive design for mobile and desktop
- Export functionality (CSV, JSON)
- Home Assistant integration with API access
- Multi-architecture support (amd64, armv7, arm64)
- Comprehensive documentation and troubleshooting guide

### Features
- 📊 Visual dashboard with statistics
- 🔍 Advanced filtering and search
- 📝 Notes and metadata management
- 🔗 Integration tracking
- 📈 Issue trend analysis
- 📱 Responsive web interface
- 🔐 AppArmor security profile
- 🐳 Docker containerization
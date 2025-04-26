# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 26.04.2025
### Added
- Extended error logging with full stack traces using `traceback.format_exc()` for better debugging.
- Improved exception handling during the parsing process to ensure more reliable execution.
- Enhanced user interface updates with progress bar and status messages during parsing.

### Fixed
- Improved stability of page parsing with better error recovery and retry mechanism.
- Refined handling of AJAX requests and page loading to reduce errors.


## [1.0.1] - 15.04.2025
### Added
- CHANGELOG.md for recording project changes
- Opportunity for changing theme in app

### Changed
- The method of saving and changing settings has been changed
- Content in README file

### Fixed
- Saving settings are now correct and when restarted will be the same as before closure


## [1.0.0] - 11.04.2025
### Added
- Initial release of `Jobs_Parsing` project.
- Core functionality for parsing job listings.
- Core functionality for user GUI
- Basic error handling and logging.


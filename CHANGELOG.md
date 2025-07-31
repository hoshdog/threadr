# Changelog

All notable changes to the Threadr project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-07-31

### Added
- Complete web scraping functionality for allowed domains
- Comprehensive error handling with user-friendly messages
- Debug endpoints for troubleshooting (removed in production)
- Complete deployment documentation
- API endpoints reference documentation
- Deployment troubleshooting guide
- PYTHONPATH configuration for src/ directory structure

### Changed
- Reorganized project structure with proper folder hierarchy
- Moved backend source files to `backend/src/` directory
- Moved frontend source files to `frontend/src/` directory
- Consolidated documentation into `docs/` folder
- Updated all import statements to handle new structure
- Simplified httpx configuration for Railway compatibility
- Updated Vercel configuration for new frontend structure

### Fixed
- Railway deployment 502 errors
- Pydantic v2 HttpUrl isinstance type error
- CORS configuration issues (removed trailing slashes)
- Import errors with new directory structure
- Web scraping failures on Railway
- Health check timeouts
- SSL/TLS configuration issues in containers

### Removed
- Debug endpoints from production code
- Temporary debug scripts and files
- Complex SSL context configuration
- Redundant documentation files

## [0.9.0] - 2025-07-30

### Added
- FastAPI backend with thread generation
- Rate limiting with Redis
- OpenAI GPT-3.5-turbo integration
- Basic web scraping with BeautifulSoup
- Health check endpoints
- CORS middleware

### Fixed
- Railway health check failures
- OpenAI API key startup dependency
- Gunicorn to Uvicorn migration

## [0.1.0] - 2025-07-29

### Added
- Initial project setup
- Basic project structure
- MVP specification
- Technology stack decisions
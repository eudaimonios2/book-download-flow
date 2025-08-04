# Overview

Free PDF Book Finder is a web application that searches for free PDF download links across multiple sources including OceanOfPDF, Library Genesis, and Internet Archive. The application features a simple interface where users can input multiple book titles and authors, then receive real-time search results with direct download links from various sources.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Technology**: Vanilla HTML, CSS, and JavaScript with Bootstrap for styling
- **Design Pattern**: Single-page application with client-side form handling
- **UI Components**: 
  - Textarea input for batch book entry in "Title – Author" format
  - Real-time results table showing title, author, source, and download links
  - Loading states and error handling with user-friendly messages
- **Styling**: Dark theme with gradient backgrounds and responsive design using Bootstrap

## Backend Architecture
- **Framework**: Flask web framework with Python
- **API Design**: RESTful endpoint structure with JSON request/response format
- **Concurrency**: Parallel processing using ThreadPoolExecutor for simultaneous searches across multiple sources
- **Error Handling**: Graceful error handling with timeout management and detailed error messages

## Search Engine Architecture
- **Multi-Source Strategy**: Simultaneous searches across three different book sources
- **Web Scraping**: BeautifulSoup for HTML parsing with realistic browser headers
- **Request Management**: Session-based HTTP requests with proper user-agent strings
- **Parallel Processing**: Each book search spawns multiple concurrent threads for different sources

## Data Flow
- **Input Processing**: Client-side parsing of multi-line book input with validation
- **Search Coordination**: Backend distributes search tasks across worker threads
- **Result Aggregation**: Real-time collection and formatting of search results
- **Response Format**: Structured JSON with title, author, source, and download link fields

# External Dependencies

## Python Libraries
- **Flask**: Web framework for API endpoints and static file serving
- **Flask-CORS**: Cross-origin resource sharing support
- **requests**: HTTP client for web scraping and API calls
- **BeautifulSoup4**: HTML parsing for web scraping
- **concurrent.futures**: Thread pool management for parallel processing

## Frontend Libraries
- **Bootstrap**: CSS framework for responsive design and dark theme
- **Font Awesome**: Icon library for UI elements

## External Services
- **OceanOfPDF**: Book search through web scraping of search results
- **Library Genesis (LibGen)**: Academic book database access via web scraping
- **Internet Archive**: Digital library API for book searches
- **Various Book Source APIs**: Multiple fallback sources for comprehensive coverage

## Browser APIs
- **Fetch API**: Client-side HTTP requests to backend
- **DOM Manipulation**: Dynamic result rendering and user interaction handling
import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from book_searcher import BookSearcher

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Enable CORS
CORS(app)

# Initialize book searcher
searcher = BookSearcher()

@app.route('/')
def index():
    """Serve the main HTML page"""
    response = send_from_directory('static', 'index.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    response = send_from_directory('static', filename)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/search_books', methods=['POST'])
def search_books():
    """Search for books across multiple sources"""
    try:
        data = request.get_json()
        if not data or 'books' not in data:
            return jsonify({'error': 'Invalid request format. Expected {"books": [{"title": "...", "author": "..."}]}'}), 400
        
        books = data['books']
        if not isinstance(books, list):
            return jsonify({'error': 'Books must be a list'}), 400
        
        # Validate book entries
        for book in books:
            if not isinstance(book, dict) or 'title' not in book or 'author' not in book:
                return jsonify({'error': 'Each book must have title and author fields'}), 400
        
        app.logger.info(f"Searching for {len(books)} books")
        
        # Search for books
        results = searcher.search_books(books)
        
        app.logger.info(f"Found {len(results)} results")
        return jsonify({'results': results})
        
    except Exception as e:
        app.logger.error(f"Error in search_books: {str(e)}")
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/test-search')
def test_search():
    """Test search endpoint for debugging"""
    test_books = [{"title": "Republic", "author": "Plato"}]
    results = searcher.search_books(test_books)
    return jsonify({
        'test_request': test_books,
        'results': results,
        'count': len(results)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

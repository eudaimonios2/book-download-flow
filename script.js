class BookFinder {
    constructor() {
        console.log('BookFinder constructor called');
        
        this.searchBtn = document.getElementById('searchBtn');
        this.bookInput = document.getElementById('bookInput');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.errorMessage = document.getElementById('errorMessage');
        this.errorText = document.getElementById('errorText');
        this.resultsSection = document.getElementById('resultsSection');
        this.resultsTable = document.getElementById('resultsTable');
        this.emptyState = document.getElementById('emptyState');
        
        console.log('Elements found:', {
            searchBtn: !!this.searchBtn,
            bookInput: !!this.bookInput,
            loadingSpinner: !!this.loadingSpinner,
            errorMessage: !!this.errorMessage,
            errorText: !!this.errorText,
            resultsSection: !!this.resultsSection,
            resultsTable: !!this.resultsTable,
            emptyState: !!this.emptyState
        });
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        console.log('Initializing event listeners...');
        
        if (this.searchBtn) {
            this.searchBtn.addEventListener('click', () => {
                console.log('Search button clicked');
                this.performSearch();
            });
            console.log('Search button event listener added');
        } else {
            console.error('Search button not found!');
        }
        
        if (this.bookInput) {
            // Allow Enter key to trigger search when Ctrl/Cmd is pressed
            this.bookInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                    e.preventDefault();
                    console.log('Keyboard shortcut triggered');
                    this.performSearch();
                }
            });
            console.log('Keyboard event listener added');
        } else {
            console.error('Book input not found!');
        }
    }
    
    parseBookInput() {
        const input = this.bookInput.value.trim();
        if (!input) {
            throw new Error('Please enter at least one book in the format "Title – Author"');
        }
        
        const lines = input.split('\n').filter(line => line.trim());
        const books = [];
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) continue;
            
            // Split by various dash characters
            const parts = line.split(/\s*[–—-]\s*/);
            if (parts.length !== 2) {
                throw new Error(`Line ${i + 1}: Invalid format. Use "Title – Author"`);
            }
            
            const [title, author] = parts.map(part => part.trim());
            if (!title || !author) {
                throw new Error(`Line ${i + 1}: Both title and author are required`);
            }
            
            books.push({ title, author });
        }
        
        if (books.length === 0) {
            throw new Error('No valid books found. Please check your formatting.');
        }
        
        return books;
    }
    
    async performSearch() {
        try {
            // Hide previous results and errors
            this.hideAllStates();
            
            // Parse input
            const books = this.parseBookInput();
            
            // Show loading state
            this.showLoading();
            this.searchBtn.disabled = true;
            this.searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Searching...';
            
            // Perform search
            console.log('Sending search request for books:', books);
            
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ books })
            });
            
            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Error response data:', errorData);
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }
            
            const results = await response.json();
            console.log('Search results received:', results);
            this.displayResults(results);
            
        } catch (error) {
            console.error('Search error:', error);
            console.error('Error stack:', error.stack);
            this.showError(error.message);
        } finally {
            this.hideLoading();
            this.searchBtn.disabled = false;
            this.searchBtn.innerHTML = '<i class="fas fa-search me-2"></i>Search for PDFs';
        }
    }
    
    hideAllStates() {
        this.loadingSpinner.style.display = 'none';
        this.errorMessage.style.display = 'none';
        this.resultsSection.style.display = 'none';
        this.emptyState.style.display = 'none';
    }
    
    showLoading() {
        this.hideAllStates();
        this.loadingSpinner.style.display = 'block';
    }
    
    hideLoading() {
        this.loadingSpinner.style.display = 'none';
    }
    
    showError(message) {
        this.hideAllStates();
        this.errorText.textContent = message;
        this.errorMessage.style.display = 'block';
    }
    
    displayResults(results) {
        console.log('Displaying results:', results);
        this.hideAllStates();
        
        if (!results || results.length === 0) {
            console.log('No results found, showing empty state');
            this.emptyState.style.display = 'block';
            return;
        }
        
        // Clear previous results
        this.resultsTable.innerHTML = '';
        
        // Group results by book
        const bookGroups = {};
        results.forEach(result => {
            const key = `${result.title}|||${result.author}`;
            if (!bookGroups[key]) {
                bookGroups[key] = [];
            }
            bookGroups[key].push(result);
        });
        
        // Create table rows
        Object.values(bookGroups).forEach(group => {
            group.forEach((result, index) => {
                const row = this.createResultRow(result, index === 0 ? group.length : 0);
                this.resultsTable.appendChild(row);
            });
        });
        
        this.resultsSection.style.display = 'block';
        
        // Smooth scroll to results
        this.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    createResultRow(result, rowspan = 0) {
        const row = document.createElement('tr');
        
        // Title cell (with rowspan if multiple sources)
        if (rowspan > 0) {
            const titleCell = document.createElement('td');
            titleCell.textContent = result.title;
            titleCell.rowSpan = rowspan;
            titleCell.classList.add('fw-medium');
            row.appendChild(titleCell);
            
            // Author cell (with rowspan if multiple sources)
            const authorCell = document.createElement('td');
            authorCell.textContent = result.author;
            authorCell.rowSpan = rowspan;
            authorCell.classList.add('text-muted');
            row.appendChild(authorCell);
        } else if (rowspan === 0) {
            // This is a continuation row for the same book
            // Don't add title and author cells
        }
        
        // Source cell
        const sourceCell = document.createElement('td');
        const sourceSpan = document.createElement('span');
        sourceSpan.classList.add('badge');
        
        // Add source-specific styling
        switch (result.source) {
            case 'OceanOfPDF':
                sourceSpan.classList.add('bg-primary');
                sourceSpan.innerHTML = '<i class="fas fa-water me-1"></i>OceanOfPDF';
                break;
            case 'LibGen':
                sourceSpan.classList.add('bg-success');
                sourceSpan.innerHTML = '<i class="fas fa-book me-1"></i>LibGen';
                break;
            case 'Internet Archive':
                sourceSpan.classList.add('bg-warning', 'text-dark');
                sourceSpan.innerHTML = '<i class="fas fa-archive me-1"></i>Internet Archive';
                break;
            case 'Project Gutenberg':
                sourceSpan.classList.add('bg-info');
                sourceSpan.innerHTML = '<i class="fas fa-book-open me-1"></i>Project Gutenberg';
                break;
            default:
                sourceSpan.classList.add('bg-secondary');
                sourceSpan.textContent = result.source;
        }
        
        sourceCell.appendChild(sourceSpan);
        row.appendChild(sourceCell);
        
        // Download cell
        const downloadCell = document.createElement('td');
        const downloadBtn = document.createElement('a');
        downloadBtn.href = result.link;
        downloadBtn.target = '_blank';
        downloadBtn.rel = 'noopener noreferrer';
        downloadBtn.classList.add('btn', 'btn-info', 'btn-sm');
        downloadBtn.innerHTML = '<i class="fas fa-download me-1"></i>Download PDF';
        
        // Add click tracking
        downloadBtn.addEventListener('click', () => {
            console.log(`Download clicked: ${result.title} from ${result.source}`);
        });
        
        downloadCell.appendChild(downloadBtn);
        row.appendChild(downloadCell);
        
        return row;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing BookFinder...');
    try {
        const bookFinder = new BookFinder();
        console.log('BookFinder initialized successfully');
        
        // Add a global test function for debugging
        window.testSearch = function() {
            console.log('Running test search...');
            bookFinder.bookInput.value = 'Republic – Plato';
            bookFinder.performSearch();
        };
        
        console.log('Test function added. Try running: testSearch() in console');
    } catch (error) {
        console.error('Error initializing BookFinder:', error);
    }
});

// Add some helper functions for better UX
window.addEventListener('beforeunload', (e) => {
    const bookInput = document.getElementById('bookInput');
    if (bookInput && bookInput.value.trim()) {
        e.preventDefault();
        e.returnValue = '';
    }
});

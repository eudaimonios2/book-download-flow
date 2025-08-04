# Free PDF Book Finder

A web application that searches for free PDF download links from legal sources including Project Gutenberg, Internet Archive, and other public domain repositories.

## Features

- **Multi-source Search**: Searches across Project Gutenberg, Internet Archive, and other legal sources
- **Parallel Processing**: Fast search results using concurrent requests
- **Simple Interface**: Clean, user-friendly web interface with dark theme
- **Batch Search**: Enter multiple books at once
- **Real-time Results**: See results as they come in from different sources
- **Error Handling**: Graceful error handling with helpful messages
- **Responsive Design**: Works on desktop and mobile devices

## How to Use

1. **Enter Books**: Type book titles and authors in the format "Title – Author" (one per line)
   
   **Example format:**
   ```
   Republic – Plato
   Pride and Prejudice – Jane Austen
   Alice – Lewis Carroll
   ```

2. **Click Search**: Press the "Search for PDFs" button to start searching

3. **Download**: Click the download buttons next to any results to get your PDFs

## Supported Books

The application works best with:
- **Classic Literature**: Books in the public domain (published before 1928 in the US)
- **Public Domain Works**: Books whose copyright has expired
- **Open Access Publications**: Academic and research publications made freely available

## Example Books That Work

Try searching for these popular classics:
- Republic – Plato
- Pride and Prejudice – Jane Austen  
- Alice's Adventures in Wonderland – Lewis Carroll
- Frankenstein – Mary Shelley
- The Great Gatsby – F. Scott Fitzgerald
- Dracula – Bram Stoker
- The Adventures of Sherlock Holmes – Arthur Conan Doyle
- Jane Eyre – Charlotte Brontë

## Technical Details

### Backend (Python Flask)
- **Endpoint**: `/search` (POST)
- **Request Format**: `{"books": [{"title": "...", "author": "..."}]}`
- **Response Format**: `[{"title": "...", "author": "...", "source": "...", "link": "..."}]`

### Frontend (HTML/CSS/JavaScript)
- Vanilla JavaScript with Bootstrap for styling
- Real-time search interface with loading states
- Responsive design that works on all devices

## Running the Project

1. **On Replit**: Simply click the "Run" button - the Flask server will start automatically
2. **Locally**: 
   ```bash
   pip install -r requirements.txt
   python main.py
   ```
3. **Access**: Open your browser to the provided URL (usually `https://your-repl-name.replit.app`)

## Legal Notice

This application only searches for and provides links to books that are:
- In the public domain
- Legally available for free distribution
- Provided by legitimate sources like Project Gutenberg and Internet Archive

We do not host any copyrighted content and only link to legal, free sources.
   
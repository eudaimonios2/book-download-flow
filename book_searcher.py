import requests
import logging
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote, urljoin
import time
import json
import re

class BookSearcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def search_books(self, books):
        """Search for books across all sources in parallel"""
        results = []
        
        # Add demo results for common classic books to show functionality
        demo_books = {
            ('republic', 'plato'): {
                'title': 'Republic',
                'author': 'Plato', 
                'source': 'OceanOfPDF',
                'link': 'https://oceanofpdf.com/the-republic-pdf-free-download/'
            },
            ('pride and prejudice', 'jane austen'): {
                'title': 'Pride and Prejudice',
                'author': 'Jane Austen',
                'source': 'Project Gutenberg', 
                'link': 'https://www.gutenberg.org/cache/epub/1342/pg1342.pdf'
            },
            ('alice', 'lewis carroll'): {
                'title': "Alice's Adventures in Wonderland",
                'author': 'Lewis Carroll',
                'source': 'Project Gutenberg',
                'link': 'https://www.gutenberg.org/cache/epub/11/pg11.pdf'
            },
            ('frankenstein', 'mary shelley'): {
                'title': 'Frankenstein',
                'author': 'Mary Wollstonecraft Shelley',
                'source': 'Project Gutenberg',
                'link': 'https://www.gutenberg.org/cache/epub/84/pg84.pdf'
            },
            ('great gatsby', 'f. scott fitzgerald'): {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'source': 'Internet Archive',
                'link': 'https://archive.org/download/great-gatsby_20200827/The%20Great%20Gatsby%20-%20F.%20Scott%20Fitzgerald.pdf'
            }
        }
        
        # Skip demo results for now - use only real searches for better accuracy
        
        # Always try real searches for better results
        # Skip demo results if we want real-time searches only
        
        # Otherwise, try real searches
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all search tasks
            future_to_book = {}
            
            for book in books:
                title = book['title'].strip()
                author = book['author'].strip()
                
                if not title or not author:
                    continue
                
                # Submit search tasks for each source
                future_archive = executor.submit(self.search_internet_archive, title, author)
                future_gutenberg = executor.submit(self.search_project_gutenberg, title, author)
                future_libgen = executor.submit(self.search_libgen, title, author)
                future_pdfcoffee = executor.submit(self.search_pdfcoffee, title, author)
                
                future_to_book[future_archive] = (book, 'Internet Archive')
                future_to_book[future_gutenberg] = (book, 'Project Gutenberg')
                future_to_book[future_libgen] = (book, 'LibGen')
                future_to_book[future_pdfcoffee] = (book, 'PDF Coffee')
            
            # Collect results
            for future in as_completed(future_to_book):
                book_info, source = future_to_book[future]
                try:
                    result = future.result(timeout=30)
                    if result:
                        results.append({
                            'title': book_info['title'],
                            'author': book_info['author'],
                            'source': source,
                            'link': result
                        })
                except Exception as e:
                    logging.error(f"Error searching {source} for {book_info['title']}: {str(e)}")
        
        return results
    
    def search_oceanpdf(self, title, author):
        """Search OceanOfPDF for a book using the proper flow"""
        try:
            search_query = f"{title} {author}"
            search_url = f"https://oceanofpdf.com/?s={quote(search_query)}"
            
            logging.info(f"Searching OceanOfPDF: {search_url}")
            
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for search results - find article links
            articles = soup.find_all('article') or soup.find_all('div', class_=['post', 'entry'])
            
            for article in articles[:3]:  # Check first 3 results
                # Find the book page link
                title_link = None
                links = article.find_all('a', href=True)
                for link in links:
                    href = link.get('href')
                    if href and 'oceanofpdf.com' in href and any(word in href.lower() for word in title.lower().split()[:2]):
                        title_link = link
                        break
                
                if not title_link:
                    continue
                
                book_url = title_link.get('href')
                if not book_url:
                    continue
                
                # Visit the book page to find the download form
                pdf_link = self._get_oceanpdf_download_link(book_url)
                if pdf_link:
                    return pdf_link
            
            return None
            
        except Exception as e:
            logging.error(f"Error searching OceanOfPDF: {str(e)}")
            return None
    
    def _get_oceanpdf_download_link(self, book_url):
        """Extract PDF download link from OceanOfPDF book page using the proper flow"""
        try:
            response = self.session.get(book_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for the image submit button as described: 
            # <input style="width: 141px; height: 192px;" alt="Submit" src="https://media.oceanofpdf.com/pdf-button.jpg" type="image">
            image_buttons = soup.find_all('input', {'type': 'image'})
            for button in image_buttons:
                src = button.get('src', '')
                alt = button.get('alt', '')
                
                # Check if this is the PDF download button
                if 'pdf-button' in src or alt.lower() == 'submit':
                    # This button should lead to Fetching_Resource.php
                    # We need to construct the proper download URL
                    parent_form = button.find_parent('form')
                    if parent_form:
                        action = parent_form.get('action', '')
                        method = parent_form.get('method', 'post').lower()
                        
                        if 'Fetching_Resource.php' in action or not action:
                            # Return the fetching resource URL
                            base_url = 'https://oceanofpdf.com/'
                            if action:
                                download_url = urljoin(base_url, action)
                            else:
                                download_url = base_url + 'Fetching_Resource.php'
                            
                            return download_url
            
            # Fallback: look for any form that might lead to the download
            forms = soup.find_all('form')
            for form in forms:
                action = form.get('action', '')
                if 'Fetching_Resource.php' in action:
                    return urljoin('https://oceanofpdf.com/', action)
            
            # If no form found, try to find direct links to Fetching_Resource.php
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if 'Fetching_Resource.php' in href:
                    return urljoin('https://oceanofpdf.com/', href)
            
            return None
            
        except Exception as e:
            logging.error(f"Error getting OceanOfPDF download link: {str(e)}")
            return None
    
    def search_libgen(self, title, author):
        """Search Library Genesis for a book"""
        try:
            # Try multiple LibGen mirrors
            mirrors = [
                'https://libgen.is/',
                'https://libgen.li/',
                'https://libgen.st/'
            ]
            
            for mirror in mirrors:
                try:
                    search_query = f"{title} {author}"
                    search_url = f"{mirror}search.php?req={quote(search_query)}&lg_topic=libgen&open=0&view=simple&res=25&phrase=1&column=def"
                    
                    logging.info(f"Searching LibGen mirror {mirror}: {search_url}")
                    
                    response = self.session.get(search_url, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find results table
                    tables = soup.find_all('table')
                    for table in tables:
                        rows = table.find_all('tr')[1:]  # Skip header
                        
                        for row in rows[:3]:  # Check first 3 results
                            cells = row.find_all('td')
                            if len(cells) < 5:
                                continue
                            
                            # Look for download links in the row
                            for cell in cells:
                                links = cell.find_all('a', href=True)
                                for link in links:
                                    href = link.get('href')
                                    if href and ('download' in href.lower() or 'get.php' in href or 'ads.php' in href):
                                        # Make absolute URL if needed
                                        if not href.startswith('http'):
                                            href = urljoin(mirror, href)
                                        return href
                    
                    # If we get here, this mirror worked but no results found
                    break
                    
                except Exception as mirror_error:
                    logging.warning(f"Mirror {mirror} failed: {str(mirror_error)}")
                    continue
            
            return None
            
        except Exception as e:
            logging.error(f"Error searching LibGen: {str(e)}")
            return None
    
    def search_internet_archive(self, title, author):
        """Search Internet Archive for a book with improved relevance checking"""
        try:
            # Try multiple search variations
            search_queries = [
                f'title:("{title}") AND creator:("{author}")',
                f'{title} {author}',
                f'{title} AND {author}'
            ]
            
            for search_query in search_queries:
                try:
                    search_url = f"https://archive.org/advancedsearch.php?q={quote(search_query)}&fl[]=identifier,title,creator&rows=10&page=1&output=json"
                    
                    logging.info(f"Searching Internet Archive: {search_url}")
                    
                    response = self.session.get(search_url, timeout=15)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if 'response' in data and 'docs' in data['response']:
                        docs = data['response']['docs']
                        
                        for doc in docs[:5]:  # Check first 5 results
                            identifier = doc.get('identifier')
                            if identifier:
                                # Try multiple PDF naming patterns
                                pdf_patterns = [
                                    f"https://archive.org/download/{identifier}/{identifier}.pdf",
                                    f"https://archive.org/download/{identifier}/{identifier}_text.pdf",
                                    f"https://archive.org/download/{identifier}/{identifier}_bw.pdf"
                                ]
                                
                                for pdf_url in pdf_patterns:
                                    try:
                                        head_response = self.session.head(pdf_url, timeout=8, allow_redirects=True)
                                        if head_response.status_code == 200:
                                            # Verify it's actually the right book by checking title relevance
                                            doc_title = doc.get('title', '').lower()
                                            if any(word.lower() in doc_title for word in title.split()[:2]):
                                                return pdf_url
                                        # Handle redirects
                                        elif head_response.status_code in [302, 301] and head_response.headers.get('location'):
                                            redirect_url = head_response.headers.get('location')
                                            if redirect_url.endswith('.pdf'):
                                                doc_title = doc.get('title', '').lower()
                                                if any(word.lower() in doc_title for word in title.split()[:2]):
                                                    return redirect_url
                                    except:
                                        continue
                    
                    # If we found results but no PDFs, try next query
                    if data.get('response', {}).get('docs'):
                        continue
                    else:
                        break
                        
                except Exception as query_error:
                    logging.warning(f"Search query failed: {str(query_error)}")
                    continue
            
            return None
            
        except Exception as e:
            logging.error(f"Error searching Internet Archive: {str(e)}")
            return None
    
    def search_pdfcoffee(self, title, author):
        """Search PDF Coffee for a book"""
        try:
            search_query = f"{title} {author}"
            search_url = f"https://pdfcoffee.com/search?q={quote(search_query)}"
            
            logging.info(f"Searching PDF Coffee: {search_url}")
            
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for search results
            results = soup.find_all('div', class_=['item', 'result']) or soup.find_all('a', href=True)
            
            for result in results[:5]:
                link = result if result.name == 'a' else result.find('a', href=True)
                if link:
                    href = link.get('href')
                    if href and 'pdfcoffee.com' in href and any(word.lower() in href.lower() for word in title.split()[:2]):
                        # Make absolute URL
                        if not href.startswith('http'):
                            href = urljoin('https://pdfcoffee.com/', href)
                        return href
            
            return None
            
        except Exception as e:
            logging.error(f"Error searching PDF Coffee: {str(e)}")
            return None
    
    def search_project_gutenberg(self, title, author):
        """Search Project Gutenberg for a book"""
        try:
            search_query = f"{title} {author}"
            search_url = f"https://www.gutenberg.org/ebooks/search/?query={quote(search_query)}&submit_search=Go%21"
            
            logging.info(f"Searching Project Gutenberg: {search_url}")
            
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for book results
            results = soup.find_all('li', class_='booklink')
            
            for result in results[:3]:  # Check first 3 results
                # Find the book ID from the link
                link = result.find('a', href=True)
                if not link:
                    continue
                
                href = link.get('href')
                if '/ebooks/' in href:
                    # Extract book ID
                    import re
                    book_id_match = re.search(r'/ebooks/(\d+)', href)
                    if book_id_match:
                        book_id = book_id_match.group(1)
                        
                        # Try different PDF formats
                        pdf_urls = [
                            f"https://www.gutenberg.org/files/{book_id}/{book_id}-pdf.pdf",
                            f"https://www.gutenberg.org/files/{book_id}/{book_id}.pdf",
                            f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.pdf"
                        ]
                        
                        for pdf_url in pdf_urls:
                            try:
                                head_response = self.session.head(pdf_url, timeout=10)
                                if head_response.status_code == 200:
                                    return pdf_url
                            except:
                                continue
            
            return None
            
        except Exception as e:
            logging.error(f"Error searching Project Gutenberg: {str(e)}")
            return None
    
    def search_pdf_drive(self, title, author):
        """Search PDF Drive for a book"""
        try:
            search_query = f"{title} {author} filetype:pdf"
            # Use a general search approach since PDF Drive has anti-scraping measures
            # Try with a simplified search URL format
            search_url = f"https://www.pdfdrive.com/search?q={quote(search_query)}"
            
            logging.info(f"Searching PDF Drive: {search_url}")
            
            # Due to anti-scraping measures, we'll return None for now
            # In a production environment, you might use a proper API or service
            return None
            
        except Exception as e:
            logging.error(f"Error searching PDF Drive: {str(e)}")
            return None

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

class WebsiteCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_urls = set()  # Track visited URLs to avoid duplicates
        self.all_urls = set()      # Store all found URLs
        self.domain = urlparse(base_url).netloc  # Extract domain (e.g., fiberoptics.com)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def is_valid_url(self, url):
        """Check if URL is valid and belongs to the target domain"""
        parsed = urlparse(url)
        return bool(parsed.netloc) and parsed.netloc == self.domain

    def get_links(self, url):
        """Fetch a page and extract all links"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()  # Raise exception for bad status codes
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = set()
            
            # Find all <a> tags with href attributes
            for anchor in soup.find_all('a', href=True):
                href = anchor['href']
                full_url = urljoin(url, href.strip())  # Convert relative URLs to absolute
                
                # Filter for URLs within the same domain
                if self.is_valid_url(full_url):
                    links.add(full_url)
                    
            return links
            
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return set()

    def crawl(self, start_url, max_pages=100):
        """Crawl the website starting from start_url"""
        to_visit = {start_url}
        
        while to_visit and len(self.visited_urls) < max_pages:
            url = to_visit.pop()  # Get next URL to visit
            
            if url in self.visited_urls:
                continue
                
            print(f"Crawling: {url}")
            self.visited_urls.add(url)
            self.all_urls.add(url)
            
            # Get all links from current page
            new_links = self.get_links(url)
            
            # Add new links to visit if not already visited
            to_visit.update(link for link in new_links if link not in self.visited_urls)
            
            # Be polite to the server
            time.sleep(1)  # Delay between requests
            
        print(f"\nCrawling complete. Found {len(self.all_urls)} URLs.")

    def save_urls(self, filename="fiberoptics_urls.txt"):
        """Save collected URLs to a file"""
        with open(filename, 'w', encoding='utf-8') as f:
            for url in sorted(self.all_urls):
                f.write(f"{url}\n")
        print(f"URLs saved to {filename}")

def main():
    base_url = "https://fiberoptics.com"
    crawler = WebsiteCrawler(base_url)
    
    # Start crawling from the homepage
    crawler.crawl(base_url, max_pages=200)  # Adjust max_pages as needed
    
    # Save the results
    crawler.save_urls()
    
    # Print all URLs (optional)
    print("\nAll collected URLs:")
    for url in sorted(crawler.all_urls):
        print(url)

if __name__ == "__main__":
    main()
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class WebsiteAnalyzer:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_urls = set()
        self.broken_links = []
        self.page_load_times = {}

    def check_page_speed(self, url):
        """Measure page load time"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            end_time = time.time()
            
            load_time = end_time - start_time
            self.page_load_times[url] = load_time
            
            return {
                'url': url,
                'load_time': load_time,
                'status_code': response.status_code
            }
        except requests.RequestException as e:
            return {
                'url': url,
                'error': str(e)
            }

    def find_broken_links(self, url):
        """Check for broken links on a page"""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                if full_url in self.visited_urls:
                    continue
                    
                self.visited_urls.add(full_url)
                
                if self.base_url in full_url:
                    try:
                        link_response = requests.head(full_url, timeout=5)
                        if link_response.status_code >= 400:
                            self.broken_links.append({
                                'source': url,
                                'broken_url': full_url,
                                'status': link_response.status_code
                            })
                    except requests.RequestException:
                        self.broken_links.append({
                            'source': url,
                            'broken_url': full_url,
                            'status': 'Connection Error'
                        })
        except requests.RequestException as e:
            print(f"Error accessing {url}: {e}")

    def check_seo_basics(self, url):
        """Check basic SEO elements"""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            seo_report = {
                'url': url,
                'title': '',
                'title_length': 0,
                'description': '',
                'h1_count': 0,
                'img_alt_missing': 0
            }
            
            title_tag = soup.find('title')
            if title_tag:
                seo_report['title'] = title_tag.text
                seo_report['title_length'] = len(title_tag.text)
            
            desc_tag = soup.find('meta', {'name': 'description'})
            if desc_tag and desc_tag.get('content'):
                seo_report['description'] = desc_tag['content']
            
            seo_report['h1_count'] = len(soup.find_all('h1'))
            
            for img in soup.find_all('img'):
                if not img.get('alt'):
                    seo_report['img_alt_missing'] += 1
                    
            return seo_report
            
        except requests.RequestException as e:
            return {'url': url, 'error': str(e)}

    def generate_report(self):
        """Generate a comprehensive improvement report"""
        print("\n=== Website Improvement Report for fiberoptics.com ===")
        
        print("\nPage Load Times:")
        for url, time in self.page_load_times.items():
            recommendation = "Good" if time < 3 else "Needs Optimization"
            print(f"{url}: {time:.2f} seconds - {recommendation}")
        
        print("\nBroken Links:")
        if self.broken_links:
            for link in self.broken_links:
                print(f"Source: {link['source']}")
                print(f"Broken URL: {link['broken_url']}")
                print(f"Status: {link['status']}\n")
        else:
            print("No broken links found!")
            
        print("\nRecommendations:")
        if any(t > 3 for t in self.page_load_times.values()):
            print("- Optimize images and enable compression to improve load times")
        if self.broken_links:
            print("- Fix broken links to improve user experience and SEO")

def read_urls_from_file(filename="fiberoptics_urls.txt"):
    """Read URLs from the output file"""
    urls = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(urls)} URLs from {filename}")
    except FileNotFoundError:
        print(f"Warning: {filename} not found. Please run the crawler script or specify URLs manually.")
    return urls

def main():
    website = WebsiteAnalyzer("https://fiberoptics.com")
    
    # Pages to analyze (manually entered URLs here)
    pages_to_check = [
        # "https://fiberoptics.com",
        # "https://fiberoptics.com/about",
        # "https://fiberoptics.com/products"
    ]
    
    # If no pages are manually specified, read from file
    if not pages_to_check:
        print("No URLs manually specified. Attempting to read from file...")
        pages_to_check = read_urls_from_file()
    
    # Check if we have any URLs to analyze
    if not pages_to_check:
        print("No URLs to analyze. Please specify URLs or ensure fiberoptics_urls.txt exists.")
        return
    
    print(f"Analyzing {len(pages_to_check)} pages...")
    
    # Analyze each page
    for page in pages_to_check:
        print(f"\nAnalyzing {page}...")
        
        speed_result = website.check_page_speed(page)
        print(f"Load time: {speed_result.get('load_time', 'N/A'):.2f} seconds")
        
        seo_result = website.check_seo_basics(page)
        print("SEO Check:")
        print(f"Title length: {seo_result['title_length']} characters")
        print(f"H1 tags: {seo_result['h1_count']}")
        print(f"Images without alt text: {seo_result['img_alt_missing']}")
        
        website.find_broken_links(page)
    
    website.generate_report()

if __name__ == "__main__":
    main()
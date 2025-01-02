"""
- This is currently not used.
- This does not work for reddit.
"""

import requests
from bs4 import BeautifulSoup

class PageFetcher:
    @staticmethod
    def fetch_page_text(url):
        """Fetch and extract text content from a web page.
        
        Args:
            url (str): The URL of the page to fetch
            
        Returns:
            str: The extracted text content
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
                
            # Get text and clean up whitespace
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page: {e}")
            return None

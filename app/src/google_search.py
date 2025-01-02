from googleapiclient.discovery import build
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class GoogleSearch:
    """A class to handle Google Custom Search operations."""
    
    def __init__(self):
        """
        Initialize the GoogleSearch instance.
        """
        keys = json.load(open("app/settings/api-keys.json"))
        self.api_key = keys["google_api_key"]
        self.search_engine_id = keys["google_custom_search_id"]
        self.service = build("customsearch", "v1", developerKey=self.api_key)
        
        self.site_map = {
            'reddit': '(site:reddit.com OR site:www.redditmedia.com)',
            'arxiv': 'site:arxiv.org'
        }
        
        self.freshness_map = {
            'day': 'date:d',
            'week': 'date:w',
            'month': 'date:m'
        }

    def clean_text(self, text):
        """Clean text similar to Bing's implementation."""
        if not text:
            return text
        text = text.replace('\u2018', "'").replace('\u2019', "'")
        text = text.replace('\u201C', '"').replace('\u201D', '"')
        return ''.join(char for char in text if 32 <= ord(char) <= 126 or char in '\n\r\t')

    def search(self, query: str, site_filter: str = '', time_filter: str = '') -> Dict[str, Any]:
        """
        Perform a Google Custom Search with Bing-like parameters.
        
        Args:
            query (str): Search query
            site_filter (str): Filter for specific sites ('reddit', 'arxiv')
            time_filter (str): Time filter ('day', 'week', 'month', 'year')
        """
        if not query:
            raise ValueError('Query is required')

        search_query = f"{query} {self.site_map[site_filter]}" if site_filter in self.site_map else query
        
        # Add time filter
        if time_filter in self.freshness_map:
            search_query = f"{search_query} {self.freshness_map[time_filter]}"
        elif time_filter == 'year':
            last_year = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            search_query = f"{search_query} after:{last_year}"

        try:
            response = self.service.cse().list(
                q=search_query,
                cx=self.search_engine_id,
                num=10  # Google Custom Search API maximum is 10
            ).execute()

            # Format response to match Bing's structure
            if 'items' in response:
                web_pages = {
                    'value': [
                        {
                            'name': self.clean_text(item['title']) if 'title' in item else '',
                            'url': item['link'] if 'link' in item else '',
                            'snippet': self.clean_text(item['snippet']) if 'snippet' in item else ''
                        }
                        for item in response['items']
                    ]
                }
                return {'webPages': web_pages}
            return {}

        except Exception as e:
            error_detail = {
                'error': str(e),
                'status_code': None,
                'response_text': str(e)
            }
            print(f"API Error: {error_detail}")
            raise Exception(error_detail)

if __name__ == "__main__":
    # Example usage
    search_client = GoogleSearch()
    results = search_client.search("python programming")

    if results and 'webPages' in results:
        web_pages = results['webPages']['value']
        print(f"\nFound {len(web_pages)} results:")
        
        for i, result in enumerate(web_pages, 1):
            print(f"\nResult {i}:")
            print(f"Title: {result['name']}")
            print(f"URL: {result['url']}")
            print(f"Snippet: {result['snippet']}")
            print("-" * 50)

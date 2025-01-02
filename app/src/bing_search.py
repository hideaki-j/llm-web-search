import json
import requests
from datetime import datetime, timedelta

class BingSearch:
    def __init__(self):
        try:
            with open('./app/settings/api-keys.json', 'r') as f:
                self.BING_API_KEY = json.load(f)['bing']
        except FileNotFoundError:
            raise Exception("api-keys.json not found. Please create it with your API key.")
        except json.JSONDecodeError:
            raise Exception("Invalid JSON format in api-keys.json")
            
        self.BING_ENDPOINT = 'https://api.bing.microsoft.com/v7.0/search'
        
        self.site_map = {
            'reddit': '(site:reddit.com OR site:www.redditmedia.com)',
            'arxiv': 'site:arxiv.org'
        }
        
        self.freshness_map = {
            'day': 'day',
            'week': 'week',
            'month': 'month'
        }

    def clean_text(self, text):
        if not text:
            return text
        # Handle smart quotes and other special quotes
        text = text.replace('\u2018', "'")  # Left single quote
        text = text.replace('\u2019', "'")  # Right single quote
        text = text.replace('\u201C', '"')  # Left double quote
        text = text.replace('\u201D', '"')  # Right double quote
        # Remove non-printable characters while preserving basic ASCII
        return ''.join(char for char in text if 32 <= ord(char) <= 126 or char in '\n\r\t')

    def search(self, query, site_filter='', time_filter=''):
        if not query:
            raise ValueError('Query is required')
            
        search_query = f"{query} {self.site_map[site_filter]}" if site_filter in self.site_map else query
        
        params = {
            'q': search_query,
            'count': 50,
            'textDecorations': True,
            'mkt': 'en-US'
        }
        
        # Add freshness parameter if time filter is selected
        if time_filter in self.freshness_map:
            params['freshness'] = self.freshness_map[time_filter]
        elif time_filter == 'year':
            # Calculate date range for the past year
            today = datetime.now()
            last_year = today - timedelta(days=365)
            params['freshness'] = f"{last_year.strftime('%Y-%m-%d')}..{today.strftime('%Y-%m-%d')}"
        
        try:
            response = requests.get(
                self.BING_ENDPOINT,
                params=params,
                headers={
                    'Ocp-Apim-Subscription-Key': self.BING_API_KEY
                }
            )
            response.raise_for_status()
            
            # Clean the snippets and names in the response
            data = response.json()
            if 'webPages' in data and 'value' in data['webPages']:
                for result in data['webPages']['value']:
                    result['snippet'] = self.clean_text(result.get('snippet', ''))
                    result['name'] = self.clean_text(result.get('name', ''))
                    
            return data
        except requests.exceptions.RequestException as e:
            # Add more detailed error information
            error_detail = {
                'error': str(e),
                'status_code': response.status_code if hasattr(response, 'status_code') else None,
                'response_text': response.text if hasattr(response, 'text') else None
            }
            print(f"API Error: {error_detail}")  # Add console logging
            raise Exception(error_detail)

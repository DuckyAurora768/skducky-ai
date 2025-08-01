import requests
from bs4 import BeautifulSoup
import json
import os
import time
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime, timedelta

class SkriptHubService:
    def __init__(self):
        self.base_url = "https://skripthub.net"
        self.cache_dir = "data/skripthub_cache"
        self.cache_duration = timedelta(days=7)
        self.headers = {
            'User-Agent': 'SkDucky-AI/1.0 (Advanced Skript Assistant)'
        }
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load syntax mapping
        self.load_syntax_mapping()
        
    def load_syntax_mapping(self):
        """Load or create mapping of common terms to SkriptHub IDs"""
        self.syntax_map = {
            # Events
            "on death": {"id": "1001", "type": "event"},
            "on combust": {"id": "1026", "type": "event"},
            "on join": {"id": "119", "type": "event"},
            "on quit": {"id": "120", "type": "event"},
            "on damage": {"id": "115", "type": "event"},
            "on block break": {"id": "106", "type": "event"},
            "on block place": {"id": "107", "type": "event"},
            "on chat": {"id": "109", "type": "event"},
            "on command": {"id": "111", "type": "event"},
            "on click": {"id": "1094", "type": "event"},
            "on inventory click": {"id": "1337", "type": "event"},
            
            # Effects
            "send": {"id": "607", "type": "effect"},
            "broadcast": {"id": "593", "type": "effect"},
            "teleport": {"id": "614", "type": "effect"},
            "give": {"id": "599", "type": "effect"},
            "kill": {"id": "602", "type": "effect"},
            "spawn": {"id": "612", "type": "effect"},
            "cancel event": {"id": "594", "type": "effect"},
            
            # Expressions
            "player": {"id": "833", "type": "expression"},
            "attacker": {"id": "816", "type": "expression"},
            "victim": {"id": "816", "type": "expression"},
            "location": {"id": "863", "type": "expression"},
            "uuid": {"id": "928", "type": "expression"},
            "balance": {"id": "2420", "type": "expression"},
            
            # Conditions
            "is online": {"id": "274", "type": "condition"},
            "has permission": {"id": "273", "type": "condition"},
            "is set": {"id": "249", "type": "condition"},
            "contains": {"id": "215", "type": "condition"}
        }
        
    def get_cache_path(self, query: str) -> str:
        """Get cache file path for a query"""
        safe_query = re.sub(r'[^\w\s-]', '', query).strip().replace(' ', '_')
        return os.path.join(self.cache_dir, f"{safe_query}.json")
        
    def is_cache_valid(self, cache_path: str) -> bool:
        """Check if cache file is still valid"""
        if not os.path.exists(cache_path):
            return False
            
        mod_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        return datetime.now() - mod_time < self.cache_duration
        
    def save_to_cache(self, query: str, data: Dict):
        """Save data to cache"""
        cache_path = self.get_cache_path(query)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump({
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }, f, indent=2)
            
    def load_from_cache(self, query: str) -> Optional[Dict]:
        """Load data from cache if valid"""
        cache_path = self.get_cache_path(query)
        if self.is_cache_valid(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)['data']
        return None
        
    def search_documentation(self, query: str) -> List[Dict]:
        """Search SkriptHub documentation"""
        # Check cache first
        cached = self.load_from_cache(f"search_{query}")
        if cached:
            return cached
            
        try:
            # Search URL
            search_url = f"{self.base_url}/docs/?search={query}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Find search results (adjust based on actual HTML structure)
            result_elements = soup.find_all('div', class_='search-result')
            
            for elem in result_elements[:10]:  # Limit to 10 results
                title_elem = elem.find('h3') or elem.find('a')
                if title_elem:
                    results.append({
                        'title': title_elem.text.strip(),
                        'url': title_elem.get('href', ''),
                        'type': self._detect_syntax_type(title_elem.text)
                    })
                    
            # Save to cache
            self.save_to_cache(f"search_{query}", results)
            return results
            
        except Exception as e:
            print(f"Error searching SkriptHub: {e}")
            return []
            
    def get_syntax_details(self, doc_id: str) -> Optional[Dict]:
        """Get detailed syntax information from a specific doc page"""
        # Check cache
        cached = self.load_from_cache(f"doc_{doc_id}")
        if cached:
            return cached
            
        try:
            url = f"{self.base_url}/docs/?id={doc_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract information (adjust selectors based on actual HTML)
            data = {
                'id': doc_id,
                'title': '',
                'description': '',
                'syntax': [],
                'examples': [],
                'required_addons': [],
                'since': ''
            }
            
            # Title
            title_elem = soup.find('h1') or soup.find('h2', class_='doc-title')
            if title_elem:
                data['title'] = title_elem.text.strip()
                
            # Description
            desc_elem = soup.find('div', class_='description') or soup.find('p', class_='doc-description')
            if desc_elem:
                data['description'] = desc_elem.text.strip()
                
            # Syntax patterns
            syntax_section = soup.find('div', class_='syntax') or soup.find('section', {'id': 'syntax'})
            if syntax_section:
                code_blocks = syntax_section.find_all('code')
                data['syntax'] = [code.text.strip() for code in code_blocks]
                
            # Examples
            examples_section = soup.find('div', class_='examples') or soup.find('section', {'id': 'examples'})
            if examples_section:
                example_codes = examples_section.find_all('code')
                data['examples'] = [code.text.strip() for code in example_codes]
                
            # Save to cache
            self.save_to_cache(f"doc_{doc_id}", data)
            return data
            
        except Exception as e:
            print(f"Error fetching doc {doc_id}: {e}")
            return None
            
    def find_syntax_by_keyword(self, keyword: str) -> Optional[Dict]:
        """Find syntax information by keyword"""
        # Check direct mapping first
        keyword_lower = keyword.lower()
        
        for key, value in self.syntax_map.items():
            if keyword_lower in key or key in keyword_lower:
                details = self.get_syntax_details(value['id'])
                if details:
                    details['type'] = value['type']
                    return details
                    
        # If not found, try searching
        results = self.search_documentation(keyword)
        if results:
            # Get details of first result
            first_result = results[0]
            if 'id' in first_result:
                return self.get_syntax_details(first_result['id'])
                
        return None
        
    def _detect_syntax_type(self, text: str) -> str:
        """Detect syntax type from text"""
        text_lower = text.lower()
        if 'event' in text_lower or text_lower.startswith('on '):
            return 'event'
        elif 'effect' in text_lower:
            return 'effect'
        elif 'expression' in text_lower:
            return 'expression'
        elif 'condition' in text_lower:
            return 'condition'
        elif 'type' in text_lower:
            return 'type'
        return 'unknown'
        
    def analyze_user_request(self, request: str) -> Dict:
        """Analyze user request and find relevant syntax"""
        request_lower = request.lower()
        findings = {
            'events': [],
            'effects': [],
            'expressions': [],
            'conditions': [],
            'examples': []
        }
        
        # Keywords to search for
        keywords = {
            'events': ['on', 'when', 'event', 'trigger'],
            'effects': ['send', 'give', 'teleport', 'set', 'add', 'remove'],
            'expressions': ['player', 'location', 'item', 'block', 'uuid'],
            'conditions': ['if', 'is', 'has', 'contains']
        }
        
        # Search for relevant syntax
        for category, words in keywords.items():
            for word in words:
                if word in request_lower:
                    syntax_info = self.find_syntax_by_keyword(word)
                    if syntax_info:
                        findings[category].append(syntax_info)
                        
        return findings
        
    def generate_code_from_docs(self, request: str, findings: Dict) -> str:
        """Generate Skript code based on documentation findings"""
        code_parts = ["# Generated with SkDucky AI\n# Based on SkriptHub documentation\n"]
        
        # Add relevant examples from findings
        for category, items in findings.items():
            for item in items:
                if item.get('examples'):
                    # Use the first example as reference
                    example = item['examples'][0]
                    code_parts.append(f"\n# {item.get('title', 'Example')}:")
                    code_parts.append(example)
                    
        # If we have code parts, join them
        if len(code_parts) > 1:
            return '\n'.join(code_parts)
            
        # Fallback to basic template
        return """# Generated with SkDucky AI
# No specific documentation found for your request
# Here's a basic template:

command /help:
    trigger:
        send "&cPlease be more specific about what you need!" to player"""
#!/usr/bin/env python3
"""
PEP Database Updater
Fetches and updates PEP data from various public sources
"""
import os
import json
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from urllib.parse import quote_plus
import pandas as pd
from bs4 import BeautifulSoup
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PEPDatabaseManager:
    """Manages PEP database updates from multiple public sources"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.database_path = os.path.join(data_dir, "pep_database.json")
        self.cache_dir = os.path.join(data_dir, "pep_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Public data sources
        self.sources = {
            "opensanctions": {
                "name": "OpenSanctions",
                "url": "https://www.opensanctions.org/datasets/default/",
                "api_url": "https://api.opensanctions.org/",
                "description": "Global sanctions and PEP data"
            },
            "cia_world_leaders": {
                "name": "CIA World Leaders",
                "url": "https://www.cia.gov/resources/world-leaders/",
                "description": "Current world leaders"
            },
            "everypolitician": {
                "name": "EveryPolitician",
                "url": "http://everypolitician.org/",
                "api_url": "http://everypolitician.org/api/v0.1/countries.json",
                "description": "Politicians worldwide"
            },
            "pep_search": {
                "name": "PEP Search Aggregators",
                "urls": [
                    "https://www.worldcompliance.com/",
                    "https://sanctionssearch.ofac.treas.gov/"
                ],
                "description": "Various PEP search engines"
            }
        }
        
        self.load_database()
    
    def load_database(self):
        """Load existing database or create new one"""
        if os.path.exists(self.database_path):
            with open(self.database_path, 'r') as f:
                self.database = json.load(f)
            logger.info(f"Loaded existing database with {len(self.database.get('peps', []))} entries")
        else:
            self.database = {
                "peps": [],
                "sources": [],
                "version": "3.0",
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            self.save_database()
            logger.info("Created new PEP database")
    
    def save_database(self):
        """Save database to file"""
        self.database['last_updated'] = datetime.now().isoformat()
        with open(self.database_path, 'w') as f:
            json.dump(self.database, f, indent=2)
        logger.info(f"Saved database with {len(self.database.get('peps', []))} entries")
    
    async def fetch_everypolitician_data(self):
        """Fetch data from EveryPolitician API"""
        logger.info("Fetching EveryPolitician data...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.sources['everypolitician']['api_url'],
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        countries = await response.json()
                        
                        pep_entries = []
                        for country in countries[:10]:  # Limit for demo
                            country_name = country.get('name', '')
                            
                            for legislature in country.get('legislatures', []):
                                legislature_name = legislature.get('name', '')
                                
                                # Get persons data if available
                                persons_url = legislature.get('persons')
                                if persons_url:
                                    try:
                                        async with session.get(persons_url) as persons_response:
                                            if persons_response.status == 200:
                                                persons_data = await persons_response.json()
                                                
                                                for person in persons_data.get('persons', [])[:20]:  # Limit
                                                    pep_entries.append({
                                                        'id': f"EP_{person.get('id', '')}",
                                                        'name': person.get('name', ''),
                                                        'country': country_name,
                                                        'position': legislature_name,
                                                        'source': 'everypolitician',
                                                        'last_updated': datetime.now().isoformat()
                                                    })
                                    except Exception as e:
                                        logger.error(f"Error fetching persons data: {e}")
                                        continue
                        
                        logger.info(f"Fetched {len(pep_entries)} entries from EveryPolitician")
                        return pep_entries
                        
        except Exception as e:
            logger.error(f"Error fetching EveryPolitician data: {e}")
        return []
    
    async def fetch_cia_world_leaders(self):
        """Fetch world leaders data (simulated - would need proper scraping)"""
        logger.info("Fetching CIA World Leaders data...")
        
        # This is a simplified example - actual implementation would scrape the CIA website
        # For demo purposes, we'll return sample data
        sample_leaders = [
            {
                'id': 'CIA_001',
                'name': 'Sample Leader 1',
                'country': 'Sample Country',
                'position': 'President',
                'source': 'cia_world_leaders',
                'last_updated': datetime.now().isoformat()
            }
        ]
        
        return sample_leaders
    
    def merge_pep_entries(self, new_entries: List[Dict]):
        """Merge new PEP entries with existing database"""
        existing_ids = {pep.get('id') for pep in self.database['peps']}
        
        added_count = 0
        updated_count = 0
        
        for entry in new_entries:
            entry_id = entry.get('id')
            
            if not entry_id:
                # Generate ID if missing
                entry_id = f"{entry.get('source', 'unknown')}_{hash(entry.get('name', ''))}"
                entry['id'] = entry_id
            
            if entry_id in existing_ids:
                # Update existing entry
                for i, existing in enumerate(self.database['peps']):
                    if existing.get('id') == entry_id:
                        self.database['peps'][i].update(entry)
                        updated_count += 1
                        break
            else:
                # Add new entry
                self.database['peps'].append(entry)
                added_count += 1
        
        logger.info(f"Added {added_count} new entries, updated {updated_count} existing entries")
    
    async def update_from_all_sources(self):
        """Update database from all configured sources"""
        logger.info("Starting comprehensive PEP database update...")
        
        all_entries = []
        
        # Fetch from EveryPolitician
        everypolitician_data = await self.fetch_everypolitician_data()
        all_entries.extend(everypolitician_data)
        
        # Fetch from CIA World Leaders (simulated)
        cia_data = await self.fetch_cia_world_leaders()
        all_entries.extend(cia_data)
        
        # Update sources list
        self.database['sources'] = [
            {
                'name': source_info['name'],
                'url': source_info.get('url', ''),
                'last_fetched': datetime.now().isoformat()
            }
            for source_name, source_info in self.sources.items()
        ]
        
        # Merge entries
        self.merge_pep_entries(all_entries)
        
        # Save updated database
        self.save_database()
        
        logger.info("Database update completed")
    
    def search_database(self, name: str, fuzzy: bool = True) -> List[Dict]:
        """Search the local database for a name"""
        results = []
        name_lower = name.lower()
        
        for pep in self.database.get('peps', []):
            pep_name = pep.get('name', '').lower()
            
            if fuzzy:
                # Fuzzy matching
                if name_lower in pep_name or pep_name in name_lower:
                    results.append(pep)
                elif any(part in pep_name for part in name_lower.split()):
                    results.append(pep)
            else:
                # Exact matching
                if name_lower == pep_name:
                    results.append(pep)
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        stats = {
            'total_entries': len(self.database.get('peps', [])),
            'sources': len(self.database.get('sources', [])),
            'last_updated': self.database.get('last_updated', 'Unknown'),
            'version': self.database.get('version', 'Unknown')
        }
        
        # Count by source
        source_counts = {}
        for pep in self.database.get('peps', []):
            source = pep.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        stats['entries_by_source'] = source_counts
        
        # Count by country
        country_counts = {}
        for pep in self.database.get('peps', []):
            country = pep.get('country', 'unknown')
            country_counts[country] = country_counts.get(country, 0) + 1
        
        stats['entries_by_country'] = dict(sorted(
            country_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10])  # Top 10 countries
        
        return stats


async def main():
    """Main function"""
    print("\n🔍 PEP Database Updater")
    print("=" * 50)
    
    manager = PEPDatabaseManager()
    
    while True:
        print("\nOptions:")
        print("1. Update database from all sources")
        print("2. Search database")
        print("3. Show statistics")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            await manager.update_from_all_sources()
            
        elif choice == "2":
            name = input("Enter name to search: ").strip()
            if name:
                results = manager.search_database(name)
                print(f"\nFound {len(results)} matches:")
                for result in results[:5]:
                    print(f"- {result.get('name')} ({result.get('country')}) - {result.get('position')}")
            
        elif choice == "3":
            stats = manager.get_statistics()
            print("\n📊 Database Statistics:")
            print(f"Total entries: {stats['total_entries']}")
            print(f"Sources: {stats['sources']}")
            print(f"Last updated: {stats['last_updated']}")
            print(f"Version: {stats['version']}")
            
            if stats['entries_by_source']:
                print("\nEntries by source:")
                for source, count in stats['entries_by_source'].items():
                    print(f"  - {source}: {count}")
            
            if stats['entries_by_country']:
                print("\nTop countries:")
                for country, count in stats['entries_by_country'].items():
                    print(f"  - {country}: {count}")
        
        elif choice == "4":
            print("Exiting...")
            break
        
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    asyncio.run(main())
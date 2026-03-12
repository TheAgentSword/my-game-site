#!/usr/bin/env python3
"""
Free Games Scraper & Manager
Finds free, open-source games from legitimate sources and adds them to your repo
"""

import os
import subprocess
import json
import csv
import re
from pathlib import Path
from datetime import datetime
import urllib.request
from urllib.error import URLError

class FreeGamesScraper:
    def __init__(self):
        self.games = []
        self.sources = {
            'itch.io': self.scrape_itch_io,
            'github': self.scrape_github_games,
            'open-source': self.scrape_open_source,
        }
    
    def scrape_itch_io(self):
        """Scrape free games from itch.io"""
        print("\n🎮 Scraping itch.io for free games...\n")
        
        games = []
        
        # itch.io free games
        free_game_tags = [
            'https://itch.io/games/free',
            'https://itch.io/games/made-with-javascript',
            'https://itch.io/games/html5',
        ]
        
        for url in free_game_tags:
            try:
                print(f"Fetching {url}...")
                headers = {'User-Agent': 'Mozilla/5.0'}
                req = urllib.request.Request(url, headers=headers)
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    html = response.read().decode('utf-8')
                    
                    # Extract game links from itch.io
                    pattern = r'href="(https://[^"]*\.itch\.io/[^"]*)"[^>]*>([^<]+)<'
                    matches = re.findall(pattern, html)
                    
                    for link, title in matches:
                        if title.strip():
                            games.append({
                                'name': title.strip(),
                                'link': link.strip(),
                                'source': 'itch.io',
                                'type': 'free-game',
                                'date_found': datetime.now().isoformat()
                            })
                            print(f"  ✓ Found: {title.strip()}")
            except Exception as e:
                print(f"  ✗ Error: {e}")
        
        print(f"\n✓ Found {len(games)} games on itch.io")
        return games
    
    def scrape_github_games(self):
        """Scrape free games from GitHub"""
        print("\n🎮 Scraping GitHub for free games...\n")
        
        games = []
        
        # GitHub game topics/search
        search_queries = [
            'awesome-games',
            'game-development',
            'html5-games',
            'javascript-games',
        ]
        
        for query in search_queries:
            try:
                url = f"https://github.com/search?q={query}&type=repositories"
                print(f"Searching GitHub for '{query}'...")
                
                headers = {'User-Agent': 'Mozilla/5.0'}
                req = urllib.request.Request(url, headers=headers)
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    html = response.read().decode('utf-8')
                    
                    # Extract GitHub repo links
                    pattern = r'href="(/[^/]+/[^"]+)"[^>]*>([^<]+)<'
                    matches = re.findall(pattern, html)
                    
                    for repo_path, title in matches:
                        if 'github.com' not in repo_path and title.strip():
                            games.append({
                                'name': title.strip(),
                                'link': f"https://github.com{repo_path}",
                                'source': 'github',
                                'type': 'open-source',
                                'date_found': datetime.now().isoformat()
                            })
                            print(f"  ✓ Found: {title.strip()}")
            except Exception as e:
                print(f"  ✗ Error: {e}")
        
        print(f"\n✓ Found {len(games)} games on GitHub")
        return games
    
    def scrape_open_source(self):
        """Scrape from open-source game sites"""
        print("\n🎮 Scraping open-source game sites...\n")
        
        games = []
        
        open_source_sources = [
            {
                'name': 'OpenGameArt',
                'url': 'https://opengameart.org/art-search?keys=game&field_art_type_tid%5B%5D=13',
                'pattern': r'href="([^"]*)"[^>]*>([^<]+)</a>'
            },
            {
                'name': 'LibreGames',
                'url': 'https://libregames.org/',
                'pattern': r'<a href="([^"]+)"[^>]*>([^<]+)</a>'
            },
        ]
        
        for source in open_source_sources:
            try:
                print(f"Fetching {source['name']}...")
                headers = {'User-Agent': 'Mozilla/5.0'}
                req = urllib.request.Request(source['url'], headers=headers)
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    html = response.read().decode('utf-8')
                    
                    matches = re.findall(source['pattern'], html)
                    
                    for link, title in matches:
                        if title.strip() and ('game' in title.lower() or 'play' in title.lower()):
                            games.append({
                                'name': title.strip(),
                                'link': link.strip(),
                                'source': source['name'],
                                'type': 'open-source',
                                'date_found': datetime.now().isoformat()
                            })
                            print(f"  ✓ Found: {title.strip()}")
            except Exception as e:
                print(f"  ✗ Error fetching {source['name']}: {e}")
        
        print(f"\n✓ Found {len(games)} open-source games")
        return games
    
    def run_all_scrapers(self):
        """Run all scrapers"""
        print("=" * 60)
        print("🎮 Free Games Scraper")
        print("=" * 60)
        
        all_games = []
        
        for source_name, scraper_func in self.sources.items():
            try:
                games = scraper_func()
                all_games.extend(games)
            except Exception as e:
                print(f"\n✗ Error with {source_name}: {e}")
        
        return all_games
    
    def remove_duplicates(self, games):
        """Remove duplicate games"""
        seen = set()
        unique_games = []
        
        for game in games:
            key = game['name'].lower()
            if key not in seen:
                unique_games.append(game)
                seen.add(key)
        
        return unique_games
    
    def save_results(self, games, output_dir='/mnt/user-data/outputs'):
        """Save scraped games"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Remove duplicates
        games = self.remove_duplicates(games)
        
        print(f"\n✓ Total unique games found: {len(games)}\n")
        
        # Save as JSON
        json_file = f"{output_dir}/free_games.json"
        with open(json_file, 'w') as f:
            json.dump(games, f, indent=2)
        print(f"✓ Saved to {json_file}")
        
        # Save as CSV
        csv_file = f"{output_dir}/free_games.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'link', 'source', 'type', 'date_found'])
            writer.writeheader()
            writer.writerows(games)
        print(f"✓ Saved to {csv_file}")
        
        # Save as Markdown
        md_file = f"{output_dir}/free_games.md"
        with open(md_file, 'w') as f:
            f.write("# Free & Open-Source Games Collection\n\n")
            f.write(f"**Total Games:** {len(games)}\n")
            f.write(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Group by source
            sources = {}
            for game in games:
                source = game.get('source', 'Unknown')
                if source not in sources:
                    sources[source] = []
                sources[source].append(game)
            
            for source, source_games in sorted(sources.items()):
                f.write(f"## {source} ({len(source_games)} games)\n\n")
                for game in source_games:
                    f.write(f"- [{game['name']}]({game['link']})\n")
                f.write("\n")
        
        print(f"✓ Saved to {md_file}")
        
        return games


class GameCollector:
    def __init__(self, storage_file='free_games.json'):
        self.storage_file = storage_file
        self.games = self.load_games()
    
    def load_games(self):
        """Load games from storage"""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_games(self):
        """Save games"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.games, f, indent=2)
        print(f"✓ Saved {len(self.games)} games")
    
    def add_game(self, name, link, source='manual'):
        """Add a game"""
        if any(g['name'].lower() == name.lower() for g in self.games):
            print(f"⚠ Game '{name}' already exists!")
            return False
        
        self.games.append({
            'name': name.strip(),
            'link': link.strip(),
            'source': source,
            'date_added': datetime.now().isoformat()
        })
        print(f"✓ Added: {name}")
        return True
    
    def list_games(self):
        """List all games"""
        if not self.games:
            print("No games yet!")
            return
        
        print(f"\n📋 Games ({len(self.games)} total):\n")
        for i, game in enumerate(self.games, 1):
            print(f"{i}. {game['name']}")
            print(f"   Source: {game.get('source', 'Unknown')}")
            print(f"   Link: {game['link']}\n")
    
    def run_interactive(self):
        """Interactive menu"""
        while True:
            print("\n" + "="*50)
            print("🎮 Free Games Manager")
            print("="*50)
            print("\n1. Add a game")
            print("2. List all games")
            print("3. Save & Exit")
            print("0. Exit")
            
            choice = input("\nChoice: ").strip()
            
            if choice == '1':
                name = input("Game name: ").strip()
                link = input("Game link: ").strip()
                if name and link:
                    self.add_game(name, link)
            
            elif choice == '2':
                self.list_games()
            
            elif choice == '3':
                self.save_games()
                print("Exiting...")
                break
            
            elif choice == '0':
                print("Exiting without saving...")
                break


def main():
    """Main menu"""
    while True:
        print("\n" + "=" * 60)
        print("🎮 Free Games Suite")
        print("=" * 60)
        print("\n1. Scrape free games from the web")
        print("2. Manually add games")
        print("0. Exit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            scraper = FreeGamesScraper()
            games = scraper.run_all_scrapers()
            scraper.save_results(games)
            
            print("\n" + "=" * 60)
            print("✓ SCRAPING COMPLETE!")
            print("=" * 60)
            print("\nGames saved to:")
            print("  - free_games.json")
            print("  - free_games.csv")
            print("  - free_games.md")
        
        elif choice == '2':
            collector = GameCollector()
            collector.run_interactive()
        
        elif choice == '0':
            print("Goodbye! 👋")
            break


if __name__ == "__main__":
    main()

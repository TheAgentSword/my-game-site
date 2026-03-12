#!/usr/bin/env python3
"""
GN-Math Games Management Suite
Complete tool for syncing, collecting, and extracting games
"""

import os
import subprocess
import json
import csv
import shutil
import re
from pathlib import Path
from datetime import datetime

class GamesSyncManager:
    def __init__(self, github_username="TheAgentSword", repo_name="my-game-site"):
        self.github_username = github_username
        self.repo_name = repo_name
        self.user_repo_url = f"https://github.com/{github_username}/{repo_name}.git"
        self.gn_math_repo = "https://github.com/gn-math/gn-math.github.io.git"
        
        self.work_dir = Path("/home/claude/games_sync")
        self.gn_math_dir = self.work_dir / "gn-math-source"
        self.user_repo_dir = self.work_dir / repo_name
        
        self.games_list = []
    
    def setup_directories(self):
        """Create necessary directories"""
        print("📁 Setting up directories...\n")
        self.work_dir.mkdir(exist_ok=True)
        print(f"✓ Working directory: {self.work_dir}")
    
    def clone_gn_math(self):
        """Clone GN-Math repository"""
        print("\n📥 Cloning GN-Math repository...\n")
        
        if self.gn_math_dir.exists():
            print(f"⚠ GN-Math source already exists, using existing copy")
            return True
        
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", self.gn_math_repo, str(self.gn_math_dir)],
                check=True,
                capture_output=True,
                timeout=300
            )
            print(f"✓ Cloned GN-Math to {self.gn_math_dir}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to clone GN-Math: {e}")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def clone_user_repo(self):
        """Clone your private repository"""
        print("\n📥 Cloning your private repository...\n")
        
        if self.user_repo_dir.exists():
            print(f"⚠ User repo already exists at {self.user_repo_dir}")
            return True
        
        try:
            subprocess.run(
                ["git", "clone", self.user_repo_url, str(self.user_repo_dir)],
                check=True,
                capture_output=True,
                timeout=300
            )
            print(f"✓ Cloned your repo to {self.user_repo_dir}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to clone your repo")
            print(f"Make sure:")
            print(f"  1. The repo URL is correct: {self.user_repo_url}")
            print(f"  2. You have access to this repo")
            print(f"  3. Git is configured with your GitHub credentials")
            print(f"\nTo set up credentials:")
            print(f"  git config --global user.name 'Your Name'")
            print(f"  git config --global user.email 'your@email.com'")
            print(f"\nOr use a Personal Access Token:")
            print(f"  git clone https://YOUR_USERNAME:YOUR_TOKEN@github.com/{self.github_username}/{self.repo_name}.git")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def find_games(self):
        """Find all games in GN-Math"""
        print("\n🎮 Scanning for games...\n")
        
        games_dir = self.gn_math_dir / "games"
        if not games_dir.exists():
            print(f"⚠ Games directory not found at {games_dir}")
            print("Checking alternative locations...")
            
            alt_paths = [
                self.gn_math_dir / "game",
                self.gn_math_dir / "src" / "games",
            ]
            
            for alt_path in alt_paths:
                if alt_path.exists():
                    games_dir = alt_path
                    break
            
            if not games_dir.exists():
                print("✗ Could not find games directory")
                return []
        
        games = []
        for game_folder in sorted(games_dir.iterdir()):
            if game_folder.is_dir() and not game_folder.name.startswith('.'):
                games.append(game_folder)
                print(f"  ✓ Found: {game_folder.name}")
        
        print(f"\n✓ Found {len(games)} games total\n")
        self.games_list = games
        return games
    
    def copy_games(self):
        """Copy all games to your repo"""
        print("\n📋 Copying games to your repository...\n")
        
        target_dir = self.user_repo_dir / "games"
        target_dir.mkdir(exist_ok=True)
        
        copied = 0
        failed = 0
        
        for game_dir in self.games_list:
            game_name = game_dir.name
            target_path = target_dir / game_name
            
            try:
                if target_path.exists():
                    print(f"⚠ {game_name} already exists, skipping")
                    continue
                
                shutil.copytree(game_dir, target_path)
                print(f"✓ Copied: {game_name}")
                copied += 1
            except Exception as e:
                print(f"✗ Failed to copy {game_name}: {e}")
                failed += 1
        
        print(f"\n✓ Copied {copied} games")
        if failed > 0:
            print(f"⚠ Failed to copy {failed} games")
        
        return copied, failed
    
    def create_metadata(self):
        """Create metadata files"""
        print("\n📝 Creating metadata files...\n")
        
        games_data = []
        games_dir = self.user_repo_dir / "games"
        
        for game_folder in sorted(games_dir.iterdir()):
            if game_folder.is_dir() and not game_folder.name.startswith('.'):
                games_data.append({
                    "name": game_folder.name.replace('-', ' ').title(),
                    "folder": game_folder.name,
                    "link": f"./games/{game_folder.name}/",
                    "date_added": datetime.now().isoformat()
                })
        
        json_file = self.user_repo_dir / "games.json"
        with open(json_file, 'w') as f:
            json.dump(games_data, f, indent=2)
        print(f"✓ Created: games.json ({len(games_data)} games)")
        
        readme_file = self.user_repo_dir / "GAMES.md"
        with open(readme_file, 'w') as f:
            f.write("# Game Collection\n\n")
            f.write(f"**Total Games:** {len(games_data)}\n")
            f.write(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Games List\n\n")
            
            for game in games_data:
                f.write(f"- **{game['name']}** - `{game['folder']}`\n")
        
        print(f"✓ Created: GAMES.md")
    
    def commit_and_push(self):
        """Commit and push changes to your repo"""
        print("\n🚀 Committing and pushing to GitHub...\n")
        
        try:
            os.chdir(self.user_repo_dir)
            
            print("Adding files to git...")
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            
            commit_msg = f"Add GN-Math games collection - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            print(f"Committing: {commit_msg}")
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                check=True,
                capture_output=True
            )
            
            print("Pushing to GitHub...")
            subprocess.run(
                ["git", "push", "origin", "main"],
                check=True,
                capture_output=True,
                timeout=300
            )
            
            print(f"✓ Successfully pushed to GitHub!")
            print(f"✓ View your repo: {self.user_repo_url}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Git operation failed")
            print(f"Error: {e.stderr.decode() if e.stderr else str(e)}")
            
            print("\n💡 Troubleshooting:")
            print("1. Make sure you're authenticated with GitHub")
            print("2. Check that you have push permissions")
            print("3. Verify the default branch is 'main' (not 'master')")
            
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def run(self):
        """Run the complete sync process"""
        print("=" * 60)
        print("🎮 GN-Math Games Sync Manager")
        print("=" * 60)
        print(f"\nTarget Repository: {self.user_repo_url}")
        print(f"Working Directory: {self.work_dir}\n")
        
        self.setup_directories()
        
        if not self.clone_gn_math():
            print("\n✗ Failed to clone GN-Math")
            return False
        
        if not self.clone_user_repo():
            print("\n✗ Failed to clone your repository")
            return False
        
        if not self.find_games():
            print("\n✗ No games found")
            return False
        
        copied, failed = self.copy_games()
        if copied == 0:
            print("\n⚠ No games were copied")
            return False
        
        self.create_metadata()
        
        if not self.commit_and_push():
            print("\n⚠ Sync completed but push failed")
            print("You can manually push from:", self.user_repo_dir)
            return False
        
        print("\n" + "=" * 60)
        print("✓ SYNC COMPLETE!")
        print("=" * 60)
        print(f"\n✓ {copied} games added to your private repository")
        print(f"✓ Repository: {self.user_repo_url}")
        print(f"✓ Local copy: {self.user_repo_dir}")
        
        return True


class GameCollector:
    def __init__(self, storage_file='games_data.json'):
        self.storage_file = storage_file
        self.games = self.load_games()
    
    def load_games(self):
        """Load existing games from storage"""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_games(self):
        """Save games to storage"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.games, f, indent=2)
        print(f"✓ Saved {len(self.games)} games to {self.storage_file}")
    
    def add_game(self, name, link):
        """Add a single game"""
        if any(g['name'].lower() == name.lower() for g in self.games):
            print(f"⚠ Game '{name}' already exists!")
            return False
        
        self.games.append({
            'name': name.strip(),
            'link': link.strip(),
            'added_date': datetime.now().isoformat()
        })
        print(f"✓ Added: {name}")
        return True
    
    def remove_game(self, name):
        """Remove a game by name"""
        original_count = len(self.games)
        self.games = [g for g in self.games if g['name'].lower() != name.lower()]
        if len(self.games) < original_count:
            print(f"✓ Removed: {name}")
            return True
        print(f"✗ Game '{name}' not found")
        return False
    
    def list_games(self):
        """Display all games"""
        if not self.games:
            print("No games collected yet!")
            return
        
        print(f"\n📋 Collected Games ({len(self.games)} total):\n")
        for i, game in enumerate(self.games, 1):
            print(f"{i:3d}. {game['name']}")
            print(f"      → {game['link']}\n")
    
    def search_games(self, query):
        """Search for games by name"""
        results = [g for g in self.games if query.lower() in g['name'].lower()]
        if not results:
            print(f"No games found matching '{query}'")
            return
        
        print(f"\n🔍 Search results for '{query}':\n")
        for game in results:
            print(f"- {game['name']}")
            print(f"  {game['link']}\n")
    
    def export_json(self, filename='games.json'):
        """Export to JSON"""
        with open(filename, 'w') as f:
            json.dump(self.games, f, indent=2)
        print(f"✓ Exported to {filename}")
    
    def export_csv(self, filename='games.csv'):
        """Export to CSV"""
        if not self.games:
            print("No games to export!")
            return
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'link', 'added_date'])
            writer.writeheader()
            writer.writerows(self.games)
        print(f"✓ Exported to {filename}")
    
    def export_markdown(self, filename='games.md'):
        """Export to Markdown"""
        if not self.games:
            print("No games to export!")
            return
        
        with open(filename, 'w') as f:
            f.write("# GN-Math Games Collection\n\n")
            f.write(f"**Total Games:** {len(self.games)}\n")
            f.write(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for game in self.games:
                f.write(f"- [{game['name']}]({game['link']})\n")
        
        print(f"✓ Exported to {filename}")
    
    def run_interactive(self):
        """Run interactive menu"""
        while True:
            print("\n" + "="*50)
            print("🎮 GN-Math Game Collector")
            print("="*50)
            print("\nOptions:")
            print("  1. Add a game")
            print("  2. Remove a game")
            print("  3. List all games")
            print("  4. Search games")
            print("  5. Export to JSON")
            print("  6. Export to CSV")
            print("  7. Export to Markdown")
            print("  8. Save & Exit")
            print("  0. Exit without saving")
            
            choice = input("\nChoice (0-8): ").strip()
            
            if choice == '1':
                name = input("Game name: ").strip()
                link = input("Game link: ").strip()
                if name and link:
                    self.add_game(name, link)
                else:
                    print("✗ Name and link required!")
            
            elif choice == '2':
                name = input("Game name to remove: ").strip()
                if name:
                    self.remove_game(name)
            
            elif choice == '3':
                self.list_games()
            
            elif choice == '4':
                query = input("Search for: ").strip()
                if query:
                    self.search_games(query)
            
            elif choice == '5':
                self.export_json()
            
            elif choice == '6':
                self.export_csv()
            
            elif choice == '7':
                self.export_markdown()
            
            elif choice == '8':
                self.save_games()
                print("✓ Saved! Exiting...")
                break
            
            elif choice == '0':
                print("Exiting without saving...")
                break
            
            else:
                print("Invalid choice!")


class GamesExtractor:
    def extract_games_from_html(self, html_content):
        """Extract game links and titles from HTML content"""
        games = []
        
        pattern1 = r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>'
        matches = re.findall(pattern1, html_content)
        
        for href, text in matches:
            if text.strip() and not any(skip in text.lower() for skip in ['dmca', 'contact', 'privacy', 'github']):
                games.append({
                    'name': text.strip(),
                    'link': href.strip()
                })
        
        return games
    
    def extract_from_readme(self, readme_content):
        """Extract games from README markdown format"""
        games = []
        
        pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        matches = re.findall(pattern, readme_content)
        
        for title, url in matches:
            if title.strip() and url.strip():
                games.append({
                    'name': title.strip(),
                    'link': url.strip()
                })
        
        return games
    
    def fetch_github_raw(self, repo_owner, repo_name, file_path, branch='main'):
        """Fetch raw file from GitHub"""
        url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}/{file_path}"
        try:
            import urllib.request
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            print(f"Error fetching {file_path}: {e}")
            return None
    
    def save_results(self, games, output_dir='/mnt/user-data/outputs'):
        """Save games to JSON, CSV, and Markdown"""
        unique_games = []
        seen = set()
        for game in games:
            key = (game['name'].lower(), game['link'].lower())
            if key not in seen:
                unique_games.append(game)
                seen.add(key)
        
        print(f"\n✓ Found {len(unique_games)} unique games\n")
        
        json_file = f"{output_dir}/games.json"
        with open(json_file, 'w') as f:
            json.dump(unique_games, f, indent=2)
        print(f"✓ Saved to {json_file}")
        
        csv_file = f"{output_dir}/games.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'link'])
            writer.writeheader()
            writer.writerows(unique_games)
        print(f"✓ Saved to {csv_file}")
        
        md_file = f"{output_dir}/games.md"
        with open(md_file, 'w') as f:
            f.write("# GN-Math Games Collection\n\n")
            f.write(f"**Total Games:** {len(unique_games)}\n\n")
            for game in unique_games:
                f.write(f"- [{game['name']}]({game['link']})\n")
        print(f"✓ Saved to {md_file}")
        
        return unique_games
    
    def run(self):
        """Run the extractor"""
        print("🎮 GN-Math Games Extractor\n")
        print("Fetching data from GitHub...\n")
        
        games = []
        
        files_to_try = [
            ('index.html', 'HTML index'),
            ('README.md', 'README'),
            ('games.json', 'Games JSON'),
            ('data.json', 'Data JSON'),
            ('games/index.html', 'Games folder'),
        ]
        
        for file_path, description in files_to_try:
            print(f"Trying {description} ({file_path})...")
            content = self.fetch_github_raw('gn-math', 'gn-math.github.io', file_path)
            
            if content:
                print(f"  ✓ Found!")
                
                if file_path.endswith('.md'):
                    games.extend(self.extract_from_readme(content))
                else:
                    games.extend(self.extract_games_from_html(content))
            else:
                print(f"  ✗ Not found")
        
        if games:
            self.save_results(games)
            print("\n✓ Done!")
            
            print("\nPreview (first 10 games):")
            for i, game in enumerate(games[:10], 1):
                print(f"\n{i}. {game['name']}")
                print(f"   {game['link']}")
        else:
            print("\n✗ No games found in fetched files")
            print("\nManual approach:")
            print("1. Visit: https://github.com/gn-math/gn-math.github.io")
            print("2. Look at the repository structure")
            print("3. Edit the script with the correct file paths")


def main():
    """Main menu"""
    import sys
    
    while True:
        print("\n" + "=" * 60)
        print("🎮 GN-Math Games Management Suite")
        print("=" * 60)
        print("\nChoose an option:")
        print("  1. Sync GN-Math games to your private GitHub repo")
        print("  2. Manually collect games (interactive)")
        print("  3. Extract games from GitHub")
        print("  0. Exit")
        
        choice = input("\nChoice (0-3): ").strip()
        
        if choice == '1':
            github_username = input("GitHub username (default: TheAgentSword): ").strip() or "TheAgentSword"
            repo_name = input("Repository name (default: my-game-site): ").strip() or "my-game-site"
            
            manager = GamesSyncManager(github_username, repo_name)
            manager.run()
        
        elif choice == '2':
            storage_file = input("Storage file (default: games_data.json): ").strip() or "games_data.json"
            collector = GameCollector(storage_file)
            collector.run_interactive()
        
        elif choice == '3':
            extractor = GamesExtractor()
            extractor.run()
        
        elif choice == '0':
            print("Goodbye! 👋")
            break
        
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()

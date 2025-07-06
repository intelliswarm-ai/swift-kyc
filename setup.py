"""
Setup script for KYC Analysis CrewAI
"""
import os
import json
from datetime import datetime


def create_sample_databases():
    """Create sample PEP and sanctions databases"""
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Sample PEP database
    pep_database = {
        "version": "2.0",
        "last_updated": datetime.now().isoformat(),
        "peps": [
            {
                "id": "PEP001",
                "name": "Angela Merkel",
                "aliases": ["A. Merkel", "Angela Dorothea Merkel"],
                "date_of_birth": "1954-07-17",
                "nationality": "Germany",
                "positions": [
                    {
                        "title": "Chancellor of Germany",
                        "country": "Germany",
                        "start_date": "2005-11-22",
                        "end_date": "2021-12-08",
                        "current": False
                    }
                ],
                "family_members": [
                    {"name": "Joachim Sauer", "relationship": "Spouse"}
                ],
                "risk_level": "High",
                "last_updated": "2024-01-15"
            },
            {
                "id": "PEP002",
                "name": "Emmanuel Macron",
                "aliases": ["E. Macron"],
                "date_of_birth": "1977-12-21",
                "nationality": "France",
                "positions": [
                    {
                        "title": "President of France",
                        "country": "France",
                        "start_date": "2017-05-14",
                        "end_date": None,
                        "current": True
                    }
                ],
                "family_members": [
                    {"name": "Brigitte Macron", "relationship": "Spouse"}
                ],
                "risk_level": "High",
                "last_updated": "2024-01-15"
            },
            {
                "id": "PEP003",
                "name": "Xi Jinping",
                "aliases": ["Xi Jin-ping"],
                "date_of_birth": "1953-06-15",
                "nationality": "China",
                "positions": [
                    {
                        "title": "President of China",
                        "country": "China",
                        "start_date": "2013-03-14",
                        "end_date": None,
                        "current": True
                    }
                ],
                "family_members": [
                    {"name": "Peng Liyuan", "relationship": "Spouse"}
                ],
                "risk_level": "High",
                "last_updated": "2024-01-15"
            }
        ]
    }
    
    # Sample sanctions database
    sanctions_database = {
        "version": "2.0",
        "last_updated": datetime.now().isoformat(),
        "lists": {
            "OFAC": {
                "entries": [
                    {
                        "id": "OFAC-001",
                        "name": "Cyber Criminal Organization LLC",
                        "type": "entity",
                        "aliases": ["CCO LLC", "Cyber Crim Org"],
                        "sanctions_program": "CYBER2",
                        "listing_date": "2023-06-15",
                        "country": "Russia",
                        "additional_info": "Ransomware operations"
                    },
                    {
                        "id": "OFAC-002",
                        "name": "Vladimir Petrov",
                        "type": "individual",
                        "date_of_birth": "1975-03-10",
                        "sanctions_program": "UKRAINE-EO14024",
                        "listing_date": "2022-02-25",
                        "nationality": "Russia",
                        "additional_info": "Oligarch"
                    }
                ],
                "last_updated": "2024-01-20"
            },
            "EU": {
                "entries": [
                    {
                        "id": "EU-001",
                        "name": "Arms Trading International",
                        "type": "entity",
                        "sanctions_program": "Arms Embargo",
                        "listing_date": "2023-01-15",
                        "country": "Iran",
                        "additional_info": "Weapons trafficking"
                    }
                ],
                "last_updated": "2024-01-18"
            },
            "SECO": {
                "entries": [
                    {
                        "id": "SECO-001",
                        "name": "Money Laundering Services AG",
                        "type": "entity",
                        "sanctions_program": "ML/TF",
                        "listing_date": "2023-09-01",
                        "country": "Switzerland",
                        "additional_info": "Financial crimes"
                    }
                ],
                "last_updated": "2024-01-19"
            },
            "UN": {
                "entries": [
                    {
                        "id": "UN-001",
                        "name": "Terror Finance Network",
                        "type": "entity",
                        "sanctions_program": "ISIL and Al-Qaida",
                        "listing_date": "2022-11-30",
                        "additional_info": "Terrorist financing"
                    }
                ],
                "last_updated": "2024-01-17"
            }
        }
    }
    
    # Save databases
    with open('data/pep_database.json', 'w') as f:
        json.dump(pep_database, f, indent=2)
    
    with open('data/sanctions_lists.json', 'w') as f:
        json.dump(sanctions_database, f, indent=2)
    
    print("✅ Sample databases created successfully!")


def setup_environment():
    """Setup the environment for KYC Analysis"""
    
    print("🔧 Setting up KYC Analysis Environment...")
    print("-" * 50)
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("⚠️  No .env file found. Creating from .env.example...")
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as src, open('.env', 'w') as dst:
                dst.write(src.read())
            print("✅ .env file created. Please add your API keys.")
        else:
            print("❌ .env.example not found!")
    else:
        print("✅ .env file exists")
    
    # Create directories
    directories = ['data', 'reports', 'logs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}/")
    
    # Create sample databases
    create_sample_databases()
    
    # Create .gitignore
    gitignore_content = """
# Environment variables
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Reports and logs
reports/*.json
logs/*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.bak
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content.strip())
    print("✅ Created .gitignore file")
    
    print("\n📋 Setup Complete!")
    print("-" * 50)
    print("Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Install Playwright browsers: playwright install chromium")
    print("3. Run example: python example_usage.py")
    print("4. Or run main: python main.py")


if __name__ == "__main__":
    setup_environment()
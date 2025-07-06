#!/usr/bin/env python3
"""
Clean up irrelevant files from the project
Removes test files, CrewAI-related files, and temporary files
"""
import os
import shutil
import json
from datetime import datetime


def cleanup_project():
    """Remove irrelevant files and create cleanup summary"""
    
    print("🧹 Cleaning up project files...")
    print("=" * 60)
    
    # Files to remove
    files_to_remove = [
        # Test files
        "test_ollama.py",
        "test_ollama_windows.py",
        "test_wsl_ips.py",
        
        # CrewAI-related files
        "setup_crewai_ollama.py",
        "kyc_direct.py",  # Direct implementation without framework
        "example_usage.py",  # Old example file
        
        # Diagnostic/debug files
        "diagnose_ollama_connection.py",
        "check_versions.py",
        "find_windows_ip.py",
        
        # Old main versions
        "main_fixed.py",
        "main_simple.py",
        "main_mistral.py",
        
        # Setup scripts (keeping only essential ones)
        "ollama_setup.py",
        "start_ollama_windows.bat",
        "start_ollama_windows.ps1",
        
        # Redundant documentation
        "WSL_SETUP_GUIDE.md",
        "PROJECT_SUMMARY.md",  # Old summary
        
        # Old cleanup script
        "cleanup_and_reorganize.py",
        
        # Enhanced/Modern/Simple implementations (keeping only Interactive)
        "kyc_enhanced.py",
        "kyc_modern.py", 
        "kyc_simple.py",
        
        # Data files that should be in data directory
        "pep_database.json",
    ]
    
    # Archive directory for backup
    archive_dir = "archive_cleanup"
    os.makedirs(archive_dir, exist_ok=True)
    
    removed_files = []
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                # Move to archive instead of deleting
                shutil.move(file, os.path.join(archive_dir, file))
                removed_files.append(file)
                print(f"  ✓ Archived: {file}")
            except Exception as e:
                print(f"  ✗ Error moving {file}: {e}")
    
    # Special handling for venv directory
    if os.path.exists("venv"):
        print("\n⚠️  Virtual environment directory 'venv' found")
        print("   This should not be in version control")
        print("   Add 'venv/' to .gitignore if not already present")
    
    # Create/update .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
archive_*/
logs/
reports/
data/
*.log
.env
*.bak

# Streamlit
.streamlit/
"""
    
    with open(".gitignore", 'w') as f:
        f.write(gitignore_content)
    print("\n✓ Updated .gitignore")
    
    # Create project structure summary
    kept_files = {
        "Core Files": [
            "main.py - Main entry point",
            "kyc_interactive.py - Interactive KYC analysis",
            "requirements.txt - Python dependencies"
        ],
        "Web UI": [
            "streamlit_app.py - Main web UI",
            "streamlit_interactive.py - Advanced interactive UI",
            "run_ui.bat - Windows UI launcher",
            "run_ui.sh - Linux/Mac UI launcher"
        ],
        "Tools": [
            "tools/ - Simple tools directory",
            "tools_langchain/ - Enhanced LangChain tools"
        ],
        "Agents & Chains": [
            "agents/ - LangChain agents",
            "chains/ - Workflow chains"
        ],
        "Documentation": [
            "README.md - Main documentation",
            "UI_README.md - UI documentation",
            "INTERACTIVE_KYC_GUIDE.md - Interactive system guide",
            "CLEANUP_SUMMARY.json - Previous cleanup summary"
        ],
        "Configuration": [
            ".env.example - Environment variables template",
            ".gitignore - Git ignore file"
        ]
    }
    
    # Create cleanup summary
    summary = {
        "cleanup_date": datetime.now().isoformat(),
        "files_removed": len(removed_files),
        "files_archived_to": archive_dir,
        "removed_files": removed_files,
        "project_structure": kept_files,
        "next_steps": [
            "Run 'pip install -r requirements.txt' to install dependencies",
            "Run 'python main.py' for command line interface",
            "Run 'streamlit run streamlit_app.py' for web UI",
            "Ensure Ollama is running before use"
        ]
    }
    
    with open("CLEANUP_PROJECT_SUMMARY.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Cleanup complete!")
    print(f"   - Removed {len(removed_files)} files")
    print(f"   - Files archived to '{archive_dir}/'")
    print(f"   - Summary saved to 'CLEANUP_PROJECT_SUMMARY.json'")
    print("\n📁 Current project structure focuses on:")
    print("   - Interactive KYC analysis")
    print("   - Web UI interface")
    print("   - LangChain implementation")
    print("   - Local processing with Ollama")


if __name__ == "__main__":
    cleanup_project()
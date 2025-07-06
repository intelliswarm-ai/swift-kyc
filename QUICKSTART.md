# KYC Analysis System - Quick Start Guide

## Overview
This KYC (Know Your Customer) system uses CrewAI with Ollama for confidential, local AI-powered client screening.

## Prerequisites

### 1. Install Ollama
Download and install Ollama from: https://ollama.ai/download

### 2. Start Ollama Server
Open a terminal and run:
```bash
ollama serve
```
Keep this terminal open.

### 3. Install Mistral Model
In another terminal:
```bash
ollama pull mistral
```

## Installation

### 1. Create Virtual Environment
```powershell
# In PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

Or install manually:
```powershell
pip install crewai langchain langchain-community langchain-ollama
pip install python-dotenv requests beautifulsoup4 playwright pandas
```

## Running the System

### Option 1: CrewAI + Ollama (Recommended)
```powershell
python main_crewai_ollama_final.py
```

### Option 2: Direct Analysis (Fallback)
```powershell
python kyc_direct.py
```

### Option 3: Test Installation
```powershell
python test_crewai_ollama_new.py
```

## Configuration

Create a `.env` file:
```env
# Ollama Configuration
USE_OLLAMA=true
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434

# Report Output
REPORT_OUTPUT_DIR=./reports
```

## Troubleshooting

### "Ollama is not running" Error
1. Make sure Ollama server is running: `ollama serve`
2. Check if model is installed: `ollama list`
3. Install model if needed: `ollama pull mistral`

### CrewAI Errors
If CrewAI fails, the system automatically falls back to direct analysis.

### Import Errors
Reinstall packages:
```powershell
pip uninstall crewai langchain langchain-community langchain-ollama -y
pip install crewai langchain langchain-community langchain-ollama
```

## Features

1. **Multi-Agent System**:
   - Research Analyst
   - PEP Screening Specialist
   - Sanctions Compliance Officer
   - Risk Assessment Analyst
   - Compliance Report Writer

2. **Screening Tools**:
   - PEP (Politically Exposed Person) checking
   - Sanctions list screening (OFAC, EU, UN)
   - Risk assessment scoring
   - Web research capabilities

3. **Confidentiality**:
   - All processing done locally with Ollama
   - No data sent to external APIs
   - Reports saved locally

## Example Client Data

```python
client_info = {
    "name": "John Doe",
    "entity_type": "individual",
    "date_of_birth": "1980-05-15",
    "nationality": "USA",
    "residence_country": "Switzerland",
    "occupation": "Software Engineer",
    "source_of_funds": "Employment income"
}
```

## Output

Reports are saved to `./reports/` directory as JSON files with timestamp.

Example: `KYC_Report_John_Doe_20250107_143052_crewai.json`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages for specific guidance
3. Use the fallback direct analysis mode if needed
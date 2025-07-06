# KYC Analysis with CrewAI

An automated Know Your Customer (KYC) solution built on the CrewAI platform for Swiss banking compliance. This system uses AI agents to perform comprehensive due diligence on potential bank clients, including PEP screening, sanctions checks, and risk assessment.

🔒 **Privacy First**: Supports local LLM processing with Ollama to ensure complete confidentiality of client data.

## Features

- **Confidential Web Research**: Uses headless browser technology to search for client information while maintaining privacy
- **Local LLM Processing**: Run entirely offline with Ollama for maximum data security
- **Advanced PEP Screening**: 
  - Dynamic fetching from public PEP databases (OpenSanctions, EveryPolitician)
  - Real-time web search for political connections
  - News article analysis for PEP identification
  - Fuzzy name matching and alias detection
- **Sanctions Checking**: Screens against SECO, EU, OFAC, and UN sanctions lists
- **Risk Assessment**: Comprehensive risk scoring based on multiple factors
- **Automated Reporting**: Generates detailed KYC compliance reports

## Architecture

The system uses CrewAI's multi-agent architecture with specialized agents:

1. **Research Analyst**: Conducts online research using headless browsers
2. **PEP Screening Specialist**: Checks PEP databases and identifies political connections
3. **Sanctions Compliance Officer**: Screens against international sanctions lists
4. **Risk Assessment Analyst**: Calculates comprehensive risk scores
5. **Compliance Report Writer**: Compiles findings into regulatory-compliant reports

## Installation

### Prerequisites

- Python 3.8 or higher
- Ollama (for local LLM processing)

### Step 1: Install Ollama

For maximum confidentiality, we recommend using Ollama with local models:

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [https://ollama.ai/download/windows](https://ollama.ai/download/windows)

### Step 2: Pull a Model

```bash
# Start Ollama service
ollama serve

# In another terminal, pull a model (choose one):
ollama pull llama2        # 7B parameters, good balance
ollama pull mistral       # 7B parameters, faster
ollama pull mixtral       # Larger, more capable
ollama pull neural-chat   # Optimized for conversation
```

### Step 3: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd swift-kyc

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Setup environment
cp .env.example .env
python setup.py
```

## Configuration

Edit the `.env` file:

```bash
# Use Ollama for local processing (recommended)
USE_OLLAMA=true
OLLAMA_MODEL=llama2  # Choose your model
OLLAMA_BASE_URL=http://localhost:11434

# Only if you want to use OpenAI (not recommended for confidential data)
# USE_OLLAMA=false
# OPENAI_API_KEY=your_key_here
```

## Usage

### Basic Usage

```python
from main import KYCAnalysisCrew

# Client information
client_info = {
    "name": "John Doe",
    "entity_type": "individual",
    "date_of_birth": "1980-05-15",
    "nationality": "USA",
    "residence_country": "Switzerland"
}

# Run KYC analysis
kyc_crew = KYCAnalysisCrew()
result = kyc_crew.run(client_info)
```

### Command Line

```bash
# Ensure Ollama is running
ollama serve

# In another terminal
python main.py
```

### Example Usage

```bash
python example_usage.py
```

### Client Information Structure

```python
client_info = {
    # Required fields
    "name": "Full Name",
    "entity_type": "individual",  # or "corporate"
    
    # Optional fields for individuals
    "date_of_birth": "YYYY-MM-DD",
    "nationality": "Country",
    "residence_country": "Country",
    
    # Optional fields for corporates
    "registration_number": "Company number",
    "registration_country": "Country",
    "business_countries": ["Country1", "Country2"],
    
    # Additional optional fields
    "industry": "Industry sector",
    "customer_type": "Type of customer",
    "complex_structure": false,
    "offshore_elements": false
}
```

## Output

The system generates comprehensive KYC reports saved in JSON format:

```
reports/
├── KYC_Report_John_Doe_20240120_143022.json
└── KYC_Report_Company_Ltd_20240120_150511.json
```

Each report contains:
- Executive summary and recommendations
- Background research findings
- PEP screening results
- Sanctions screening results
- Risk assessment with detailed scoring
- Required documentation checklist
- Ongoing monitoring requirements

## Privacy and Security

### Using Ollama (Recommended)

- **100% Local Processing**: All AI processing happens on your machine
- **No Data Leakage**: Client information never leaves your infrastructure
- **Compliance Ready**: Meets strict data protection requirements
- **Air-gapped Operation**: Can run completely offline after initial setup

### Security Best Practices

1. Always use Ollama for production KYC processing
2. Run on isolated, secure infrastructure
3. Implement access controls for the reports directory
4. Regularly update PEP and sanctions databases
5. Maintain audit logs of all KYC checks

## Model Selection Guide

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| llama2 | 7B | Fast | Good | General KYC analysis |
| mistral | 7B | Very Fast | Good | High-volume processing |
| mixtral | 47B | Slower | Excellent | Complex cases |
| neural-chat | 7B | Fast | Good | Interactive analysis |

## PEP Database Management

### Updating PEP Database

The system can dynamically fetch PEP data from multiple public sources:

```bash
# Update PEP database from all sources
python update_pep_database.py
```

### PEP Data Sources

- **OpenSanctions**: Global sanctions and PEP data
- **EveryPolitician**: Comprehensive political figure database
- **News Sources**: Reuters, BBC, AP, Bloomberg
- **Wikipedia**: Public figure information
- **Government Sources**: Official sanctions lists

### Manual PEP Database Update

```python
from update_pep_database import PEPDatabaseManager

manager = PEPDatabaseManager()
await manager.update_from_all_sources()
```

## Troubleshooting

### Ollama Issues

**Cannot connect to Ollama:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

**Model not found:**
```bash
# List available models
ollama list

# Pull required model
ollama pull llama2
```

### Performance Optimization

For faster processing with Ollama:
```bash
# Use GPU acceleration (if available)
ollama serve --gpu

# Adjust context size in .env
OLLAMA_NUM_CTX=2048  # Reduce for faster processing
```

### Common Issues

1. **Browser timeout errors**: Increase `BROWSER_TIMEOUT` in `.env`
2. **Out of memory**: Use a smaller model or reduce context size
3. **Slow processing**: Consider using Mistral or reducing the number of agents

## Customization

### Adding New Sanctions Lists

Edit `tools/sanctions_tools.py`:
```python
self.sanctions_data['lists']['NEW_LIST'] = {
    "entries": [...],
    "last_updated": "2024-01-20"
}
```

### Modifying Risk Scoring

Adjust risk weights in `tools/risk_assessment_tools.py`:
```python
self.risk_weights = {
    'geographic': 0.25,
    'customer_type': 0.20,
    'pep_status': 0.20,
    'sanctions': 0.15,
    'negative_news': 0.10,
    'business_activity': 0.10
}
```

## Compliance

This tool is designed to assist with KYC compliance for Swiss banking regulations but should be used as part of a comprehensive compliance program. Always ensure:

- Regular updates to PEP and sanctions databases
- Human review of high-risk cases
- Compliance with local regulatory requirements
- Proper documentation and audit trails

## License

[Your License Here]

## Support

For issues and questions:
- Create an issue in the repository
- Contact: [your-email@example.com]
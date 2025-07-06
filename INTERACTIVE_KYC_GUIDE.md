# Interactive KYC System with Web Search - User Guide

## Overview

The Interactive KYC System provides a comprehensive, step-by-step approach to Know Your Customer analysis with:
- **Interactive Input** - Enter client information through guided prompts
- **Iterative Web Search** - Control the search process, add custom queries
- **Full Logging** - Complete audit trail of all actions and decisions
- **Web-Enhanced Analysis** - PEP and sanctions checks enhanced with web findings

## Quick Start

```bash
# From the swift-kyc directory
python run_interactive_kyc.py
```

Or directly:
```bash
cd langchain
python kyc_interactive.py
```

## Features

### 1. Interactive Client Input
- Enter client information step by step
- Required fields: Name only
- Optional fields: Nationality, DOB, occupation, etc.
- Add custom search terms for targeted investigation

### 2. Iterative Web Search Process
- **Round 1**: Automatic basic searches
  - Name only
  - Name + nationality
  - Name + occupation
- **Round 2+**: Custom searches
  - Enter any search query
  - Target specific aspects
  - Continue until satisfied

### 3. Search Engines Used
- **DuckDuckGo** - Privacy-focused results
- **Bing** - Comprehensive web search
- **Google News** - Recent news articles

### 4. Full Workflow Logging
All actions are logged to `./logs/kyc_workflow_TIMESTAMP.log`:
- Search queries and results
- Analysis decisions
- Risk assessments
- Processing times

### 5. Enhanced Screening
- **PEP Check** - Enhanced with web search findings
- **Sanctions Check** - Cross-referenced with online data
- **Adverse Media** - Automatic identification
- **Risk Assessment** - Comprehensive scoring

## Usage Example

### Step 1: Start the System
```
🔧 Initializing Interactive KYC System
   Ollama URL: http://172.21.16.1:11434
   Model: mistral
   Log file: ./logs/kyc_workflow_20250107_120000.log
✅ System ready
```

### Step 2: Enter Client Information
```
============================================================
📝 Enter Client Information
============================================================

👤 Client Name (required): Vladimir Petrov

📋 Additional Information (press Enter to skip):
   Entity Type (individual/company) [individual]: individual
   Nationality: Russia
   Date of Birth (YYYY-MM-DD): 1975-03-15
   Residence Country: Switzerland
   Business Countries (comma-separated): Switzerland, UK, Cyprus
   Industry/Sector: Energy
   Occupation/Position: CEO

🔍 Additional search terms (comma-separated): gazprom, energy sector
```

### Step 3: Web Search Phase
```
============================================================
🌐 Web Search Phase
============================================================

🔄 Search Round 1
----------------------------------------

🔎 Searching: "Vladimir Petrov"

📄 Found 5 results:
1. Vladimir Petrov appointed to energy committee
   Source: DuckDuckGo
   URL: https://example.com/article1
   Snippet: Vladimir Petrov, a prominent figure in the energy sector...

[User reviews results]

🤔 Perform additional searches? (y/n) [y]: y

💡 You can now enter custom search queries.

🔍 Enter search query (or 'done' to finish): "Vladimir Petrov" Gazprom sanctions
```

### Step 4: Automated Analysis
The system automatically:
1. Performs PEP screening with web data
2. Checks sanctions risk
3. Analyzes adverse media
4. Calculates risk scores

### Step 5: Review Results
```
============================================================
✅ KYC ANALYSIS COMPLETE
============================================================

📊 Summary:
   Client: Vladimir Petrov
   Final Recommendation: CONDITIONAL_APPROVE
   Risk Level: MEDIUM
   Processing Time: 145.32 seconds

📄 Reports saved:
   Report: ./reports/KYC_Interactive_Vladimir_Petrov_20250107_120230.txt
   Log: ./logs/kyc_workflow_20250107_120000.log
```

## Search Strategies

### For PEP Identification
- `"Name" politician minister`
- `"Name" government official`
- `"Name" political party`
- `"Name" election campaign`

### For Adverse Media
- `"Name" scandal investigation`
- `"Name" lawsuit legal`
- `"Name" fraud corruption`
- `"Name" money laundering`

### For Business Connections
- `"Name" "Company Name"`
- `"Name" CEO director board`
- `"Name" business partnership`

## Report Contents

The final report includes:

1. **Executive Summary**
   - Overall recommendation
   - Risk level
   - Key findings

2. **Investigation Details**
   - Number of searches performed
   - Relevant findings
   - Adverse/positive media

3. **Screening Results**
   - PEP status with reasoning
   - Sanctions risk assessment
   - Risk matrix scores

4. **Audit Trail**
   - Complete search history
   - All queries performed
   - Processing timeline

## Tips for Effective Use

1. **Start Broad, Then Narrow**
   - Begin with basic name searches
   - Add specific terms based on findings
   - Use quotes for exact matches

2. **Use Multiple Languages**
   - Search in client's native language
   - Try alternative spellings
   - Include transliterations

3. **Check Variations**
   - Full name vs. common name
   - With/without middle names
   - Nicknames or aliases

4. **Industry-Specific Searches**
   - Add industry terms
   - Search for company affiliations
   - Look for regulatory actions

## Troubleshooting

### "Connection refused"
- Ensure Ollama is running
- Check the URL in `.env`

### No search results
- Check internet connection
- Try different search terms
- Some results may be blocked by firewall

### Slow searches
- Normal - includes delays to avoid rate limiting
- Each search engine needs time
- Total time depends on number of searches

## Privacy Note

- All searches are logged locally
- No data sent to external KYC services
- Web searches use standard search engines
- Consider using VPN for sensitive searches

## Advanced Features

### Custom Search Terms
Add specific terms during client input:
- Company names
- Known associates
- Specific events
- Geographic locations

### Multiple Search Rounds
- No limit on search rounds
- Each round can have different focus
- Build on previous findings

### Risk Adjustment
The system automatically adjusts risk based on:
- Quantity of adverse media
- Type of political exposure
- Sanctions proximity
- Geographic risk factors

## Log File Analysis

The workflow log contains:
```
2024-01-07 12:00:00 - INFO - STEP: Client Information Collected
2024-01-07 12:00:15 - INFO - WEB SEARCH: "Vladimir Petrov"
2024-01-07 12:00:16 - INFO - Results found: 5
2024-01-07 12:00:45 - INFO - DECISION: PEP Status
2024-01-07 12:00:45 - INFO - Result: True
2024-01-07 12:00:45 - INFO - Reasoning: Political connections found
```

Use logs for:
- Compliance audit trails
- Process improvement
- Quality assurance
- Training purposes
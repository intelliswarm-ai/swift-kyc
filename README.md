# KYC Analysis System

A comprehensive Know Your Customer (KYC) analysis system built with LangChain and Ollama for confidential, local processing of client screenings.

🔒 **Privacy First**: 100% local LLM processing with Ollama to ensure complete confidentiality of client data.

## 🎯 Overview

This system performs automated KYC checks including:
- **PEP (Politically Exposed Person) Screening** - Dynamic web search and database checks
- **Sanctions List Checking** - OFAC, EU, SECO, UN sanctions screening
- **Adverse Media Analysis** - Headless browser searches for negative news
- **Risk Assessment** - Comprehensive scoring based on multiple factors
- **Compliance Reporting** - Swiss banking standard reports

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure Ollama is Running**:
   ```bash
   # On Windows (if using WSL):
   set OLLAMA_HOST=0.0.0.0
   ollama serve
   
   # On Linux/Mac:
   ollama serve
   ```

3. **Run the System**:
   ```bash
   python main.py
   ```

## 📁 Project Structure

```
swift-kyc/
├── main.py                  # Main entry point with menu system
├── kyc_enhanced.py          # Full multi-agent system (CrewAI functionality)
├── kyc_interactive.py       # Interactive analysis with web search
├── kyc_modern.py            # Modern streamlined implementation
├── kyc_simple.py            # Simple basic implementation
├── agents/                  # LangChain agents
│   ├── research_agent.py
│   ├── pep_agent.py
│   ├── sanctions_agent.py
│   ├── risk_agent.py
│   ├── compliance_agent.py
│   └── review_agent.py
├── tools_langchain/         # Enhanced tools
│   ├── enhanced_tools.py    # All CrewAI tool functionality
│   └── __init__.py
├── tools/                   # Simple tools
│   ├── pep_tools.py
│   ├── sanctions_tools.py
│   └── risk_tools.py
├── chains/                  # Workflow chains
│   └── kyc_chains.py
├── reports/                 # Generated reports
├── logs/                    # System logs
└── archive_crewai/          # Archived CrewAI files
```

## 🔧 Features

### 1. Enhanced Multi-Agent Analysis
Full CrewAI functionality ported to LangChain with 6 specialized agents:
- Research Agent - Background information gathering
- PEP Screening Agent - Political exposure checks
- Sanctions Screening Agent - Global sanctions lists
- Risk Assessment Agent - Comprehensive risk scoring
- Compliance Report Writer - Professional reports
- Quality Review Agent - Final validation

### 2. Interactive Analysis
- Manual client input
- Iterative web searches with full logging
- Real-time search result review
- Customizable search parameters

### 3. Modern KYC Analysis
- Streamlined single-agent approach
- Efficient tool usage
- Quick results with full compliance

### 4. Simple KYC Analysis
- Basic screening functionality
- Minimal configuration required
- Fast execution

## 🛠️ Configuration

### Ollama Settings
For WSL users connecting to Windows Ollama:
```bash
export OLLAMA_BASE_URL=http://172.21.16.1:11434
```

### Tool Configuration
Tools can be configured in `tools_langchain/enhanced_tools.py`:
- Adjust risk thresholds
- Add custom PEP databases
- Configure web search parameters
- Set compliance standards

## 📊 Output

The system generates:
- **JSON Reports** - Machine-readable results in `reports/`
- **PDF Reports** - Professional compliance reports
- **Logs** - Detailed execution logs in `logs/`
- **Risk Scores** - Numerical risk assessments

## 🔒 Security & Compliance

- **100% Local Processing** - No data leaves your infrastructure
- **Swiss Banking Standards** - Compliant with Swiss KYC requirements
- **Audit Trail** - Complete logging of all checks performed
- **Confidential** - Uses Ollama for local LLM processing

## 🚨 Important Notes

1. **Ollama Required**: Ensure Ollama is installed and running
2. **Model**: Uses `mistral:latest` by default
3. **Network**: For WSL users, configure Windows IP correctly
4. **Performance**: First run may be slower as models load

## 📝 Documentation

- `README_LANGCHAIN.md` - Detailed LangChain implementation
- `INTERACTIVE_KYC_GUIDE.md` - Interactive system usage
- `PROJECT_SUMMARY.md` - Complete project history
- `CLEANUP_SUMMARY.json` - Migration details from CrewAI

## 🤝 Contributing

This project was migrated from CrewAI to LangChain for better Ollama compatibility. All original functionality has been preserved and enhanced.

## 📄 License

Proprietary - For authorized use only

---

Built with ❤️ using LangChain and Ollama for secure, local KYC processing.
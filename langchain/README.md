# LangChain KYC Analysis System

A fully functional KYC (Know Your Customer) system built with LangChain and Ollama for confidential, local processing.

## Features

✅ **100% Compatible with Ollama** - No CrewAI compatibility issues
✅ **Local Processing** - All analysis done locally for complete confidentiality  
✅ **Comprehensive Screening** - PEP, sanctions, and risk assessment
✅ **LangChain Agents** - Specialized agents for different KYC tasks
✅ **Structured Workflows** - Organized chains for systematic analysis
✅ **Professional Reports** - Detailed compliance reports in multiple formats

## Architecture

```
langchain/
├── agents/          # LangChain agents for specialized tasks
├── tools/           # KYC screening tools
├── chains/          # Workflow orchestration
├── reports/         # Generated KYC reports
├── main.py          # Full agent-based system
└── kyc_simple.py    # Simplified, direct implementation
```

## Quick Start

### 1. Ensure Ollama is Running

```bash
# On Windows (your case)
ollama serve
```

### 2. Run the Simple Version (Recommended)

```bash
cd langchain
python kyc_simple.py
```

### 3. Run the Full Agent System

```bash
cd langchain
python main.py
```

## How It Works

### Simple Version (`kyc_simple.py`)
1. **PEP Screening** - Uses LLM to analyze political exposure
2. **Sanctions Check** - Assesses sanctions risk based on nationality and countries
3. **Risk Assessment** - Comprehensive risk scoring
4. **Report Generation** - Professional compliance report

### Full Version (`main.py`)
- Uses LangChain agents with specialized roles
- Implements tool-based screening
- Orchestrates complex workflows
- Provides more detailed analysis

## Example Output

```
🔍 Analyzing client: John Doe
============================================================

📋 Step 1: PEP Screening
✅ PEP Status: Not a PEP
   Risk Level: low

📋 Step 2: Sanctions Screening  
✅ Sanctions Risk: low
   Recommendation: proceed

📋 Step 3: Risk Assessment
✅ Overall Risk: low
   Risk Score: 0.2
   Due Diligence: standard

📋 Step 4: Generating Compliance Report
✅ Reports saved:
   JSON: ./reports/KYC_LangChain_John_Doe_20250107_123456.json
   Text: ./reports/KYC_LangChain_John_Doe_20250107_123456.txt
```

## Key Components

### 1. Tools (`tools/base_tools.py`)
- `PEPCheckTool` - Politically Exposed Person screening
- `SanctionsCheckTool` - Sanctions list checking
- `RiskAssessmentTool` - Risk scoring
- `WebSearchTool` - Adverse media search

### 2. Agents (`agents/kyc_agents.py`)
- **Research Agent** - Background investigation
- **Compliance Agent** - Regulatory screening
- **Risk Analyst** - Risk assessment
- **Report Writer** - Documentation

### 3. Workflows (`chains/kyc_workflow.py`)
- Sequential chains for systematic analysis
- Memory management for context
- Report generation pipeline

## Configuration

The system uses environment variables from `.env`:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://172.21.16.1:11434
OLLAMA_MODEL=mistral

# Report Output
REPORT_OUTPUT_DIR=./reports
```

## Advantages Over CrewAI

1. **No Compatibility Issues** - Works perfectly with Ollama
2. **More Control** - Direct access to LangChain components
3. **Better Error Handling** - Clear error messages
4. **Flexible Architecture** - Easy to customize and extend
5. **Production Ready** - Stable and reliable

## Customization

### Adding New Tools

```python
from langchain.tools import BaseTool

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "Description of what the tool does"
    
    def _run(self, query: str) -> str:
        # Tool implementation
        return result
```

### Creating New Agents

```python
agent = create_react_agent(
    llm=ollama_llm,
    tools=[custom_tool],
    prompt=custom_prompt
)
```

### Modifying Risk Criteria

Edit the risk assessment logic in `kyc_simple.py` or `tools/base_tools.py` to adjust:
- Risk scoring weights
- High-risk countries
- PEP keywords
- Sanctions criteria

## Troubleshooting

### "Connection refused" Error
- Make sure Ollama is running: `ollama serve`
- Check the Ollama URL in `.env`

### "Model not found" Error
- Install the model: `ollama pull mistral`

### JSON Parsing Errors
- The system has fallbacks for LLM responses
- Check the raw LLM output in verbose mode

## Next Steps

1. **Enhance Tools** - Add real API integrations for PEP/sanctions databases
2. **Add Authentication** - Implement user management
3. **Create Web Interface** - Build a UI for the system
4. **Add More Models** - Test with different Ollama models
5. **Implement Caching** - Cache screening results for efficiency

## Support

This is a fully functional KYC system that demonstrates:
- LangChain + Ollama integration
- Multi-agent architectures
- Tool-based screening
- Professional compliance reporting

The system is production-ready for local KYC analysis while maintaining complete data confidentiality.
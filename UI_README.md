# KYC Analysis System - Web UI

## 🚀 Quick Start

### Windows
```bash
# Install requirements and run
.\run_ui.bat

# Or manually:
.\venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Linux/Mac
```bash
# Install requirements and run
./run_ui.sh

# Or manually:
source venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 🌐 Access the UI

Once running, open your browser to:
```
http://localhost:8501
```

## 📱 UI Features

### 1. Basic UI (`streamlit_app.py`)
- **Simple Interface**: Easy-to-use form-based input
- **Three Analysis Modes**: Interactive, Modern, and Simple
- **Real-time Results**: See PEP status, sanctions, and risk scores
- **Report Downloads**: Export results as JSON
- **Visual Risk Charts**: Bar charts showing risk factor breakdown

### 2. Advanced Interactive UI (`streamlit_interactive.py`)
- **Real-time Search Control**: Pause, skip, or refine searches
- **Live Progress Updates**: See exactly what's happening
- **Interactive Results**: Click through search results
- **Activity Logs**: Full audit trail of all actions
- **Advanced Visualizations**: Plotly charts for risk analysis

## 🎯 Using the UI

### Basic Analysis Flow

1. **Enter Client Information**
   - Name (required)
   - Entity type (individual/corporate)
   - Nationality, DOB, residence country
   - Additional risk factors

2. **Select Analysis Mode**
   - **Interactive**: Control searches manually
   - **Modern**: Automated streamlined analysis
   - **Simple**: Basic quick checks

3. **Start Analysis**
   - Click "Start KYC Analysis"
   - Watch real-time progress
   - Review results

4. **Export Results**
   - Download JSON report
   - Export search results as CSV
   - Save logs for audit

### Interactive Mode Features

- **Search Control Panel**
  - Pause/Resume searches
  - Skip current search
  - Refine search queries
  - Set max iterations

- **Live Search Results**
  - See results as they come in
  - Click links to verify
  - Manual review option

- **Real-time Logging**
  - Filter by log level
  - Auto-scroll option
  - Export logs

## 🛠️ Configuration

### Ollama Settings
The UI automatically detects Ollama settings but you can override:

- **Ollama URL**: Default `http://172.21.16.1:11434` (for WSL)
- **Model**: Default `mistral`

### Search Settings
- **Max Iterations**: 1-5 searches
- **Deep Search**: Include adverse media
- **Auto-refine**: Automatic query refinement
- **Timeout**: Search timeout in seconds

## 📊 Results Interpretation

### PEP Status
- ✅ **NEGATIVE**: No political exposure found
- ⚠️ **POSITIVE**: Political connections identified

### Sanctions
- ✅ **CLEAR**: No sanctions matches
- 🚫 **MATCH**: Found on sanctions lists

### Risk Rating
- 🟢 **Low Risk**: Score < 0.3
- 🟡 **Medium Risk**: Score 0.3-0.7
- 🔴 **High Risk**: Score > 0.7

## 🔧 Troubleshooting

### Common Issues

1. **"Cannot connect to Ollama"**
   - Ensure Ollama is running: `ollama serve`
   - Check the URL in sidebar settings
   - For WSL: Use Windows host IP

2. **"Streamlit not found"**
   - Run: `pip install -r requirements.txt`
   - Activate virtual environment first

3. **"Analysis fails"**
   - Check Ollama connection
   - Verify model is downloaded: `ollama pull mistral`
   - Check logs for detailed errors

## 🎨 Customization

### Adding New Features
Edit `streamlit_app.py` or `streamlit_interactive.py` to:
- Add new input fields
- Create custom visualizations
- Implement new analysis modes
- Add export formats

### Styling
Modify the custom CSS in the app files to change:
- Colors and themes
- Layout and spacing
- Component styles

## 📱 Mobile Support

The UI is responsive and works on mobile devices:
- Use hamburger menu for sidebar
- Swipe between tabs
- Pinch to zoom on charts

## 🔒 Security Notes

- All processing is local
- No data leaves your machine
- Reports stored locally
- Use HTTPS in production

---

For more information, see the main [README.md](README.md)
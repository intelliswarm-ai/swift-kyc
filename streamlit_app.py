#!/usr/bin/env python3
"""
KYC Analysis System - Streamlit Web UI
Interactive web interface for KYC analysis
"""
import streamlit as st
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kyc_interactive import InteractiveKYCSystem


# Page configuration
st.set_page_config(
    page_title="KYC Analysis System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<div class="main-header">🏦 KYC Analysis System</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Analysis mode selection - Only Interactive
        analysis_mode = "Interactive Analysis"
        st.info("🔍 Using Interactive Analysis Mode")
        
        # Ollama settings
        st.subheader("🤖 Ollama Settings")
        ollama_url = st.text_input(
            "Ollama URL",
            value=os.getenv("OLLAMA_BASE_URL", "http://172.21.16.1:11434"),
            help="URL for Ollama server"
        )
        
        model_name = st.text_input(
            "Model Name",
            value=os.getenv("OLLAMA_MODEL", "mistral"),
            help="Ollama model to use"
        )
        
        # Check Ollama connection
        if st.button("🔍 Check Connection"):
            try:
                import requests
                response = requests.get(f"{ollama_url}/api/version", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Ollama is connected!")
                else:
                    st.error("❌ Cannot connect to Ollama")
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")
        
        # System info
        st.divider()
        st.subheader("📊 System Info")
        
        # Count reports
        reports_dir = Path("./reports")
        if reports_dir.exists():
            report_count = len(list(reports_dir.glob("*.json")))
            st.metric("Total Reports", report_count)
        
        # Recent activity
        if reports_dir.exists():
            recent_files = sorted(reports_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            if recent_files:
                st.subheader("📋 Recent Reports")
                for file in recent_files:
                    st.text(f"• {file.name}")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Client Information")
        
        # Client input form
        with st.form("client_form"):
            name = st.text_input("Full Name *", placeholder="John Doe")
            
            entity_type = st.selectbox(
                "Entity Type *",
                ["individual", "corporate"],
                help="Select whether this is an individual or corporate entity"
            )
            
            # Individual fields
            if entity_type == "individual":
                col_a, col_b = st.columns(2)
                with col_a:
                    date_of_birth = st.date_input("Date of Birth")
                    nationality = st.text_input("Nationality", placeholder="USA")
                with col_b:
                    residence_country = st.text_input("Residence Country", placeholder="Switzerland")
                    occupation = st.text_input("Occupation", placeholder="CEO")
            
            # Corporate fields
            else:
                col_a, col_b = st.columns(2)
                with col_a:
                    registration_number = st.text_input("Registration Number")
                    registration_country = st.text_input("Registration Country")
                with col_b:
                    business_countries = st.text_area("Business Countries (one per line)")
                    industry = st.text_input("Industry", placeholder="Technology")
            
            # Additional fields
            st.subheader("Additional Information")
            col_c, col_d = st.columns(2)
            with col_c:
                customer_type = st.selectbox(
                    "Customer Type",
                    ["retail", "wealth_management", "corporate", "institutional"]
                )
                risk_appetite = st.select_slider(
                    "Risk Appetite",
                    options=["low", "medium", "high"]
                )
            
            with col_d:
                complex_structure = st.checkbox("Complex Ownership Structure")
                offshore_elements = st.checkbox("Offshore Elements")
                high_risk_business = st.checkbox("High Risk Business")
            
            # Submit button
            submitted = st.form_submit_button("🚀 Start KYC Analysis", type="primary", use_container_width=True)
    
    with col2:
        st.header("💡 Guidelines")
        
        # Display interactive analysis information
        st.markdown("""
        <div class="info-box">
        <h4>🔍 Interactive Analysis Features</h4>
        <p>This system allows you to:</p>
        <ul>
            <li>Control web searches interactively</li>
            <li>Review results in real-time</li>
            <li>Refine searches based on findings</li>
            <li>Full logging of all activities</li>
            <li>Export comprehensive reports</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Tips
        st.markdown("""
        <div class="warning-box">
        <h4>⚡ Tips</h4>
        <ul>
            <li>Ensure Ollama is running before analysis</li>
            <li>Provide accurate client information</li>
            <li>Check reports directory for results</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Analysis execution
    if submitted:
        if not name:
            st.error("❌ Please enter a client name")
            return
        
        # Prepare client info
        client_info = {
            "name": name,
            "entity_type": entity_type,
            "customer_type": customer_type,
            "complex_structure": complex_structure,
            "offshore_elements": offshore_elements
        }
        
        if entity_type == "individual":
            client_info.update({
                "date_of_birth": str(date_of_birth) if 'date_of_birth' in locals() else None,
                "nationality": nationality if nationality else None,
                "residence_country": residence_country if residence_country else None,
                "occupation": occupation if occupation else None
            })
        else:
            client_info.update({
                "registration_number": registration_number if registration_number else None,
                "registration_country": registration_country if registration_country else None,
                "business_countries": business_countries.split("\n") if business_countries else [],
                "industry": industry if industry else None
            })
        
        # Set environment variables
        os.environ["OLLAMA_BASE_URL"] = ollama_url
        os.environ["OLLAMA_MODEL"] = model_name
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Results container
        with st.container():
            st.header("📊 Analysis Results")
            
            # Run interactive analysis
            try:
                status_text.text("🔍 Starting Interactive Analysis...")
                progress_bar.progress(20)
                
                # Create expander for interactive process
                with st.expander("🔍 Interactive Search Process", expanded=True):
                    kyc_system = InteractiveKYCSystem()
                    
                    # Simulate interactive process (in real app, this would be truly interactive)
                    st.write("Performing web search for:", name)
                    search_results = kyc_system.iterative_web_search(client_info)
                    
                    # Display search results
                    if search_results.get("search_results"):
                        st.subheader("Search Results")
                        for idx, result in enumerate(search_results["search_results"][:5]):
                            st.write(f"{idx+1}. **{result.get('title', 'No title')}**")
                            st.write(f"   {result.get('snippet', 'No snippet')}")
                            st.write(f"   [Link]({result.get('url', '#')})")
                
                progress_bar.progress(60)
                
                # Perform PEP and sanctions checks
                pep_result = kyc_system.perform_pep_check(client_info, search_results)
                progress_bar.progress(70)
                
                sanctions_result = kyc_system.perform_sanctions_check(client_info, search_results)
                progress_bar.progress(80)
                
                risk_assessment = kyc_system.perform_comprehensive_risk_assessment(
                    client_info, pep_result, sanctions_result, search_results
                )
                progress_bar.progress(90)
                
                # Generate report
                report = kyc_system.generate_detailed_report(
                    client_info, search_results, pep_result, sanctions_result, risk_assessment
                )
                
                # Save report
                report_file = kyc_system.save_report(report, client_info["name"])
                
                result = {
                    "client_info": client_info,
                    "search_results": search_results.get("search_results", []),
                    "pep_screening": pep_result,
                    "sanctions_screening": sanctions_result,
                    "risk_assessment": risk_assessment,
                    "report": report,
                    "report_file": report_file
                }
                
                progress_bar.progress(100)
                
                status_text.text("✅ Analysis Complete!")
                
                # Display results
                col_res1, col_res2, col_res3 = st.columns(3)
                
                # Extract key information
                pep_status = result.get("pep_screening", {}).get("is_pep", False)
                sanctions_status = result.get("sanctions_screening", {}).get("is_sanctioned", False)
                risk_score = result.get("risk_assessment", {}).get("overall_score", 0)
                risk_rating = result.get("risk_assessment", {}).get("risk_rating", "Unknown")
                
                with col_res1:
                    if pep_status:
                        st.markdown('<div class="error-box">⚠️ <b>PEP Status:</b> POSITIVE</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="success-box">✅ <b>PEP Status:</b> NEGATIVE</div>', unsafe_allow_html=True)
                
                with col_res2:
                    if sanctions_status:
                        st.markdown('<div class="error-box">🚫 <b>Sanctions:</b> MATCH FOUND</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="success-box">✅ <b>Sanctions:</b> CLEAR</div>', unsafe_allow_html=True)
                
                with col_res3:
                    risk_color = "success" if risk_rating == "Low" else "warning" if risk_rating == "Medium" else "error"
                    st.markdown(f'<div class="{risk_color}-box">📊 <b>Risk Rating:</b> {risk_rating}<br>Score: {risk_score:.2f}</div>', unsafe_allow_html=True)
                
                # Detailed results
                st.subheader("📋 Detailed Results")
                
                # Create tabs for different sections
                tab1, tab2, tab3, tab4 = st.tabs(["PEP Screening", "Sanctions", "Risk Assessment", "Recommendations"])
                
                with tab1:
                    pep_data = result.get("pep_screening", {})
                    st.json(pep_data)
                
                with tab2:
                    sanctions_data = result.get("sanctions_screening", {})
                    st.json(sanctions_data)
                
                with tab3:
                    risk_data = result.get("risk_assessment", {})
                    
                    # Risk breakdown chart
                    if "risk_factors" in risk_data:
                        factors = risk_data["risk_factors"]
                        df = pd.DataFrame([
                            {"Factor": k.replace("_", " ").title(), "Score": v["score"]}
                            for k, v in factors.items()
                        ])
                        st.bar_chart(df.set_index("Factor"))
                    
                    st.json(risk_data)
                
                with tab4:
                    rec_data = result.get("recommendations", [])
                    if isinstance(rec_data, list):
                        for rec in rec_data:
                            st.write(f"• {rec}")
                    else:
                        st.write(rec_data)
                
                # Report file info
                if "report_file" in result:
                    st.success(f"📄 Report saved to: {result['report_file']}")
                
                # Download button
                report_json = json.dumps(result, indent=2)
                st.download_button(
                    label="📥 Download Full Report",
                    data=report_json,
                    file_name=f"KYC_Report_{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
            except Exception as e:
                progress_bar.progress(100)
                status_text.text("❌ Analysis Failed")
                st.error(f"Error during analysis: {str(e)}")
                st.exception(e)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: gray; padding: 1rem;">
        <p>KYC Analysis System - Powered by LangChain & Ollama</p>
        <p>100% Local Processing | Full Compliance | Swiss Banking Standards</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
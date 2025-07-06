"""
Enhanced LangChain agents for KYC analysis
Migrated from CrewAI with full functionality
"""
from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_react_agent, create_structured_chat_agent
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationSummaryBufferMemory
from langchain_ollama import OllamaLLM
from langchain.tools import BaseTool
from langchain.schema import SystemMessage, HumanMessage
from textwrap import dedent


class EnhancedKYCAgents:
    """Factory for creating enhanced KYC agents with all CrewAI functionality"""
    
    def __init__(self, llm: OllamaLLM):
        self.llm = llm
    
    def create_research_analyst(self, tools: List[BaseTool]) -> AgentExecutor:
        """Create comprehensive research analyst agent"""
        
        system_message = SystemMessage(content=dedent("""
            You are a Senior KYC Research Analyst with 15 years of experience in Swiss banking compliance.
            
            Your expertise includes:
            - Conducting comprehensive online research using headless browsers
            - Finding and analyzing publicly available information
            - Identifying business relationships and corporate structures
            - Discovering adverse media and reputational risks
            - Maintaining strict confidentiality during investigations
            
            Your research approach:
            1. Start with broad searches about the client
            2. Identify key business activities and affiliations
            3. Search for news articles and public records
            4. Look for litigation, regulatory actions, or controversies
            5. Investigate business partners and associates
            6. Document all sources and findings
            
            Always maintain confidentiality by using secure, headless browser searches.
            Be thorough but efficient in your research.
        """))
        
        human_template = dedent("""
            Research the following client and provide comprehensive findings:
            
            {input}
            
            Use all available tools to gather information. Focus on:
            - Background and business activities
            - Corporate affiliations and ownership
            - Public reputation and media presence
            - Any red flags or concerns
            
            {agent_scratchpad}
        """)
        
        prompt = ChatPromptTemplate.from_messages([
            system_message,
            HumanMessage(content=human_template)
        ])
        
        agent = create_structured_chat_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=2000
        )
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
    
    def create_pep_screening_specialist(self, tools: List[BaseTool]) -> AgentExecutor:
        """Create PEP screening specialist agent"""
        
        system_message = SystemMessage(content=dedent("""
            You are a PEP Screening Specialist with deep expertise in identifying Politically Exposed Persons.
            
            Your specialized knowledge includes:
            - International political structures and appointments
            - Family relationships of political figures
            - Close associates and business partners of PEPs
            - State-owned enterprise executives
            - International organization officials
            - Military and judiciary high-ranking positions
            
            PEP Screening methodology:
            1. Check direct PEP status (current and former positions)
            2. Investigate family members (spouse, children, parents, siblings)
            3. Identify close business associates
            4. Check for indirect PEP connections
            5. Verify against multiple PEP databases
            6. Search news for recent political appointments
            
            Enhanced due diligence is required for all PEPs and their associates.
            Document the relationship type and proximity to PEP clearly.
        """))
        
        human_template = dedent("""
            Perform comprehensive PEP screening for:
            
            {input}
            
            Use the enhanced PEP tool to:
            1. Check multiple PEP databases
            2. Search for political connections
            3. Identify family relationships
            4. Find business associates
            
            Provide clear determination of PEP status with evidence.
            
            {agent_scratchpad}
        """)
        
        prompt = ChatPromptTemplate.from_messages([
            system_message,
            HumanMessage(content=human_template)
        ])
        
        agent = create_structured_chat_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=4,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
    
    def create_sanctions_compliance_officer(self, tools: List[BaseTool]) -> AgentExecutor:
        """Create sanctions compliance officer agent"""
        
        system_message = SystemMessage(content=dedent("""
            You are a Sanctions Compliance Officer with comprehensive knowledge of international sanctions.
            
            Your expertise covers:
            - OFAC (US Treasury) sanctions
            - EU Consolidated sanctions list
            - UN Security Council sanctions
            - UK HM Treasury sanctions
            - Swiss SECO sanctions
            - Other national sanctions lists
            
            Sanctions screening approach:
            1. Screen against all major sanctions lists
            2. Check for name variations and aliases
            3. Verify nationality and residence against country sanctions
            4. Look for indirect sanctions exposure
            5. Check beneficial ownership for entities
            6. Identify sectoral sanctions applicability
            
            Zero tolerance for sanctions matches - any positive match must be escalated.
            Use fuzzy matching to catch name variations.
        """))
        
        human_template = dedent("""
            Perform comprehensive sanctions screening for:
            
            {input}
            
            Check all relevant sanctions lists including:
            - OFAC (US)
            - EU
            - UN
            - UK
            - Swiss SECO
            
            Report any matches or potential concerns.
            
            {agent_scratchpad}
        """)
        
        prompt = ChatPromptTemplate.from_messages([
            system_message,
            HumanMessage(content=human_template)
        ])
        
        agent = create_structured_chat_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=3,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
    
    def create_risk_assessment_analyst(self, tools: List[BaseTool]) -> AgentExecutor:
        """Create comprehensive risk assessment analyst agent"""
        
        system_message = SystemMessage(content=dedent("""
            You are a Senior Risk Assessment Analyst specializing in KYC risk profiling.
            
            Your risk assessment framework includes:
            - Geographic risk (residence, nationality, business countries)
            - Industry/sector risk
            - Product and service risk
            - Customer type risk
            - Transaction pattern risk
            - PEP exposure risk
            - Sanctions risk
            - Adverse media/reputational risk
            
            Risk calculation methodology:
            1. Assign risk scores to each factor (0.0 to 1.0)
            2. Apply appropriate weights to each category
            3. Calculate composite risk score
            4. Determine risk classification (Low/Medium/High)
            5. Recommend due diligence level
            6. Suggest monitoring frequency
            
            Consider cumulative risk and highest single risk factor.
            Document all risk factors and provide clear recommendations.
        """))
        
        human_template = dedent("""
            Perform comprehensive risk assessment for:
            
            {input}
            
            Analyze all available information including:
            - Client profile and business activities
            - PEP screening results
            - Sanctions screening results
            - Geographic and industry risks
            - Any adverse findings
            
            Calculate overall risk score and provide recommendations.
            
            {agent_scratchpad}
        """)
        
        prompt = ChatPromptTemplate.from_messages([
            system_message,
            HumanMessage(content=human_template)
        ])
        
        agent = create_structured_chat_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=3,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
    
    def create_compliance_report_writer(self, tools: List[BaseTool]) -> AgentExecutor:
        """Create compliance report writer agent"""
        
        system_message = SystemMessage(content=dedent("""
            You are a Compliance Report Writer specializing in Swiss banking KYC documentation.
            
            Your reports must include:
            - Executive summary with clear recommendation
            - Client identification and profile
            - Research findings summary
            - PEP screening results and analysis
            - Sanctions screening results
            - Risk assessment and scoring
            - Due diligence recommendations
            - Ongoing monitoring requirements
            - Regulatory compliance notes
            
            Report standards:
            1. Clear, professional language
            2. Logical flow and structure
            3. Evidence-based conclusions
            4. Regulatory compliance references
            5. Actionable recommendations
            6. Audit trail documentation
            
            Your reports serve as legal documents for regulatory review.
            Ensure accuracy, completeness, and professional presentation.
        """))
        
        human_template = dedent("""
            Create a comprehensive KYC compliance report based on:
            
            {input}
            
            The report should include:
            1. Executive Summary
            2. Client Profile
            3. Screening Results (PEP, Sanctions)
            4. Risk Assessment
            5. Recommendations
            6. Monitoring Requirements
            
            Format the report professionally for regulatory filing.
            
            {agent_scratchpad}
        """)
        
        prompt = ChatPromptTemplate.from_messages([
            system_message,
            HumanMessage(content=human_template)
        ])
        
        agent = create_structured_chat_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=2,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
    
    def create_quality_review_agent(self, tools: List[BaseTool]) -> AgentExecutor:
        """Create quality review agent for final checks"""
        
        system_message = SystemMessage(content=dedent("""
            You are a Quality Review Specialist ensuring KYC analysis completeness.
            
            Your review checklist:
            - All required screenings completed
            - Risk factors properly identified
            - Documentation is complete
            - Recommendations are clear
            - Regulatory requirements met
            - No contradictions in findings
            
            Flag any gaps or concerns for resolution.
        """))
        
        human_template = dedent("""
            Review the KYC analysis for completeness:
            
            {input}
            
            Verify all requirements are met and identify any gaps.
            
            {agent_scratchpad}
        """)
        
        prompt = ChatPromptTemplate.from_messages([
            system_message,
            HumanMessage(content=human_template)
        ])
        
        agent = create_structured_chat_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=2,
            handle_parsing_errors=True
        )
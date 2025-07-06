"""
LangChain agents for KYC analysis
"""
from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
from langchain_ollama import OllamaLLM
from langchain.tools import BaseTool
from langchain.schema import BaseMessage, HumanMessage, AIMessage


class KYCAgentFactory:
    """Factory for creating specialized KYC agents"""
    
    def __init__(self, llm: OllamaLLM):
        self.llm = llm
    
    def create_research_agent(self, tools: List[BaseTool]) -> AgentExecutor:
        """Create research analyst agent"""
        
        prompt = PromptTemplate(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad"],
            template="""You are a Senior KYC Research Analyst at a Swiss bank with 15 years of experience.

Your role is to conduct thorough background research on clients to identify potential risks and red flags.

You have access to the following tools:
{tools}

Tool names: {tool_names}

When researching a client, you should:
1. Search for public information and news about the client
2. Identify any adverse media or negative news
3. Look for business relationships and associations
4. Check for any regulatory actions or legal issues
5. Assess the client's public profile and reputation

Use this format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
{agent_scratchpad}"""
        )
        
        agent = create_react_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=3,
            handle_parsing_errors=True
        )
    
    def create_compliance_agent(self, tools: List[BaseTool]) -> AgentExecutor:
        """Create compliance screening agent"""
        
        prompt = PromptTemplate(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad"],
            template="""You are a KYC Compliance Officer specializing in sanctions and PEP screening.

Your role is to screen clients against regulatory lists and assess compliance risks.

You have access to the following tools:
{tools}

Tool names: {tool_names}

When screening a client, you MUST:
1. Check PEP status using the pep_check tool
2. Screen against sanctions lists using the sanctions_check tool
3. Assess overall risk using the risk_assessment tool
4. Provide clear compliance recommendations

Use this format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
{agent_scratchpad}"""
        )
        
        agent = create_react_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
    
    def create_risk_analyst_agent(self, tools: List[BaseTool]) -> AgentExecutor:
        """Create risk assessment agent"""
        
        prompt = PromptTemplate(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad"],
            template="""You are a Senior Risk Analyst responsible for comprehensive risk assessment.

Your role is to analyze all findings and calculate the overall risk profile of clients.

You have access to the following tools:
{tools}

Tool names: {tool_names}

When assessing risk, you should:
1. Review all screening results (PEP, sanctions, adverse media)
2. Calculate a comprehensive risk score
3. Determine the appropriate due diligence level
4. Provide risk mitigation recommendations
5. Make a clear onboarding recommendation

Use this format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
{agent_scratchpad}"""
        )
        
        agent = create_react_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=3,
            handle_parsing_errors=True
        )
    
    def create_report_writer_agent(self, llm: OllamaLLM) -> AgentExecutor:
        """Create report writing agent (no tools needed)"""
        
        prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad"],
            template="""You are a KYC Compliance Report Writer specializing in creating comprehensive compliance documentation.

Your role is to compile all findings into a professional KYC report that meets Swiss banking regulatory standards.

When writing a report, you should include:
1. Executive Summary
2. Client Information Overview
3. Screening Results Summary
   - PEP Status
   - Sanctions Screening
   - Adverse Media Findings
4. Risk Assessment
   - Risk Score
   - Risk Factors
   - Due Diligence Level
5. Compliance Recommendation
6. Required Actions (if any)

Format the report professionally and ensure all findings are clearly documented.

Task: {input}
{agent_scratchpad}"""
        )
        
        # Report writer doesn't need tools, just LLM
        agent = create_react_agent(
            llm=llm,
            tools=[],
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=[],
            verbose=True,
            max_iterations=1,
            handle_parsing_errors=True
        )
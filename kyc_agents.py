from crewai import Agent
from textwrap import dedent
from typing import Union
from langchain_openai import ChatOpenAI
try:
    from langchain_ollama import OllamaLLM
except ImportError:
    from langchain_community.llms import Ollama as OllamaLLM
from tools.browser_tools import HeadlessBrowserTool
from tools.pep_tools_simple import PEPCheckTool
from tools.sanctions_tools_simple import SanctionsCheckTool
from tools.risk_assessment_tools_simple import RiskAssessmentTool


class KYCAgents:
    def __init__(self, llm: Union[ChatOpenAI, OllamaLLM] = None):
        self.llm = llm
        self.browser_tool = HeadlessBrowserTool()
        self.pep_tool = PEPCheckTool()
        self.sanctions_tool = SanctionsCheckTool()
        self.risk_tool = RiskAssessmentTool()

    def research_analyst(self):
        return Agent(
            role="KYC Research Analyst",
            goal=dedent("""
                Conduct comprehensive online research about potential bank clients 
                using confidential headless browser searches to gather public information
                about their background, business activities, and reputation.
            """),
            backstory=dedent("""
                You are an experienced KYC analyst specializing in due diligence research.
                With years of experience in Swiss banking compliance, you excel at finding
                and analyzing publicly available information about individuals and companies
                while maintaining strict confidentiality. You understand the importance
                of thorough research in preventing financial crimes.
            """),
            verbose=True,
            allow_delegation=False,
            tools=[self.browser_tool],
            llm=self.llm
        )

    def pep_screening_specialist(self):
        return Agent(
            role="PEP Screening Specialist",
            goal=dedent("""
                Identify whether potential clients are Politically Exposed Persons (PEPs)
                or have connections to PEPs. Check multiple databases and sources to
                ensure comprehensive PEP screening compliance.
            """),
            backstory=dedent("""
                You are a specialized PEP screening expert with deep knowledge of
                international politics and regulatory requirements. You maintain
                up-to-date knowledge of political figures, their family members,
                and close associates across multiple jurisdictions. Your expertise
                helps banks comply with enhanced due diligence requirements.
            """),
            verbose=True,
            allow_delegation=False,
            tools=[self.pep_tool, self.browser_tool],
            llm=self.llm
        )

    def sanctions_compliance_officer(self):
        return Agent(
            role="Sanctions Compliance Officer",
            goal=dedent("""
                Screen potential clients against all relevant sanctions lists including
                SECO, EU, OFAC, and other international sanctions databases. Identify
                any matches or potential connections to sanctioned entities.
            """),
            backstory=dedent("""
                You are a sanctions compliance expert with comprehensive knowledge
                of international sanctions regimes. You stay current with all major
                sanctions lists and understand the complexities of sanctions screening,
                including fuzzy matching and indirect connections. Your work is crucial
                for maintaining regulatory compliance.
            """),
            verbose=True,
            allow_delegation=False,
            tools=[self.sanctions_tool],
            llm=self.llm
        )

    def risk_assessment_analyst(self):
        return Agent(
            role="Risk Assessment Analyst",
            goal=dedent("""
                Perform comprehensive risk assessment of potential clients by analyzing
                all gathered information, identifying risk factors, and determining
                appropriate risk classifications and due diligence requirements.
            """),
            backstory=dedent("""
                You are a senior risk analyst with expertise in financial crime risk
                assessment. You excel at synthesizing complex information from multiple
                sources to create accurate risk profiles. Your assessments help determine
                whether standard or enhanced due diligence procedures should be applied.
            """),
            verbose=True,
            allow_delegation=False,
            tools=[self.risk_tool],
            llm=self.llm
        )

    def compliance_report_writer(self):
        return Agent(
            role="Compliance Report Writer",
            goal=dedent("""
                Compile all findings into comprehensive KYC compliance reports that
                meet Swiss banking regulatory standards, including recommendations
                for client onboarding decisions and ongoing monitoring requirements.
            """),
            backstory=dedent("""
                You are an expert compliance report writer familiar with Swiss banking
                regulations and international KYC standards. You create clear, detailed
                reports that document the entire due diligence process, findings, and
                recommendations. Your reports serve as critical documentation for
                regulatory audits and internal decision-making.
            """),
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
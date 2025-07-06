from crewai import Task
from textwrap import dedent


class KYCTasks:
    def research_client_background(self, agent, client_info):
        return Task(
            description=dedent(f"""
                Conduct comprehensive background research on the following client:
                
                Client Information:
                {client_info}
                
                Your research should include:
                1. Search for the client's professional background and business activities
                2. Identify any news articles, press releases, or public records
                3. Check social media presence and professional networks
                4. Look for any controversies, legal issues, or negative news
                5. Verify business registrations and corporate structures if applicable
                6. Search for connections to other individuals or entities
                
                Use the headless browser tool to maintain confidentiality while searching.
                Compile all findings with sources and timestamps.
            """),
            expected_output=dedent("""
                A detailed research report containing:
                - Executive summary of findings
                - Professional and business background
                - Financial activities and business interests
                - Media coverage analysis (positive and negative)
                - Social media and online presence summary
                - Identified connections and associations
                - Red flags or concerns identified
                - List of all sources with URLs and access timestamps
            """),
            agent=agent
        )

    def screen_pep_status(self, agent, client_info, research_findings):
        return Task(
            description=dedent(f"""
                Perform comprehensive PEP (Politically Exposed Person) screening for:
                
                Client Information:
                {client_info}
                
                Previous Research Findings:
                {research_findings}
                
                Your screening should include:
                1. Check against international PEP databases
                2. Identify current or former political positions
                3. Check for family members or close associates who are PEPs
                4. Verify time periods of political exposure
                5. Assess the level of political influence
                6. Check multiple jurisdictions and spelling variations
                
                Consider both domestic and foreign PEP status.
            """),
            expected_output=dedent("""
                A comprehensive PEP screening report containing:
                - PEP status determination (Yes/No/Inconclusive)
                - Details of any political positions held
                - Jurisdictions of political exposure
                - Family members or associates with PEP status
                - Time periods of political involvement
                - Level of political influence assessment
                - Required enhanced due diligence measures if PEP
                - Database sources checked and results
            """),
            agent=agent
        )

    def check_sanctions_lists(self, agent, client_info):
        return Task(
            description=dedent(f"""
                Screen the following client against all relevant sanctions lists:
                
                Client Information:
                {client_info}
                
                Perform screening against:
                1. SECO (Swiss) sanctions list
                2. EU consolidated sanctions list
                3. OFAC (US) sanctions list
                4. UN Security Council sanctions list
                5. UK HM Treasury sanctions list
                6. Other relevant international sanctions
                
                Use fuzzy matching to catch name variations and check for:
                - Direct matches
                - Partial matches
                - Associated entities
                - Beneficial ownership connections
            """),
            expected_output=dedent("""
                A detailed sanctions screening report containing:
                - Sanctions screening results (Clear/Match/Potential Match)
                - Details of any matches or potential matches
                - Sanctions lists checked with dates
                - Matching methodology used
                - Risk assessment of any partial matches
                - Recommendations for handling matches
                - Documentation of the screening process
            """),
            agent=agent
        )

    def assess_client_risk(self, agent, client_info, all_findings):
        return Task(
            description=dedent(f"""
                Perform comprehensive risk assessment based on all gathered information:
                
                Client Information:
                {client_info}
                
                All Previous Findings:
                {all_findings}
                
                Assess risk factors including:
                1. Geographic risk (residence, nationality, business locations)
                2. Product/service risk
                3. Industry/sector risk
                4. Customer type risk
                5. Transaction/relationship risk
                6. Delivery channel risk
                
                Determine overall risk rating and due diligence requirements.
            """),
            expected_output=dedent("""
                A comprehensive risk assessment containing:
                - Overall risk rating (Low/Medium/High)
                - Detailed breakdown of risk factors
                - Scoring methodology and justification
                - Identified red flags or concerns
                - Required level of due diligence (Standard/Enhanced)
                - Recommended monitoring frequency
                - Specific risk mitigation measures
                - Documentation requirements
            """),
            agent=agent
        )

    def compile_kyc_report(self, agent, client_info, all_assessments):
        return Task(
            description=dedent(f"""
                Compile a comprehensive KYC compliance report for:
                
                Client Information:
                {client_info}
                
                All Assessment Results:
                {all_assessments}
                
                Create a report that includes:
                1. Executive summary with recommendation
                2. Client identification and verification summary
                3. Background research findings
                4. PEP screening results
                5. Sanctions screening results
                6. Risk assessment and classification
                7. Required documentation checklist
                8. Ongoing monitoring requirements
                9. Approval recommendations
                
                Ensure the report meets Swiss banking regulatory standards.
            """),
            expected_output=dedent("""
                A complete KYC compliance report containing:
                - Executive summary with clear onboarding recommendation
                - Detailed findings from all screening processes
                - Risk classification and justification
                - Documentation status and requirements
                - Conditions for account opening (if applicable)
                - Ongoing monitoring and review schedule
                - Compliance officer notes and observations
                - Sign-off section for approvals
                - Appendices with supporting documentation
            """),
            agent=agent
        )
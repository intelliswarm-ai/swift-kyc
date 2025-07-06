import json
from typing import Dict, List, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from datetime import datetime


class RiskAssessmentInput(BaseModel):
    client_data: Dict = Field(..., description="Complete client information and findings")
    pep_status: str = Field(..., description="PEP screening result")
    sanctions_status: str = Field(..., description="Sanctions screening result")
    negative_news: Optional[List[str]] = Field(default_factory=list, description="List of negative news findings")


class RiskAssessmentTool(BaseTool):
    name: str = "Risk Assessment Calculator"
    description: str = """
    Calculates comprehensive risk scores based on multiple factors including
    geographic risk, product risk, customer type, PEP status, sanctions hits,
    and other KYC findings. Provides detailed risk breakdown and recommendations.
    """
    args_schema: type[BaseModel] = RiskAssessmentInput

    def _get_risk_weights(self) -> Dict[str, float]:
        """Get risk calculation weights"""
        return {
            'geographic': 0.25,
            'customer_type': 0.20,
            'pep_status': 0.20,
            'sanctions': 0.15,
            'negative_news': 0.10,
            'business_activity': 0.10
        }
    
    def _get_country_risk_scores(self) -> Dict[str, List[str]]:
        """Get country risk classifications"""
        return {
            'high_risk': ['Iran', 'North Korea', 'Syria', 'Myanmar', 'Afghanistan'],
            'medium_risk': ['Russia', 'Pakistan', 'Turkey', 'UAE', 'China'],
            'low_risk': ['Switzerland', 'UK', 'Germany', 'Canada', 'Australia']
        }

    def _calculate_geographic_risk(self, client_data: Dict) -> Dict:
        """Calculate risk based on geographic factors"""
        country_risk_scores = self._get_country_risk_scores()
        countries = []
        
        # Extract countries from client data
        if 'nationality' in client_data:
            countries.append(client_data['nationality'])
        if 'residence_country' in client_data:
            countries.append(client_data['residence_country'])
        if 'business_countries' in client_data:
            countries.extend(client_data['business_countries'])
        
        # Calculate risk score
        max_risk = 0.2  # Default low risk
        risk_countries = []
        
        for country in countries:
            if country in country_risk_scores['high_risk']:
                max_risk = max(max_risk, 1.0)
                risk_countries.append((country, 'High'))
            elif country in country_risk_scores['medium_risk']:
                max_risk = max(max_risk, 0.6)
                risk_countries.append((country, 'Medium'))
            elif country in country_risk_scores['low_risk']:
                max_risk = max(max_risk, 0.2)
                risk_countries.append((country, 'Low'))
            else:
                max_risk = max(max_risk, 0.4)  # Unknown country - medium-low
                risk_countries.append((country, 'Unknown'))
        
        return {
            'score': max_risk,
            'factors': risk_countries,
            'assessment': 'High' if max_risk > 0.7 else 'Medium' if max_risk > 0.4 else 'Low'
        }

    def _calculate_customer_type_risk(self, client_data: Dict) -> Dict:
        """Calculate risk based on customer type"""
        risk_score = 0.3  # Default individual score
        factors = []
        
        customer_type = client_data.get('customer_type', 'individual').lower()
        
        if customer_type == 'corporate':
            risk_score = 0.5
            factors.append('Corporate entity')
            
            # Check for complex structures
            if client_data.get('complex_structure', False):
                risk_score += 0.3
                factors.append('Complex ownership structure')
            
            # Check for offshore elements
            if client_data.get('offshore_elements', False):
                risk_score += 0.2
                factors.append('Offshore components')
        
        elif customer_type == 'trust' or customer_type == 'foundation':
            risk_score = 0.7
            factors.append(f'{customer_type.capitalize()} structure')
        
        # Industry risk
        high_risk_industries = ['crypto', 'gambling', 'money_services', 'arms']
        industry = client_data.get('industry', '').lower()
        
        if any(high_risk in industry for high_risk in high_risk_industries):
            risk_score = min(risk_score + 0.3, 1.0)
            factors.append(f'High-risk industry: {industry}')
        
        return {
            'score': risk_score,
            'factors': factors,
            'assessment': 'High' if risk_score > 0.7 else 'Medium' if risk_score > 0.4 else 'Low'
        }

    def _calculate_pep_risk(self, pep_status: str) -> Dict:
        """Calculate risk based on PEP status"""
        pep_risk_mapping = {
            'Confirmed PEP': 1.0,
            'PEP Associate': 0.8,
            'Potential Match - Verification Required': 0.6,
            'Match Found': 0.7,
            'No Match': 0.0
        }
        
        risk_score = pep_risk_mapping.get(pep_status, 0.5)
        
        return {
            'score': risk_score,
            'status': pep_status,
            'assessment': 'High' if risk_score > 0.7 else 'Medium' if risk_score > 0.4 else 'Low'
        }

    def _calculate_sanctions_risk(self, sanctions_status: str) -> Dict:
        """Calculate risk based on sanctions screening"""
        sanctions_risk_mapping = {
            'Hit - Exact Match Found': 1.0,
            'Potential Hit - High Similarity': 0.9,
            'Possible Match - Manual Review Required': 0.6,
            'Clear - No Matches Found': 0.0
        }
        
        risk_score = sanctions_risk_mapping.get(sanctions_status, 0.5)
        
        return {
            'score': risk_score,
            'status': sanctions_status,
            'assessment': 'Critical' if risk_score >= 1.0 else 'High' if risk_score > 0.7 else 'Medium' if risk_score > 0.4 else 'Low'
        }

    def _calculate_negative_news_risk(self, negative_news: List[str]) -> Dict:
        """Calculate risk based on negative news findings"""
        if not negative_news:
            return {'score': 0.0, 'count': 0, 'assessment': 'Low'}
        
        # Risk increases with number and severity of negative news
        risk_score = min(len(negative_news) * 0.2, 1.0)
        
        # Check for critical keywords
        critical_keywords = ['fraud', 'money laundering', 'terrorist', 'corruption', 'criminal']
        critical_found = []
        
        for news in negative_news:
            for keyword in critical_keywords:
                if keyword in news.lower():
                    risk_score = min(risk_score + 0.3, 1.0)
                    critical_found.append(keyword)
        
        return {
            'score': risk_score,
            'count': len(negative_news),
            'critical_keywords': list(set(critical_found)),
            'assessment': 'High' if risk_score > 0.7 else 'Medium' if risk_score > 0.4 else 'Low'
        }

    def _calculate_overall_risk(self, risk_components: Dict) -> Dict:
        """Calculate overall risk score and classification"""
        risk_weights = self._get_risk_weights()
        weighted_score = 0
        
        for component, weight in risk_weights.items():
            if component in risk_components:
                weighted_score += risk_components[component]['score'] * weight
        
        # Determine risk classification
        if weighted_score >= 0.7:
            classification = 'High Risk'
            due_diligence = 'Enhanced Due Diligence Required'
        elif weighted_score >= 0.4:
            classification = 'Medium Risk'
            due_diligence = 'Standard Due Diligence with Additional Checks'
        else:
            classification = 'Low Risk'
            due_diligence = 'Standard Due Diligence'
        
        return {
            'overall_score': round(weighted_score, 3),
            'classification': classification,
            'due_diligence_level': due_diligence
        }

    def _run(self, client_data: Dict, pep_status: str, sanctions_status: str,
             negative_news: Optional[List[str]] = None) -> str:
        
        if negative_news is None:
            negative_news = []
        
        # Calculate individual risk components
        risk_components = {
            'geographic': self._calculate_geographic_risk(client_data),
            'customer_type': self._calculate_customer_type_risk(client_data),
            'pep_status': self._calculate_pep_risk(pep_status),
            'sanctions': self._calculate_sanctions_risk(sanctions_status),
            'negative_news': self._calculate_negative_news_risk(negative_news)
        }
        
        # Add business activity risk if available
        if 'business_activities' in client_data:
            risk_components['business_activity'] = {
                'score': 0.3,  # Default medium-low
                'factors': client_data['business_activities'],
                'assessment': 'Medium'
            }
        
        # Calculate overall risk
        overall_risk = self._calculate_overall_risk(risk_components)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(overall_risk, risk_components)
        
        # Prepare result
        result = {
            'timestamp': datetime.now().isoformat(),
            'risk_components': risk_components,
            'overall_risk': overall_risk,
            'recommendations': recommendations,
            'monitoring_frequency': self._get_monitoring_frequency(overall_risk['classification']),
            'approval_requirements': self._get_approval_requirements(overall_risk['classification'])
        }
        
        return json.dumps(result, indent=2)

    def _generate_recommendations(self, overall_risk: Dict, risk_components: Dict) -> List[str]:
        """Generate specific recommendations based on risk assessment"""
        recommendations = []
        
        # Overall risk recommendations
        if overall_risk['classification'] == 'High Risk':
            recommendations.append("Require senior management approval for onboarding")
            recommendations.append("Conduct enhanced due diligence including source of wealth verification")
            recommendations.append("Implement transaction monitoring with lower thresholds")
        
        # Component-specific recommendations
        if risk_components['geographic']['assessment'] == 'High':
            recommendations.append("Verify business rationale for high-risk country connections")
            recommendations.append("Obtain additional documentation for cross-border activities")
        
        if risk_components['pep_status']['score'] > 0:
            recommendations.append("Obtain senior management approval for PEP relationship")
            recommendations.append("Establish source of wealth and source of funds")
            recommendations.append("Conduct annual reviews of PEP status")
        
        if risk_components['sanctions']['score'] > 0.5:
            recommendations.append("Escalate to compliance team for sanctions review")
            recommendations.append("Do not proceed without compliance clearance")
        
        if risk_components['negative_news']['score'] > 0.4:
            recommendations.append("Investigate negative news findings in detail")
            recommendations.append("Request explanation from client regarding adverse media")
        
        return recommendations

    def _get_monitoring_frequency(self, risk_classification: str) -> str:
        """Determine ongoing monitoring frequency based on risk"""
        monitoring_map = {
            'High Risk': 'Quarterly review with continuous transaction monitoring',
            'Medium Risk': 'Semi-annual review with standard transaction monitoring',
            'Low Risk': 'Annual review with standard transaction monitoring'
        }
        return monitoring_map.get(risk_classification, 'Annual review')

    def _get_approval_requirements(self, risk_classification: str) -> List[str]:
        """Determine approval requirements based on risk"""
        if risk_classification == 'High Risk':
            return ['Compliance Officer', 'Senior Management', 'Risk Committee']
        elif risk_classification == 'Medium Risk':
            return ['Compliance Officer', 'Department Head']
        else:
            return ['Standard Approval Process']

    async def _arun(self, client_data: Dict, pep_status: str, sanctions_status: str,
                    negative_news: Optional[List[str]] = None) -> str:
        return self._run(client_data, pep_status, sanctions_status, negative_news)
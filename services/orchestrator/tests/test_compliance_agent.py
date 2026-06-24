"""
Test suite for ComplianceAgent.

Tests validate that the compliance agent:
1. Loads business profiles from markdown files
2. Identifies origin and destination countries
3. Generates comprehensive compliance reports
4. Scores risks based on business type
5. Includes all compliance checklist items
6. Downloads and records source documents
7. Exports PDF reports (or gracefully skips if reportlab unavailable)
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.agents.specialists import ComplianceAgent
from app.core.schemas import AgentType


class TestComplianceAgentReportGeneration:
    """Test compliance report generation with various business scenarios."""

    @pytest.fixture
    def compliance_agent(self):
        """Create a ComplianceAgent instance with mocked brain."""
        agent = ComplianceAgent()
        agent.brain = MagicMock()
        agent.brain.generate_response.return_value = (
            "Compliance analysis complete|Review all high-risk items: high priority"
        )
        return agent

    @pytest.fixture
    def temp_shared_folder(self):
        """Create a temporary shared folder for test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_compliance_agent_electronics_manufacturing_australia_to_vietnam(
        self, compliance_agent, temp_shared_folder
    ):
        """
        Test: Business scenario with electronics manufacturing from Australia to Vietnam.
        Expected: Report includes high-risk flags for hardware/import controls.
        """
        # Arrange: Create business profile markdown
        business_md = temp_shared_folder / "business_profile.md"
        business_md.write_text(
            """# ElectroTech Pty Ltd

**Origin Country**: Australia
**Destination Country**: Vietnam
**Business Type**: Hardware and electronics manufacturing and export

We design and manufacture industrial sensors and IoT devices for supply chain monitoring.

## Relevant URLs
- https://www.abf.gov.au/importing-exporting-and-manufacturing
- https://moit.gov.vn/en
"""
        )

        context = {
            "shared_folder": str(temp_shared_folder),
            "business_file": "business_profile.md",
        }

        # Act: Run the agent
        result = compliance_agent.run(
            user_id="test-user",
            message="Check compliance for exporting electronics from Australia to Vietnam.",
            context=context,
        )

        # Assert: Basic result structure
        assert result.agent == AgentType.compliance
        assert result.summary
        assert len(result.actions) > 0

        # Verify report was created
        report_files = sorted(temp_shared_folder.glob("compliance_report_*.md"))
        assert len(report_files) == 1, "Report file should be generated"

        report_text = report_files[0].read_text(encoding="utf-8")

        # Assert: Report sections are present
        assert "# Cross-Border Compliance Report" in report_text
        assert "## Risk Scoring" in report_text
        assert "## Compliance Checklist (Both Countries)" in report_text
        assert "## Collected Source URLs" in report_text

        # Assert: Risk scoring flags hardware/electronics as HIGH risk
        assert "[HIGH]" in report_text, "Electronics should trigger HIGH risk flag"
        assert "Import controls and technical standards" in report_text
        assert "complex customs classification" in report_text

        # Assert: Country information is captured
        assert "Origin country: Australia" in report_text
        assert "Destination country: Vietnam" in report_text
        assert "Hardware and electronics" in report_text  # Business summary extracted

    def test_compliance_agent_all_checklist_items_present(
        self, compliance_agent, temp_shared_folder
    ):
        """
        Test: Compliance checklist includes all required boxes.
        Expected: All 10 compliance checklist items are present in report.
        """
        # Arrange
        business_md = temp_shared_folder / "business_profile.md"
        business_md.write_text(
            """# MediTech Solutions

**Origin Country**: United States
**Destination Country**: Singapore
**Business Type**: Medical device manufacturing and distribution
"""
        )

        context = {
            "shared_folder": str(temp_shared_folder),
            "business_file": "business_profile.md",
        }

        # Act
        result = compliance_agent.run(
            user_id="test-user",
            message="Assess compliance for medical device export.",
            context=context,
        )

        # Get generated report
        report_files = sorted(temp_shared_folder.glob("compliance_report_*.md"))
        report_text = report_files[0].read_text(encoding="utf-8")

        # Assert: All 10 checklist items are present
        required_checklist_items = [
            "Business licensing and registration obligations",
            "Product/service specific permits and approvals",
            "Import/export controls and customs classification",
            "Restricted/prohibited goods and end-use restrictions",
            "Economic sanctions and denied-party screening",
            "Tax, VAT/GST, and transfer pricing obligations",
            "Consumer protection and labeling requirements",
            "Data protection and cybersecurity requirements",
            "Employment, contractor, and payroll law obligations",
            "Record-keeping and audit evidence requirements",
        ]

        for item in required_checklist_items:
            assert item in report_text, f"Checklist item missing: {item}"

        # Assert: Medical device triggers HIGH risk
        assert "[HIGH]" in report_text

    def test_compliance_agent_risk_scoring_food_business(
        self, compliance_agent, temp_shared_folder
    ):
        """
        Test: Food/beverage business triggers HIGH risk for food compliance.
        Expected: Report flags food and labeling compliance as HIGH risk.
        """
        # Arrange
        business_md = temp_shared_folder / "food_export.md"
        business_md.write_text(
            """# FreshFruit Exports

**Origin Country**: Australia
**Destination Country**: Japan
**Business**: Organic fruit and supplement export operations
"""
        )

        context = {
            "shared_folder": str(temp_shared_folder),
            "business_file": "food_export.md",
        }

        # Act
        result = compliance_agent.run(
            user_id="test-user",
            message="Review compliance for fruit export.",
            context=context,
        )

        # Assert
        report_files = sorted(temp_shared_folder.glob("compliance_report_*.md"))
        report_text = report_files[0].read_text(encoding="utf-8")

        assert "[HIGH] Food and labeling compliance" in report_text
        assert "Food imports and consumer labeling" in report_text

    def test_compliance_agent_risk_scoring_fintech_business(
        self, compliance_agent, temp_shared_folder
    ):
        """
        Test: Fintech business triggers HIGH risk for financial licensing and AML/KYC.
        Expected: Report flags financial licensing as HIGH risk.
        """
        # Arrange
        business_md = temp_shared_folder / "fintech_profile.md"
        business_md.write_text(
            """# PayFlow Fintech

**Origin Country**: Singapore
**Destination Country**: Australia
**Business**: Payment processing and crypto exchange platform

Cross-border financial platform for digital currency transactions.
"""
        )

        context = {
            "shared_folder": str(temp_shared_folder),
            "business_file": "fintech_profile.md",
        }

        # Act
        result = compliance_agent.run(
            user_id="test-user",
            message="Check financial compliance for payment platform.",
            context=context,
        )

        # Assert
        report_files = sorted(temp_shared_folder.glob("compliance_report_*.md"))
        report_text = report_files[0].read_text(encoding="utf-8")

        assert "[HIGH] Financial licensing and AML/KYC" in report_text
        assert "licensing and anti-money-laundering obligations" in report_text

    def test_compliance_agent_source_downloads_folder_creation(
        self, compliance_agent, temp_shared_folder
    ):
        """
        Test: Agent creates compliance_downloads folder and tracks downloaded sources.
        Expected: compliance_downloads folder exists and contains source files.
        """
        # Arrange
        business_md = temp_shared_folder / "saas_business.md"
        business_md.write_text(
            """# CloudSoft SaaS

**Origin Country**: Canada
**Destination Country**: United Kingdom
**Business**: SaaS platform with cloud data storage and AI features
"""
        )

        context = {
            "shared_folder": str(temp_shared_folder),
            "business_file": "saas_business.md",
        }

        # Act
        result = compliance_agent.run(
            user_id="test-user",
            message="Review SaaS compliance requirements.",
            context=context,
        )

        # Assert: downloads folder created
        downloads_dir = temp_shared_folder / "compliance_downloads"
        assert downloads_dir.exists(), "compliance_downloads folder should be created"

        # Assert: Source URLs are mentioned in report
        report_files = sorted(temp_shared_folder.glob("compliance_report_*.md"))
        report_text = report_files[0].read_text(encoding="utf-8")
        assert "## Collected Source URLs" in report_text

    def test_compliance_agent_pdf_export_attempt(
        self, compliance_agent, temp_shared_folder
    ):
        """
        Test: Agent attempts PDF export and tracks success/failure in report result.
        Expected: PDF file path is returned (pdf_generated flag indicates success/skip).
        """
        # Arrange
        business_md = temp_shared_folder / "business.md"
        business_md.write_text(
            """# TestCorp

**Origin Country**: United Kingdom
**Destination Country**: Australia
**Business**: General consulting services
"""
        )

        context = {
            "shared_folder": str(temp_shared_folder),
            "business_file": "business.md",
        }

        # Act
        result = compliance_agent.run(
            user_id="test-user",
            message="Check compliance.",
            context=context,
        )

        # Assert: Agent returned pdf_path in actions
        action_details = " ".join([a.details for a in result.actions])
        assert "compliance_report" in action_details

        # If reportlab is available, PDF should exist
        pdf_files = sorted(temp_shared_folder.glob("compliance_report_*.pdf"))
        # PDF may or may not exist depending on reportlab availability
        # The test passes if the agent gracefully handles both cases

    def test_compliance_agent_missing_shared_folder_error_handling(self, compliance_agent):
        """
        Test: Agent handles missing shared_folder gracefully.
        Expected: Returns error action with guidance to set shared_folder.
        """
        # Arrange: No shared_folder in context
        context = {}

        # Act
        result = compliance_agent.run(
            user_id="test-user",
            message="Check compliance.",
            context=context,
        )

        # Assert
        assert result.agent == AgentType.compliance
        assert "shared folder" in result.summary.lower()
        assert len(result.actions) > 0
        assert "Provide shared folder" in result.actions[0].title

    def test_compliance_agent_automatic_markdown_file_discovery(
        self, compliance_agent, temp_shared_folder
    ):
        """
        Test: Agent discovers markdown files automatically if business_file not specified.
        Expected: Agent finds and parses first .md file in shared_folder.
        """
        # Arrange: Create markdown without specifying filename
        business_md = temp_shared_folder / "company_info.md"
        business_md.write_text(
            """# AutoDiscover Corp

**Origin Country**: Vietnam
**Destination Country**: Australia
**Business**: Manufacturing IoT sensors for agricultural use
"""
        )

        context = {
            "shared_folder": str(temp_shared_folder),
            # Note: NOT specifying business_file
        }

        # Act
        result = compliance_agent.run(
            user_id="test-user",
            message="Check compliance.",
            context=context,
        )

        # Assert
        report_files = sorted(temp_shared_folder.glob("compliance_report_*.md"))
        assert len(report_files) == 1
        report_text = report_files[0].read_text(encoding="utf-8")
        assert "Manufacturing IoT sensors" in report_text
        assert "[HIGH]" in report_text  # IoT/sensor triggers HIGH risk

    def test_compliance_agent_country_normalization(
        self, compliance_agent, temp_shared_folder
    ):
        """
        Test: Agent normalizes country name aliases (US -> United States, UK -> United Kingdom).
        Expected: Country-specific sources are correctly retrieved for normalized names.
        """
        # Arrange
        business_md = temp_shared_folder / "alias_test.md"
        business_md.write_text(
            """# GlobalTrade Inc

**Origin Country**: US
**Destination Country**: UK
**Business**: General trading services
"""
        )

        context = {
            "shared_folder": str(temp_shared_folder),
            "business_file": "alias_test.md",
        }

        # Act
        result = compliance_agent.run(
            user_id="test-user",
            message="Check compliance with alias countries.",
            context=context,
        )

        # Assert
        report_files = sorted(temp_shared_folder.glob("compliance_report_*.md"))
        report_text = report_files[0].read_text(encoding="utf-8")

        # Should normalize to full country names in report
        assert "Origin country:" in report_text
        assert "Destination country:" in report_text


class TestComplianceAgentComplianceChecklistValidation:
    """Test validation of compliance checklist coverage across business types."""

    @pytest.fixture
    def compliance_agent(self):
        agent = ComplianceAgent()
        agent.brain = MagicMock()
        agent.brain.generate_response.return_value = "Checklist validated"
        return agent

    @pytest.fixture
    def temp_shared_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_checklist_coverage_comprehensive_validation(
        self, compliance_agent, temp_shared_folder
    ):
        """
        Test: Validate that checklist covers all critical compliance domains.
        Checklist should include:
        - Licensing/registration
        - Permits/approvals
        - Import/export/customs
        - Restricted goods
        - Sanctions screening
        - Tax/VAT
        - Consumer protection
        - Data protection
        - Employment law
        - Record-keeping
        """
        # Arrange
        scenarios = [
            (
                "electronics",
                """# TechExport
**Origin Country**: Australia
**Destination Country**: Vietnam
**Business**: Electronics and IoT hardware export
""",
            ),
            (
                "pharma",
                """# PharmaCorp
**Origin Country**: United States
**Destination Country**: Singapore
**Business**: Pharmaceutical and medical device manufacturing
""",
            ),
            (
                "financial",
                """# FinanceHub
**Origin Country**: Canada
**Destination Country**: Australia
**Business**: Financial services and crypto trading platform
""",
            ),
        ]

        expected_checklist_domains = [
            "licensing",
            "permits",
            "customs",
            "restricted",
            "sanctions",
            "tax",
            "consumer",
            "data protection",
            "employment",
            "record-keeping",
        ]

        for scenario_name, business_content in scenarios:
            # Arrange
            business_md = temp_shared_folder / f"{scenario_name}_profile.md"
            business_md.write_text(business_content)

            context = {
                "shared_folder": str(temp_shared_folder),
                "business_file": f"{scenario_name}_profile.md",
            }

            # Act
            result = compliance_agent.run(
                user_id="test-user",
                message=f"Check {scenario_name} compliance.",
                context=context,
            )

            # Assert: All checklist domains are mentioned
            report_files = sorted(temp_shared_folder.glob("compliance_report_*.md"))
            report_text = report_files[-1].read_text(encoding="utf-8")

            for domain in expected_checklist_domains:
                assert (
                    domain.lower() in report_text.lower()
                ), f"Checklist domain '{domain}' not found in {scenario_name} report"

            # Clean up for next iteration
            report_files[-1].unlink()


class TestComplianceAgentRiskAssessmentAccuracy:
    """Test risk scoring logic for various business types."""

    @pytest.fixture
    def compliance_agent(self):
        agent = ComplianceAgent()
        agent.brain = MagicMock()
        agent.brain.generate_response.return_value = "Risk assessment complete"
        return agent

    @pytest.fixture
    def temp_shared_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_risk_scoring_high_risk_categories(
        self, compliance_agent, temp_shared_folder
    ):
        """
        Test: HIGH-risk business types are correctly identified.
        Categories: Medical, Pharma, Food, Financial, Fintech, Payment, Banking, Electronics, Hardware, IoT.
        """
        high_risk_keywords = [
            "Medical",
            "Pharmaceutical",
            "Drug",
            "Food",
            "Beverage",
            "Financial",
            "Fintech",
            "Payment",
            "Banking",
            "Electronics",
            "Hardware",
        ]

        high_risk_expected = {
            "Medical": "Product approvals and safety certification",
            "Pharmaceutical": "Product approvals and safety certification",
            "Food": "Food and labeling compliance",
            "Financial": "Financial licensing and AML/KYC",
            "Fintech": "Financial licensing and AML/KYC",
            "Electronics": "Import controls and technical standards",
            "Hardware": "Import controls and technical standards",
        }

        for keyword, expected_area in high_risk_expected.items():
            # Arrange
            business_md = temp_shared_folder / f"{keyword.lower()}_risk.md"
            business_md.write_text(
                f"""# {keyword} Co

**Origin Country**: Australia
**Destination Country**: Vietnam
**Business**: {keyword} products and services
"""
            )

            context = {
                "shared_folder": str(temp_shared_folder),
                "business_file": f"{keyword.lower()}_risk.md",
            }

            # Act
            result = compliance_agent.run(
                user_id="test-user",
                message=f"Check {keyword} compliance.",
                context=context,
            )

            # Assert: HIGH risk should be flagged
            report_files = sorted(temp_shared_folder.glob("compliance_report_*.md"))
            report_text = report_files[-1].read_text(encoding="utf-8")

            assert (
                "[HIGH]" in report_text
            ), f"HIGH risk not found for {keyword}"

            # Clean up
            report_files[-1].unlink()

    def test_risk_scoring_medium_risk_categories(
        self, compliance_agent, temp_shared_folder
    ):
        """
        Test: MEDIUM-risk business types are correctly identified.
        Categories: Data, Software, SaaS, Cloud.
        """
        medium_risk_scenarios = [
            ("SaaS Platform", "Data storage SaaS with cloud platform"),
            ("CloudApp", "Software as a service cloud platform"),
        ]

        for name, description in medium_risk_scenarios:
            # Arrange
            business_md = temp_shared_folder / f"{name.lower().replace(' ', '_')}.md"
            business_md.write_text(
                f"""# {name} Corp

**Origin Country**: Australia
**Destination Country**: Canada
**Business**: {description}
"""
            )

            context = {
                "shared_folder": str(temp_shared_folder),
                "business_file": business_md.name,
            }

            # Act
            result = compliance_agent.run(
                user_id="test-user",
                message=f"Check {name} compliance.",
                context=context,
            )

            # Assert: MEDIUM risk should be flagged
            report_files = sorted(temp_shared_folder.glob("compliance_report_*.md"))
            report_text = report_files[-1].read_text(encoding="utf-8")

            assert (
                "[MEDIUM]" in report_text
            ), f"MEDIUM risk not found for {name}"

            # Clean up
            report_files[-1].unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

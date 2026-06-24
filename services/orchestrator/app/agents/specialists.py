import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from app.agents.base import BaseAgent
from app.core.schemas import AgentAction, AgentResult, AgentType


class PlannerAgent(BaseAgent):
    agent_type = AgentType.planner

    @property
    def system_prompt(self) -> str:
        return (
            "You are a planning expert. Analyze the user's goal and provide a concise summary "
            "(1-2 sentences) of the practical plan. Format response as: SUMMARY|ACTION1|ACTION2 "
            "where each action is 'Title: Details (priority)'."
        )

    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        if self.brain:
            try:
                response = self.brain.generate_response(self.system_prompt, message, context)
                return self._parse_response(response)
            except Exception:
                pass
        return self._fallback_response()

    def _parse_response(self, response: str) -> AgentResult:
        parts = response.split("|")
        summary = parts[0].strip() if len(parts) > 0 else "Created a practical plan."
        actions = []
        for part in parts[1:]:
            if ":" in part:
                title, rest = part.split(":", 1)
                priority = "medium"
                if "(high)" in rest:
                    priority = "high"
                    rest = rest.replace("(high)", "")
                elif "(low)" in rest:
                    priority = "low"
                    rest = rest.replace("(low)", "")
                actions.append(AgentAction(title=title.strip(), details=rest.strip(), priority=priority))
        if not actions:
            actions = self._fallback_response().actions
        return AgentResult(agent=self.agent_type, summary=summary, actions=actions)

    def _fallback_response(self) -> AgentResult:
        return AgentResult(
            agent=self.agent_type,
            summary="Created a practical plan with milestones.",
            actions=[
                AgentAction(title="Define weekly goals", details="Break the goal into 3 concrete outcomes."),
                AgentAction(title="Schedule deep work", details="Reserve 90-minute blocks for high-priority work."),
            ],
        )


class CalendarAgent(BaseAgent):
    agent_type = AgentType.calendar

    @property
    def system_prompt(self) -> str:
        return (
            "You are a scheduling expert. Provide a concise summary (1-2 sentences) of scheduling recommendations. "
            "Format: SUMMARY|ACTION1|ACTION2 where each action is 'Title: Details (priority)'."
        )

    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        if self.brain:
            try:
                response = self.brain.generate_response(self.system_prompt, message, context)
                return self._parse_response(response)
            except Exception:
                pass
        return self._fallback_response()

    def _parse_response(self, response: str) -> AgentResult:
        parts = response.split("|")
        summary = parts[0].strip() if len(parts) > 0 else "Prepared scheduling recommendations."
        actions = []
        for part in parts[1:]:
            if ":" in part:
                title, rest = part.split(":", 1)
                priority = "medium"
                if "(high)" in rest:
                    priority = "high"
                    rest = rest.replace("(high)", "")
                elif "(low)" in rest:
                    priority = "low"
                    rest = rest.replace("(low)", "")
                actions.append(AgentAction(title=title.strip(), details=rest.strip(), priority=priority))
        if not actions:
            actions = self._fallback_response().actions
        return AgentResult(agent=self.agent_type, summary=summary, actions=actions)

    def _fallback_response(self) -> AgentResult:
        return AgentResult(
            agent=self.agent_type,
            summary="Prepared scheduling recommendations.",
            actions=[
                AgentAction(title="Focus block", details="Add one morning focus block tomorrow.", priority="high"),
                AgentAction(title="Buffer time", details="Add 15-minute buffers between meetings."),
            ],
        )


class FinanceAgent(BaseAgent):
    agent_type = AgentType.finance

    @property
    def system_prompt(self) -> str:
        return (
            "You are a financial advisor. Provide a concise summary (1-2 sentences) of budget-focused actions. "
            "Format: SUMMARY|ACTION1|ACTION2 where each action is 'Title: Details (priority)'."
        )

    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        if self.brain:
            try:
                response = self.brain.generate_response(self.system_prompt, message, context)
                return self._parse_response(response)
            except Exception:
                pass
        return self._fallback_response()

    def _parse_response(self, response: str) -> AgentResult:
        parts = response.split("|")
        summary = parts[0].strip() if len(parts) > 0 else "Generated budget-focused next actions."
        actions = []
        for part in parts[1:]:
            if ":" in part:
                title, rest = part.split(":", 1)
                priority = "medium"
                if "(high)" in rest:
                    priority = "high"
                    rest = rest.replace("(high)", "")
                elif "(low)" in rest:
                    priority = "low"
                    rest = rest.replace("(low)", "")
                actions.append(AgentAction(title=title.strip(), details=rest.strip(), priority=priority))
        if not actions:
            actions = self._fallback_response().actions
        return AgentResult(agent=self.agent_type, summary=summary, actions=actions)

    def _fallback_response(self) -> AgentResult:
        return AgentResult(
            agent=self.agent_type,
            summary="Generated budget-focused next actions.",
            actions=[
                AgentAction(title="Track top expenses", details="Tag the top 5 expense categories this week."),
                AgentAction(title="Savings rule", details="Set an automatic transfer to savings after payday."),
            ],
        )


class WellnessAgent(BaseAgent):
    agent_type = AgentType.wellness

    @property
    def system_prompt(self) -> str:
        return (
            "You are a wellness coach. Provide a concise summary (1-2 sentences) of balanced wellbeing actions. "
            "Format: SUMMARY|ACTION1|ACTION2 where each action is 'Title: Details (priority)'."
        )

    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        if self.brain:
            try:
                response = self.brain.generate_response(self.system_prompt, message, context)
                return self._parse_response(response)
            except Exception:
                pass
        return self._fallback_response()

    def _parse_response(self, response: str) -> AgentResult:
        parts = response.split("|")
        summary = parts[0].strip() if len(parts) > 0 else "Built a balanced wellbeing action list."
        actions = []
        for part in parts[1:]:
            if ":" in part:
                title, rest = part.split(":", 1)
                priority = "medium"
                if "(high)" in rest:
                    priority = "high"
                    rest = rest.replace("(high)", "")
                elif "(low)" in rest:
                    priority = "low"
                    rest = rest.replace("(low)", "")
                actions.append(AgentAction(title=title.strip(), details=rest.strip(), priority=priority))
        if not actions:
            actions = self._fallback_response().actions
        return AgentResult(agent=self.agent_type, summary=summary, actions=actions)

    def _fallback_response(self) -> AgentResult:
        return AgentResult(
            agent=self.agent_type,
            summary="Built a balanced wellbeing action list.",
            actions=[
                AgentAction(title="Daily walk", details="Schedule a 20-minute walk in daylight."),
                AgentAction(title="Sleep prep", details="Set a wind-down reminder 1 hour before bed."),
            ],
        )


class GeneralAgent(BaseAgent):
    agent_type = AgentType.general

    @property
    def system_prompt(self) -> str:
        return (
            "You are a general assistant. Provide a concise summary (1-2 sentences) and actionable next steps. "
            "Format: SUMMARY|ACTION1|ACTION2 where each action is 'Title: Details'."
        )

    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        if self.brain:
            try:
                response = self.brain.generate_response(self.system_prompt, message, context)
                return self._parse_response(response)
            except Exception:
                pass
        return self._fallback_response()

    def _parse_response(self, response: str) -> AgentResult:
        parts = response.split("|")
        summary = parts[0].strip() if len(parts) > 0 else "Handled request with a general assistant path."
        actions = []
        for part in parts[1:]:
            if ":" in part:
                title, rest = part.split(":", 1)
                priority = "medium"
                if "(high)" in rest:
                    priority = "high"
                    rest = rest.replace("(high)", "")
                elif "(low)" in rest:
                    priority = "low"
                    rest = rest.replace("(low)", "")
                actions.append(AgentAction(title=title.strip(), details=rest.strip(), priority=priority))
        if not actions:
            actions = self._fallback_response().actions
        return AgentResult(agent=self.agent_type, summary=summary, actions=actions)

    def _fallback_response(self) -> AgentResult:
        return AgentResult(
            agent=self.agent_type,
            summary="Handled request with a general assistant path.",
            actions=[
                AgentAction(title="Clarify objective", details="Confirm expected outcome and deadline."),
            ],
        )


class ComplianceAgent(BaseAgent):
    agent_type = AgentType.compliance

    @property
    def system_prompt(self) -> str:
        return (
            "You are a compliance analyst. Summarize cross-border compliance obligations between origin and "
            "destination countries using provided business context and source extracts. "
            "Format: SUMMARY|ACTION1|ACTION2 where each action is 'Title: Details (priority)'."
        )

    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        shared_folder = context.get("shared_folder")
        if not shared_folder:
            return AgentResult(
                agent=self.agent_type,
                summary="Compliance agent needs a shared folder path to run.",
                actions=[
                    AgentAction(
                        title="Provide shared folder",
                        details=(
                            "Set context.shared_folder to the folder that contains your business markdown file."
                        ),
                        priority="high",
                    )
                ],
            )

        try:
            run_result = self._run_collection(Path(shared_folder), context)
        except Exception as exc:
            return AgentResult(
                agent=self.agent_type,
                summary="Compliance collection failed before report generation.",
                actions=[
                    AgentAction(
                        title="Fix shared folder inputs",
                        details=f"Error: {exc}",
                        priority="high",
                    )
                ],
            )

        summary = run_result["summary"]
        actions = [
            AgentAction(
                title="Review generated report",
                details=f"Open: {run_result['report_path']}",
                priority="high",
            ),
            AgentAction(
                title="Review PDF export",
                details=(
                    f"Open: {run_result['pdf_path']}"
                    if run_result.get("pdf_generated")
                    else "PDF export skipped (reportlab not installed)."
                ),
                priority="medium",
            ),
        ]

        if run_result.get("resources_archive_path"):
            actions.append(
                AgentAction(
                    title="Download collected resources",
                    details=f"Open: {run_result['resources_archive_path']}",
                    priority="medium",
                )
            )
        else:
            actions.append(
                AgentAction(
                    title="Validate source captures",
                    details=(
                        f"Downloaded {run_result['download_count']} source files to "
                        f"{run_result['downloads_dir']}"
                    ),
                    priority="medium",
                )
            )

        if self.brain:
            try:
                brain_context = {
                    "origin_country": run_result["origin_country"],
                    "destination_country": run_result["destination_country"],
                    "business_summary": run_result["business_summary"],
                    "downloaded_sources": run_result["downloaded_sources"],
                    "report_path": run_result["report_path"],
                }
                response = self.brain.generate_response(self.system_prompt, message, brain_context)
                parsed = self._parse_response(response)
                parsed.actions.extend(actions)
                return parsed
            except Exception:
                pass

        return AgentResult(agent=self.agent_type, summary=summary, actions=actions)

    def _parse_response(self, response: str) -> AgentResult:
        parts = response.split("|")
        summary = parts[0].strip() if len(parts) > 0 else "Compliance review prepared."
        actions: list[AgentAction] = []
        for part in parts[1:]:
            if ":" not in part:
                continue
            title, rest = part.split(":", 1)
            priority = "medium"
            if "(high)" in rest:
                priority = "high"
                rest = rest.replace("(high)", "")
            elif "(low)" in rest:
                priority = "low"
                rest = rest.replace("(low)", "")
            actions.append(AgentAction(title=title.strip(), details=rest.strip(), priority=priority))
        if not actions:
            actions = [
                AgentAction(
                    title="Review compliance report",
                    details="Open the generated report and confirm high-risk items.",
                    priority="high",
                )
            ]
        return AgentResult(agent=self.agent_type, summary=summary, actions=actions)

    def _run_collection(self, shared_folder: Path, context: dict) -> dict:
        if not shared_folder.exists() or not shared_folder.is_dir():
            raise ValueError(f"shared_folder does not exist or is not a folder: {shared_folder}")

        business_file = context.get("business_file")
        if business_file:
            md_path = shared_folder / business_file
        else:
            md_files = sorted(shared_folder.glob("*.md"))
            txt_files = sorted(shared_folder.glob("*.txt"))
            candidate_files = md_files + txt_files
            if not candidate_files:
                raise ValueError("No .md or .txt files found in shared folder.")
            md_path = candidate_files[0]

        if not md_path.exists() or not md_path.is_file():
            raise ValueError(f"Business file not found: {md_path}")

        raw_text = md_path.read_text(encoding="utf-8", errors="ignore")
        parsed = self._parse_business_markdown(raw_text)

        report_folder = md_path.parent
        downloads_dir = report_folder / "compliance_downloads"
        downloads_dir.mkdir(exist_ok=True)

        source_urls = list(parsed["urls"])
        context_urls = context.get("source_urls") or []
        source_urls.extend([u for u in context_urls if isinstance(u, str)])
        source_urls.extend(
            self._country_specific_sources(
                parsed["origin_country"],
                parsed["destination_country"],
            )
        )
        source_urls.extend(self._default_global_sources())
        source_urls = self._dedupe_urls(source_urls)

        downloaded_sources = []
        for idx, url in enumerate(source_urls, start=1):
            downloaded_file = self._download_source(url, downloads_dir, idx)
            if downloaded_file:
                downloaded_sources.append(str(downloaded_file))

        local_reference_docs = []
        for candidate in sorted(report_folder.iterdir()):
            if not candidate.is_file():
                continue
            if candidate.resolve() == md_path.resolve():
                continue
            if candidate.name.startswith("compliance_report_"):
                continue
            local_reference_docs.append(str(candidate))

        evidence_files = [str(md_path), *downloaded_sources, *local_reference_docs]

        now = datetime.now(timezone.utc)
        report_name = f"compliance_report_{now.strftime('%Y%m%d_%H%M%S')}.md"
        report_path = report_folder / report_name
        report_text = self._build_report(
            parsed=parsed,
            downloaded_sources=downloaded_sources,
            local_reference_docs=local_reference_docs,
            evidence_files=evidence_files,
            source_urls=source_urls,
            report_generated_at=now.isoformat(),
            business_file=str(md_path),
        )
        report_path.write_text(report_text, encoding="utf-8")

        pdf_path = report_folder / report_name.replace(".md", ".pdf")
        pdf_generated = self._export_pdf_report(report_text, pdf_path)
        resources_archive_path = self._build_resources_archive(downloads_dir, report_folder, now)

        summary = (
            f"Compliance report created for {parsed['origin_country']} -> "
            f"{parsed['destination_country']} and saved to {report_path}."
        )
        return {
            "summary": summary,
            "report_path": str(report_path),
            "downloads_dir": str(downloads_dir),
            "download_count": len(downloaded_sources),
            "origin_country": parsed["origin_country"],
            "destination_country": parsed["destination_country"],
            "business_summary": parsed["business_summary"],
            "downloaded_sources": downloaded_sources,
            "pdf_path": str(pdf_path),
            "pdf_generated": pdf_generated,
            "resources_archive_path": resources_archive_path,
        }

    def _build_resources_archive(
        self,
        downloads_dir: Path,
        report_folder: Path,
        now: datetime,
    ) -> str | None:
        if not downloads_dir.exists() or not downloads_dir.is_dir():
            return None
        try:
            archive_base = report_folder / f"compliance_resources_{now.strftime('%Y%m%d_%H%M%S')}"
            archive_path = shutil.make_archive(
                str(archive_base),
                "zip",
                root_dir=str(downloads_dir),
            )
            return str(archive_path)
        except Exception:
            return None

    def _parse_business_markdown(self, text: str) -> dict:
        origin = self._find_value(text, [r"origin country", r"business country", r"from country"])
        destination = self._find_value(
            text, [r"destination country", r"to country", r"target country"]
        )
        business = self._find_value(
            text, [r"business", r"business type", r"industry", r"product", r"service"]
        )

        # If business not found by label, try to extract from unstructured text
        if not business or business == "Business description not found in markdown.":
            # Look for paragraph text that seems like business description
            lines = text.split("\n")
            for i, line in enumerate(lines):
                stripped = line.strip()
                # Skip headers, empty lines, and labeled lines
                if (
                    stripped
                    and not stripped.startswith("#")
                    and not stripped.startswith("-")
                    and ":" not in stripped[:30]
                    and not stripped.startswith("[")
                    and len(stripped) > 20
                ):
                    business = stripped
                    break

        urls = re.findall(r"https?://[^\s)\]]+", text)
        return {
            "origin_country": origin or "Unknown",
            "destination_country": destination or "Unknown",
            "business_summary": business or "Business description not found in markdown.",
            "urls": urls,
        }

    def _find_value(self, text: str, labels: list[str]) -> str | None:
        for label in labels:
            # Accept formats: "Label: value", "- Label: value", "**Label**: value"
            match = re.search(
                rf"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?(?:{label})(?:\*\*)?\s*:\s*(.+?)\s*$",
                text,
                re.MULTILINE,
            )
            if match:
                value = match.group(1).strip()
                # Remove markdown bold formatting if present
                value = value.replace("**", "").strip()
                return value
        return None

    def _default_global_sources(self) -> list[str]:
        return [
            "https://www.wto.org/english/tratop_e/tratop_e.htm",
            "https://www.trade.gov/country-commercial-guides",
            "https://www.sanctionsmap.eu/#/main",
            "https://www.worldbank.org/en/topic/trade",
        ]

    def _country_specific_sources(self, origin_country: str, destination_country: str) -> list[str]:
        source_map = {
            "australia": [
                "https://www.abf.gov.au/importing-exporting-and-manufacturing",
                "https://www.austrade.gov.au/en/how-we-can-help-you/export-services",
                "https://www.accc.gov.au/business",
            ],
            "vietnam": [
                "https://www.customs.gov.vn/index.jsp?pageId=2311&cid=4201",
                "https://moit.gov.vn/en",
            ],
            "united states": [
                "https://www.cbp.gov/trade",
                "https://www.bis.gov/export-controls",
                "https://home.treasury.gov/policy-issues/office-of-foreign-assets-control-sanctions-programs-and-information",
            ],
            "singapore": [
                "https://www.customs.gov.sg/businesses/importing-goods",
                "https://www.enterprisesg.gov.sg/",
            ],
            "united kingdom": [
                "https://www.gov.uk/topic/business-tax/import-export",
            ],
            "canada": [
                "https://www.cbsa-asfc.gc.ca/import/menu-eng.html",
                "https://www.international.gc.ca/trade-commerce/index.aspx?lang=eng",
            ],
        }

        urls = []
        for country in [origin_country, destination_country]:
            norm = self._normalize_country(country)
            urls.extend(source_map.get(norm, []))
        return urls

    def _normalize_country(self, country: str) -> str:
        norm = (country or "").strip().lower()
        aliases = {
            "usa": "united states",
            "us": "united states",
            "u.s.": "united states",
            "u.s.a.": "united states",
            "uk": "united kingdom",
            "u.k.": "united kingdom",
            "viet nam": "vietnam",
        }
        return aliases.get(norm, norm)

    def _dedupe_urls(self, urls: list[str]) -> list[str]:
        seen = set()
        ordered = []
        for url in urls:
            norm = url.strip()
            if not norm or norm in seen:
                continue
            seen.add(norm)
            ordered.append(norm)
        return ordered

    def _download_source(self, url: str, downloads_dir: Path, idx: int) -> Path | None:
        try:
            parsed = urlparse(url)
            host = (parsed.netloc or "source").replace(":", "_")
            ext = ".html"
            file_name = f"{idx:02d}_{host}{ext}"
            out_path = downloads_dir / file_name

            req = Request(
                url,
                headers={
                    "User-Agent": "multi-agent-assistant-compliance-bot/1.0",
                },
            )
            with urlopen(req, timeout=15) as res:
                content = res.read()

            out_path.write_bytes(content)
            return out_path
        except Exception:
            return None

    def _build_report(
        self,
        parsed: dict,
        downloaded_sources: list[str],
        local_reference_docs: list[str],
        evidence_files: list[str],
        source_urls: list[str],
        report_generated_at: str,
        business_file: str,
    ) -> str:
        risk_items = self._risk_assessment(parsed)

        lines = [
            "# Cross-Border Compliance Report",
            "",
            f"- Generated at (UTC): {report_generated_at}",
            f"- Business profile file: {business_file}",
            f"- Origin country: {parsed['origin_country']}",
            f"- Destination country: {parsed['destination_country']}",
            f"- Business summary: {parsed['business_summary']}",
            "",
            "## Scope",
            (
                "This report is an operational compliance working draft. It is not legal advice. "
                "Validate all requirements with licensed legal/compliance professionals in both countries."
            ),
            "",
            "## Collected Source URLs",
        ]

        if source_urls:
            lines.extend([f"- {u}" for u in source_urls])
        else:
            lines.append("- No source URLs were provided or discovered.")

        lines.extend(["", "## Downloaded Source Files"])
        if downloaded_sources:
            lines.extend([f"- {p}" for p in downloaded_sources])
        else:
            lines.append("- No files downloaded. Check connectivity and source URLs.")

        lines.extend(["", "## Provided Local Documents"])
        if local_reference_docs:
            lines.extend([f"- {p}" for p in local_reference_docs])
        else:
            lines.append("- No extra local documents were provided.")

        lines.extend(["", "## Risk Scoring"])
        if risk_items:
            for item in risk_items:
                lines.append(
                    f"- [{item['risk'].upper()}] {item['area']}: {item['reason']}"
                )
        else:
            lines.append("- [MEDIUM] General compliance baseline applies.")

        lines.extend(
            [
                "",
                "## Compliance Checklist (Both Countries)",
                "- Business licensing and registration obligations",
                "- Product/service specific permits and approvals",
                "- Import/export controls and customs classification",
                "- Restricted/prohibited goods and end-use restrictions",
                "- Economic sanctions and denied-party screening",
                "- Tax, VAT/GST, and transfer pricing obligations",
                "- Consumer protection and labeling requirements",
                "- Data protection and cybersecurity requirements",
                "- Employment, contractor, and payroll law obligations",
                "- Record-keeping and audit evidence requirements",
                "",
            ]
        )

        # Add detailed Next Actions section with table
        next_actions_section = self._build_next_actions_section(
            parsed=parsed,
            risk_items=risk_items,
            evidence_files=evidence_files,
        )
        lines.extend(next_actions_section)

        return "\n".join(lines) + "\n"

    def _build_next_actions_section(
        self,
        parsed: dict,
        risk_items: list[dict],
        evidence_files: list[str],
    ) -> list[str]:
        """Build comprehensive Next Actions section with compliance mapping table."""
        lines = ["## Next Actions"]
        lines.append("")

        evidence_docs = self._load_evidence_documents(evidence_files)

        # Mapping of checklist items to country-specific laws and references
        checklist_mapping = {
            "Business licensing and registration obligations": {
                "australia": ["Australian Securities Exchange (ASX) registration", "ASIC Company Register"],
                "vietnam": ["Ministry of Planning and Investment (MPI) registration", "Tax Authority registration"],
                "united_states": ["Secretary of State business registration", "Federal Employer ID (EIN)"],
                "singapore": ["ACRA (Accounting & Corporate Regulatory Authority)", "Singapore business registration"],
                "united_kingdom": ["Companies House registration", "UK tax authority (HMRC) registration"],
                "canada": ["Corporations Canada registration", "Provincial business registration"],
            },
            "Product/service specific permits and approvals": {
                "australia": ["TGA (Therapeutic Goods Administration) for medical", "NATA accreditation", "Industry-specific permits"],
                "vietnam": ["Ministry of Health approvals", "Product quality certifications", "Import license"],
                "united_states": ["FDA (Food and Drug Administration) approvals", "FTC compliance", "Industry-specific licensing"],
                "singapore": ["HSA (Health Sciences Authority) for medical/food", "Enterprise Singapore approvals"],
                "united_kingdom": ["CMA (Competition and Markets Authority)", "Product certification marks", "Industry-specific permits"],
                "canada": ["Health Canada product approvals", "Canadian Standards Association (CSA)", "Provincial licensing"],
            },
            "Import/export controls and customs classification": {
                "australia": ["Australian Border Force (ABF) tariff classification", "Harmonized System (HS) code validation"],
                "vietnam": ["Vietnam Customs General Department (CGD)", "HS code classification"],
                "united_states": ["CBP (Customs and Border Protection) HS code", "ITAR/EAR export controls"],
                "singapore": ["Singapore Customs HS code", "Strategic goods licensing"],
                "united_kingdom": ["UK Customs tariff classification", "Post-Brexit trade procedures"],
                "canada": ["Canada Border Services Agency (CBSA) tariff classification", "HS code validation"],
            },
            "Restricted/prohibited goods and end-use restrictions": {
                "australia": ["DFAT (Dept of Foreign Affairs) restricted goods list", "Controlled export list"],
                "vietnam": ["Ministry of Industry and Trade restricted goods", "Hazardous materials regulations"],
                "united_states": ["Commerce Control List (CCL)", "Entity List screening", "ITAR restrictions"],
                "singapore": ["STGM (Strategic Goods Control) list", "Controlled items schedule"],
                "united_kingdom": ["UK Strategic Export Controls List", "FCDO restricted items"],
                "canada": ["Export Control List (ECL)", "ITAR-equivalent restrictions"],
            },
            "Economic sanctions and denied-party screening": {
                "australia": ["DFAT Sanctions list", "UN consolidated list screening"],
                "vietnam": ["UN and bilateral sanctions screening", "Ministry of Finance watch lists"],
                "united_states": ["OFAC (Office of Foreign Assets Control) SDN list", "BIS denied persons list"],
                "singapore": ["UN Security Council sanctions list", "Singapore MAS financial sanctions"],
                "united_kingdom": ["UK Office of Financial Sanctions Implementation (OFSI)", "EU sanctions retained list"],
                "canada": ["Global Affairs Canada sanctions list", "UNSC consolidated lists"],
            },
            "Tax, VAT/GST, and transfer pricing obligations": {
                "australia": ["ATO (Australian Tax Office) GST registration", "Transfer pricing documentation"],
                "vietnam": ["Vietnam General Department of Customs (VAT)", "Transfer pricing rules"],
                "united_states": ["IRS tax ID registration", "Transfer pricing (26 CFR 1.482)"],
                "singapore": ["IRAS (Inland Revenue Authority) GST/VAT", "Transfer pricing guidelines"],
                "united_kingdom": ["HMRC VAT registration", "UK transfer pricing regulations"],
                "canada": ["CRA (Canada Revenue Agency) GST/HST registration", "Transfer pricing rules (ITA section 247)"],
            },
            "Consumer protection and labeling requirements": {
                "australia": ["ACCC (Australian Competition & Consumer Commission)", "Australian Consumer Law labeling requirements"],
                "vietnam": ["Vietnam Ministry of Industry and Trade consumer protection", "Labeling standards"],
                "united_states": ["FTC (Federal Trade Commission) labeling", "State-level consumer protection"],
                "singapore": ["CCCS (Competition and Consumer Commission of Singapore)", "Consumer Protection (Fair Trading) Act"],
                "united_kingdom": ["CMA consumer protection regulations", "Advertising Standards Authority"],
                "canada": ["Competition Act (consumer protection)", "Consumer Packaging and Labeling Act"],
            },
            "Data protection and cybersecurity requirements": {
                "australia": ["Privacy Act 1988 (Australian Personal Data)", "Notifiable Data Breaches scheme"],
                "vietnam": ["Law on Cybersecurity (2018)", "Data localization requirements"],
                "united_states": ["State privacy laws (CCPA, etc.)", "NIST cybersecurity framework"],
                "singapore": ["PDPA (Personal Data Protection Act)", "Cybersecurity Act requirements"],
                "united_kingdom": ["UK GDPR (retained EU law)", "Data Protection Act 2018"],
                "canada": ["PIPEDA (Personal Information Protection)", "PECA (cybersecurity obligations)"],
            },
            "Employment, contractor, and payroll law obligations": {
                "australia": ["Fair Work Act 2009", "National Employment Standards", "Award/agreement rates"],
                "vietnam": ["Vietnam Labor Code", "Minimum wage regulations", "Social insurance requirements"],
                "united_states": ["FLSA (Fair Labor Standards Act)", "State employment laws", "Worker classification rules"],
                "singapore": ["Employment Act", "Ministry of Manpower (MOM) regulations"],
                "united_kingdom": ["Employment Rights Act 1996", "National Living Wage requirements"],
                "canada": ["Canada Labour Code", "Provincial employment standards"],
            },
            "Record-keeping and audit evidence requirements": {
                "australia": ["Tax Records Act", "7-year retention requirements", "ATO audit evidence"],
                "vietnam": ["Vietnam Accounting Law", "Record retention (3-5 years)", "Tax audit requirements"],
                "united_states": ["IRS record retention (3-7 years)", "SOX compliance documentation"],
                "singapore": ["ACRA record retention (5 years)", "Audit trail requirements"],
                "united_kingdom": ["HMRC record retention (6 years)", "Accounting records regulations"],
                "canada": ["CRA record retention (6 years)", "GST input tax documentation"],
            },
        }

        origin = self._normalize_country(parsed.get("origin_country", ""))
        destination = self._normalize_country(parsed.get("destination_country", ""))

        # Build detailed compliance mapping table
        lines.append("### Compliance Mapping Table")
        lines.append("")
        lines.append(
            "| Checklist Item | Origin Country Law | Destination Country Law | Reference Evidence | Legal Date | Owner | Due Date | Status | Legal Review Required |"
        )
        lines.append("|---|---|---|---|---|---|---|---|---|")

        checklist_items = [
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

        for item in checklist_items:
            mapping = checklist_mapping.get(item, {})
            origin_laws = mapping.get(origin, ["General trade compliance"])
            destination_laws = mapping.get(destination, ["General trade compliance"])

            origin_text = "; ".join(origin_laws[:1]) if origin_laws else "TBD"
            destination_text = "; ".join(destination_laws[:1]) if destination_laws else "TBD"

            origin_reference, origin_date = self._extract_reference_and_date(
                origin_text,
                evidence_docs,
            )
            destination_reference, destination_date = self._extract_reference_and_date(
                destination_text,
                evidence_docs,
            )

            reference_evidence = (
                f"Origin: {origin_reference}; Destination: {destination_reference}"
            )
            legal_date = f"Origin: {origin_date}; Destination: {destination_date}"

            # Determine if legal review is required (high-risk items)
            legal_review = "YES" if any(r["risk"] == "high" for r in risk_items) else "NO"

            lines.append(
                f"| {item} | {origin_text} | {destination_text} | {reference_evidence} | {legal_date} | [Assign Owner] | [Set Date] | In Progress | {legal_review} |"
            )

        lines.extend(
            [
                "",
                "### Detailed Implementation Steps",
                "",
            ]
        )

        # Add detailed explanations for high-risk items
        high_risk_items = [r for r in risk_items if r["risk"] == "high"]
        if high_risk_items:
            lines.extend(
                [
                    "#### ⚠️ HIGH-RISK COMPLIANCE AREAS REQUIRING IMMEDIATE LEGAL REVIEW",
                    "",
                ]
            )
            for idx, item in enumerate(high_risk_items, 1):
                lines.extend(
                    [
                        f"**{idx}. {item['area']}**",
                        "",
                        f"- **Risk Level**: {item['risk'].upper()}",
                        f"- **Reason**: {item['reason']}",
                        f"- **Action**: Schedule immediate legal consultation for both {parsed['origin_country']} and {parsed['destination_country']}",
                        f"- **Responsible**: Chief Legal Officer / Compliance Manager",
                        f"- **Timeline**: Within 2 weeks of market entry planning",
                        "",
                    ]
                )

        lines.extend(
            [
                "#### Implementation Checklist",
                "",
                "For each compliance item, complete these steps:",
                "",
                "1. **Research**: Verify applicable laws in origin ({}) and destination ({}) countries".format(
                    parsed["origin_country"], parsed["destination_country"]
                ),
                "2. **Document**: Create a compliance brief for each obligation",
                "3. **Assign**: Designate owner with clear accountability",
                "4. **Schedule**: Set implementation deadline (suggest 30-90 days pre-launch)",
                "5. **Review**: Have licensed legal/compliance professional validate approach",
                "6. **Implement**: Execute procedures and maintain records",
                "7. **Monitor**: Continuous compliance monitoring and updates",
                "",
                "#### Key Contact Information (To Be Populated)",
                "",
                "| Role | Name | Email | Phone | Country |",
                "|---|---|---|---|---|",
                "| Compliance Lead | [Name] | [Email] | [Phone] | {} |".format(parsed["origin_country"]),
                "| Legal Counsel | [Name] | [Email] | [Phone] | {} |".format(parsed["destination_country"]),
                "| Tax Advisor | [Name] | [Email] | [Phone] | [Country] |",
                "| Regulatory Affairs | [Name] | [Email] | [Phone] | [Country] |",
                "",
                "#### Next Review Date",
                "",
                "- Initial Compliance Review: [Set 30 days from report date]",
                "- Quarterly Review: [Set quarterly meetings]",
                "- Legal Sign-off Required: YES (before market entry)",
                "",
            ]
        )

        return lines

    def _load_evidence_documents(self, evidence_files: list[str]) -> list[dict]:
        docs: list[dict] = []
        seen_paths = set()
        allowed_suffixes = {".md", ".txt", ".html", ".htm", ".json", ".csv", ".xml"}

        for raw_path in evidence_files:
            path = Path(raw_path)
            try:
                resolved = path.resolve()
            except Exception:
                continue

            if str(resolved) in seen_paths:
                continue
            seen_paths.add(str(resolved))

            if not resolved.exists() or not resolved.is_file():
                continue
            if resolved.suffix.lower() not in allowed_suffixes:
                continue

            try:
                text = resolved.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            if not text.strip():
                continue

            # Limit per-doc size to keep extraction efficient.
            docs.append({"path": str(resolved), "text": text[:200000]})

        return docs

    def _extract_reference_and_date(self, law_label: str, evidence_docs: list[dict]) -> tuple[str, str]:
        if not law_label or law_label == "TBD":
            return "TBD", "Not found"

        law_lower = law_label.lower()
        fallback_reference = f"{law_label} (no local evidence match)"

        for doc in evidence_docs:
            doc_text = doc["text"]
            lowered = doc_text.lower()
            index = lowered.find(law_lower)
            if index == -1:
                continue

            date_text = self._extract_date_near_index(doc_text, index)
            source_name = Path(doc["path"]).name
            return f"{law_label} in {source_name}", date_text

        law_keywords = [w for w in re.findall(r"[a-zA-Z]{4,}", law_lower) if w not in {"and", "with", "from", "for", "requirements", "general", "trade", "compliance"}]
        for doc in evidence_docs:
            lowered = doc["text"].lower()
            if not law_keywords:
                continue
            keyword_hits = sum(1 for kw in law_keywords[:4] if kw in lowered)
            if keyword_hits < 2:
                continue

            date_text = self._extract_date_near_keywords(doc["text"], law_keywords[:2])
            source_name = Path(doc["path"]).name
            return f"{law_label} (keyword match in {source_name})", date_text

        return fallback_reference, "Not found"

    def _extract_date_near_index(self, text: str, index: int) -> str:
        start = max(0, index - 350)
        end = min(len(text), index + 350)
        window = text[start:end]

        date_text = self._extract_date_from_text(window)
        if date_text:
            return date_text

        date_text = self._extract_date_from_text(text)
        return date_text or "Not found"

    def _extract_date_near_keywords(self, text: str, keywords: list[str]) -> str:
        lowered = text.lower()
        for kw in keywords:
            idx = lowered.find(kw)
            if idx == -1:
                continue
            date_text = self._extract_date_near_index(text, idx)
            if date_text != "Not found":
                return date_text
        return self._extract_date_from_text(text) or "Not found"

    def _extract_date_from_text(self, text: str) -> str | None:
        month_names = (
            "January|February|March|April|May|June|July|August|September|October|November|December"
        )
        patterns = [
            r"\b\d{4}-\d{2}-\d{2}\b",
            r"\b\d{1,2}/\d{1,2}/\d{4}\b",
            r"\b\d{1,2}-\d{1,2}-\d{4}\b",
            rf"\b(?:{month_names})\s+\d{{1,2}},\s+\d{{4}}\b",
            rf"\b\d{{1,2}}\s+(?:{month_names})\s+\d{{4}}\b",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(0)

        indicator_pattern = re.compile(
            rf"\b(?:effective|updated|last updated|published|issued)\b[^\n]{{0,40}}((?:{month_names})\s+\d{{1,2}},\s+\d{{4}}|\d{{4}}-\d{{2}}-\d{{2}}|\d{{1,2}}/\d{{1,2}}/\d{{4}})",
            flags=re.IGNORECASE,
        )
        indicator_match = indicator_pattern.search(text)
        if indicator_match:
            return indicator_match.group(1)

        return None

    def _risk_assessment(self, parsed: dict) -> list[dict]:
        summary = (parsed.get("business_summary") or "").lower()
        items: list[dict] = []

        keyword_rules = [
            (
                ["medical", "pharma", "drug", "therapeutic", "device"],
                "Product approvals and safety certification",
                "high",
                "Regulated health-related products usually require strict approvals in both countries.",
            ),
            (
                ["food", "beverage", "supplement", "agri"],
                "Food and labeling compliance",
                "high",
                "Food imports and consumer labeling often have strict legal requirements.",
            ),
            (
                ["finance", "fintech", "payment", "bank", "insurance", "crypto"],
                "Financial licensing and AML/KYC",
                "high",
                "Financial services often trigger licensing and anti-money-laundering obligations.",
            ),
            (
                ["hardware", "electronics", "robot", "sensor", "iot", "telecom"],
                "Import controls and technical standards",
                "high",
                "Physical goods and electronics require complex customs classification, technical compliance, and may face export controls.",
            ),
            (
                ["data", "ai", "software", "saas", "cloud", "platform"],
                "Data protection and cybersecurity",
                "medium",
                "Digital services may trigger privacy, cross-border data transfer, and cyber rules.",
            ),
        ]

        for keywords, area, risk, reason in keyword_rules:
            if any(k in summary for k in keywords):
                items.append({"area": area, "risk": risk, "reason": reason})

        if not items:
            items.append(
                {
                    "area": "General cross-border operations",
                    "risk": "medium",
                    "reason": "No high-risk keywords detected, but baseline trade and tax checks remain required.",
                }
            )

        return items

    def _export_pdf_report(self, markdown_text: str, pdf_path: Path) -> bool:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
            from xml.sax.saxutils import escape
        except Exception:
            return False

        lines = [line.rstrip() for line in markdown_text.splitlines()]
        styles = getSampleStyleSheet()
        story = []

        for line in lines:
            if not line.strip():
                story.append(Spacer(1, 8))
                continue
            safe = escape(line)
            if line.startswith("# "):
                story.append(Paragraph(safe[2:].strip(), styles["Heading1"]))
            elif line.startswith("## "):
                story.append(Paragraph(safe[3:].strip(), styles["Heading2"]))
            elif line.startswith("- "):
                story.append(Paragraph(f"• {safe[2:].strip()}", styles["BodyText"]))
            else:
                story.append(Paragraph(safe, styles["BodyText"]))

        try:
            doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
            doc.build(story)
            return True
        except Exception:
            return False

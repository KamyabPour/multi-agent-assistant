import json
import re
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
                title="Validate source captures",
                details=(
                    f"Downloaded {run_result['download_count']} source files to "
                    f"{run_result['downloads_dir']}"
                ),
                priority="medium",
            ),
        ]

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
            if not md_files:
                raise ValueError("No markdown files found in shared folder.")
            md_path = md_files[0]

        raw_text = md_path.read_text(encoding="utf-8", errors="ignore")
        parsed = self._parse_business_markdown(raw_text)

        downloads_dir = shared_folder / "compliance_downloads"
        downloads_dir.mkdir(exist_ok=True)

        source_urls = list(parsed["urls"])
        context_urls = context.get("source_urls") or []
        source_urls.extend([u for u in context_urls if isinstance(u, str)])
        source_urls.extend(self._default_global_sources())
        source_urls = self._dedupe_urls(source_urls)

        downloaded_sources = []
        for idx, url in enumerate(source_urls, start=1):
            downloaded_file = self._download_source(url, downloads_dir, idx)
            if downloaded_file:
                downloaded_sources.append(str(downloaded_file))

        now = datetime.now(timezone.utc)
        report_name = f"compliance_report_{now.strftime('%Y%m%d_%H%M%S')}.md"
        report_path = shared_folder / report_name
        report_text = self._build_report(
            parsed=parsed,
            downloaded_sources=downloaded_sources,
            source_urls=source_urls,
            report_generated_at=now.isoformat(),
            business_file=str(md_path),
        )
        report_path.write_text(report_text, encoding="utf-8")

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
        }

    def _parse_business_markdown(self, text: str) -> dict:
        origin = self._find_value(text, [r"origin country", r"business country", r"from country"])
        destination = self._find_value(
            text, [r"destination country", r"to country", r"target country"]
        )
        business = self._find_value(
            text, [r"business", r"business type", r"industry", r"product", r"service"]
        )

        urls = re.findall(r"https?://[^\s)\]]+", text)
        return {
            "origin_country": origin or "Unknown",
            "destination_country": destination or "Unknown",
            "business_summary": business or "Business description not found in markdown.",
            "urls": urls,
        }

    def _find_value(self, text: str, labels: list[str]) -> str | None:
        for label in labels:
            # Accept formats like "Label: value" and "- Label: value"
            match = re.search(
                rf"(?im)^\s*(?:[-*]\s*)?(?:{label})\s*:\s*(.+?)\s*$",
                text,
            )
            if match:
                return match.group(1).strip()
        return None

    def _default_global_sources(self) -> list[str]:
        return [
            "https://www.wto.org/english/tratop_e/tratop_e.htm",
            "https://www.trade.gov/country-commercial-guides",
            "https://www.sanctionsmap.eu/#/main",
            "https://www.worldbank.org/en/topic/trade",
        ]

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
        source_urls: list[str],
        report_generated_at: str,
        business_file: str,
    ) -> str:
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
                "## Next Actions",
                "- Map each checklist line to country-specific law references.",
                "- Assign owners and due dates for each compliance obligation.",
                "- Open legal review for unresolved high-risk items.",
            ]
        )

        return "\n".join(lines) + "\n"

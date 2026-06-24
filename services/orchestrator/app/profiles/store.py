import json
from pathlib import Path

from app.profiles.models import AssistantProfile, BossProfile


class ProfileStore:
    """Simple JSON-backed profile storage for local development."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.assistant_file = self.data_dir / "assistant_profile.json"
        self.boss_file = self.data_dir / "boss_profile.json"

    def load_assistant(self) -> AssistantProfile:
        """Load assistant profile or return defaults."""
        if self.assistant_file.exists():
            data = json.loads(self.assistant_file.read_text())
            return AssistantProfile(**data)
        return AssistantProfile()

    def save_assistant(self, profile: AssistantProfile) -> None:
        """Save assistant profile."""
        self.assistant_file.write_text(profile.model_dump_json(indent=2))

    def load_boss(self, boss_id: str) -> BossProfile | None:
        """Load boss profile or return None."""
        if self.boss_file.exists():
            data = json.loads(self.boss_file.read_text())
            if data.get("boss_id") == boss_id:
                return BossProfile(**data)
        return None

    def save_boss(self, profile: BossProfile) -> None:
        """Save boss profile."""
        self.boss_file.write_text(profile.model_dump_json(indent=2))

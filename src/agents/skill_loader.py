"""
C1 — Skill Loader
Dynamically loads all markdown skill files for a specialist domain
and the project-specific playbook at runtime.

Non-negotiable rules:
- Never contains a hardcoded list of filenames
- Scans skills/{domain}/ using pathlib.Path.glob("*.md")
- Loads playbooks/{project_id}.md if it exists
- Sorts files alphabetically for deterministic order
- Returns empty string on missing domain folder (does not raise)
"""

from __future__ import annotations

from pathlib import Path

from src.logging_config import get_logger

logger = get_logger(__name__)

# Repo root: skill_loader.py is at src/agents/skill_loader.py
# parents[0] = src/agents/, parents[1] = src/, parents[2] = repo root
REPO_ROOT: Path = Path(__file__).resolve().parents[2]
SKILLS_DIR: Path = REPO_ROOT / "skills"
PLAYBOOKS_DIR: Path = REPO_ROOT / "playbooks"


class SkillLoader:
    """Loads domain skill files and project playbooks into a system prompt."""

    def load(self, domain: str, project_id: str) -> str:
        """
        Load all skill files for a domain and the project playbook.

        Args:
            domain: The specialist domain name (e.g., "claims", "legal").
            project_id: The project UUID string for playbook lookup.

        Returns:
            Concatenated markdown content with section headers.
            Empty string if no skill files or playbook found.
        """
        sections: list[str] = []

        # --- Layer 1: Domain skill files ---
        domain_dir = SKILLS_DIR / domain

        if not domain_dir.is_dir():
            logger.warning(
                "skill_loader_domain_missing",
                domain=domain,
                expected_path=str(domain_dir),
            )
        else:
            skill_files = sorted(domain_dir.glob("*.md"))

            if not skill_files:
                logger.warning(
                    "skill_loader_no_files",
                    domain=domain,
                    directory=str(domain_dir),
                )
            else:
                logger.info(
                    "skill_loader_domain_loaded",
                    domain=domain,
                    file_count=len(skill_files),
                    filenames=[f.name for f in skill_files],
                )

                for skill_file in skill_files:
                    try:
                        content = skill_file.read_text(encoding="utf-8")
                        sections.append(
                            f"--- SKILL: {skill_file.name} ---\n\n{content}"
                        )
                    except OSError as exc:
                        logger.error(
                            "skill_loader_file_read_error",
                            domain=domain,
                            filename=skill_file.name,
                            error=str(exc),
                        )

        # --- Layer 2: Project playbook ---
        playbook_path = PLAYBOOKS_DIR / f"{project_id}.md"

        if playbook_path.is_file():
            try:
                content = playbook_path.read_text(encoding="utf-8")
                sections.append(
                    f"--- PROJECT PLAYBOOK: {project_id} ---\n\n{content}"
                )
                logger.info(
                    "skill_loader_playbook_loaded",
                    project_id=project_id,
                )
            except OSError as exc:
                logger.error(
                    "skill_loader_playbook_read_error",
                    project_id=project_id,
                    error=str(exc),
                )
        else:
            logger.warning(
                "skill_loader_playbook_missing",
                project_id=project_id,
                expected_path=str(playbook_path),
            )

        return "\n\n".join(sections)

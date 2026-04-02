"""
C1 — Skill Loader
Dynamically loads all markdown skill files for a specialist domain
and the project-specific playbook at runtime.

Non-negotiable rules:
- Never contains a hardcoded list of filenames
- Scans skills/orchestrators/{domain}/ for Tier 1 orchestrators, skills/smes/{domain}/ for Tier 2 SMEs
- Falls back to skills/{domain}/ for legacy paths
- Resolution order: orchestrators/ → smes/ → legacy
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
        # Resolution order: orchestrators/{domain} → smes/{domain} → {domain} (legacy)
        orchestrator_path = SKILLS_DIR / "orchestrators" / domain
        sme_path = SKILLS_DIR / "smes" / domain
        legacy_path = SKILLS_DIR / domain

        if orchestrator_path.is_dir():
            domain_dir = orchestrator_path
        elif sme_path.is_dir():
            domain_dir = sme_path
        else:
            domain_dir = legacy_path

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

        # --- Layer 2: Project playbook (flat file override or DB auto-generation) ---
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
            # No flat file — auto-generate project context from Supabase
            sections.append(self._generate_project_context(project_id))

        return "\n\n".join(sections)

    def _generate_project_context(self, project_id: str) -> str:
        """
        Auto-generate project context from Supabase when no flat playbook exists.

        Queries contracts and parties tables for the project. Returns a markdown
        block with contracts, parties, and FIDIC edition. Gracefully degrades
        on any database error — returns partial content built so far.
        """
        from src.clients import get_supabase_client

        header = "--- PROJECT CONTEXT (auto-generated from database) ---"

        try:
            supabase = get_supabase_client()

            contracts_resp = (
                supabase.table("contracts")
                .select("id, name, contract_type, fidic_edition")
                .eq("project_id", project_id)
                .execute()
            )
            contracts = contracts_resp.data or []

            parties_resp = (
                supabase.table("parties")
                .select("id, name, role")
                .eq("project_id", project_id)
                .execute()
            )
            parties = parties_resp.data or []

        except Exception as exc:
            logger.warning(
                "skill_loader_playbook_db_error",
                project_id=project_id,
                error=str(exc),
            )
            return header + "\n\nFailed to load project context from database."

        # Both empty — no project data registered yet
        if not contracts and not parties:
            logger.info(
                "skill_loader_playbook_db_empty",
                project_id=project_id,
            )
            return (
                header
                + "\n\nNo contracts or parties have been registered for this project yet."
            )

        parts: list[str] = [header]

        # Contracts section
        if contracts:
            parts.append("\n## Contracts on Record")
            for c in contracts:
                edition = c.get("fidic_edition")
                edition_str = f"FIDIC {edition}" if edition else "FIDIC edition not specified"
                contract_type = c.get("contract_type", "type not specified")
                parts.append(f"- {c.get('name', 'Unnamed')} — {contract_type} — {edition_str}")

        # Parties section
        if parties:
            parts.append("\n## Parties on Record")
            for p in parties:
                parts.append(f"- {p.get('name', 'Unnamed')} — {p.get('role', 'role not specified')}")

        # FIDIC edition summary
        fidic_editions = [
            c["fidic_edition"] for c in contracts if c.get("fidic_edition")
        ]
        parts.append("\n## FIDIC Edition")
        if fidic_editions:
            unique_editions = sorted(set(fidic_editions))
            parts.append(f"Governing edition: {', '.join(unique_editions)}")
        else:
            parts.append(
                "FIDIC edition not confirmed — determine from contract documents in the warehouse"
            )

        logger.info(
            "skill_loader_playbook_db_generated",
            project_id=project_id,
            contract_count=len(contracts),
            party_count=len(parties),
        )

        return "\n".join(parts)

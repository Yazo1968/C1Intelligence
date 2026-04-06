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
            from src.clients import get_supabase_client
            supabase = get_supabase_client()
            sections.append(self._generate_project_context(supabase, project_id))

        return "\n\n".join(sections)

    def load_grounding_schema(self, domain: str) -> dict | None:
        """
        Load the grounding_schema.json file for a domain if it exists.

        Looks in the same directory as the domain's skill markdown files,
        using the same resolution order as load():
          orchestrators/{domain} → smes/{domain} → {domain} (legacy)

        Returns the parsed JSON dict if found, None if not present.
        Absence of a grounding schema is not an error — it means no
        automatic confidence capping is applied for that domain.
        """
        import json as _json

        orchestrator_path = SKILLS_DIR / "orchestrators" / domain
        sme_path = SKILLS_DIR / "smes" / domain
        legacy_path = SKILLS_DIR / domain

        if orchestrator_path.is_dir():
            domain_dir = orchestrator_path
        elif sme_path.is_dir():
            domain_dir = sme_path
        else:
            domain_dir = legacy_path

        schema_path = domain_dir / "grounding_schema.json"

        if not schema_path.is_file():
            logger.debug(
                "grounding_schema_not_found",
                domain=domain,
                expected_path=str(schema_path),
            )
            return None

        try:
            content = schema_path.read_text(encoding="utf-8")
            schema = _json.loads(content)
            logger.info(
                "grounding_schema_loaded",
                domain=domain,
                path=str(schema_path),
            )
            return schema
        except (OSError, _json.JSONDecodeError) as exc:
            logger.error(
                "grounding_schema_load_error",
                domain=domain,
                path=str(schema_path),
                error=str(exc),
            )
            return None

    def _generate_project_context(
        self, supabase, project_id: str
    ) -> str:
        """
        Generate a project context block for the agent system prompt.

        Reads party_identities and party_roles from the governance authority
        log. Returns a markdown block summarising identified parties and their
        roles. Gracefully degrades if governance has not been run yet.
        """
        try:
            identities_result = (
                supabase.table("party_identities")
                .select("id, legal_name, party_category, entity_type, is_internal")
                .eq("project_id", project_id)
                .execute()
            )
            identities = identities_result.data or []
        except Exception as exc:
            logger.warning(
                "skill_loader_party_identities_failed",
                project_id=project_id,
                error=str(exc),
            )
            identities = []

        try:
            roles_result = (
                supabase.table("party_roles")
                .select("party_identity_id, role_title, appointment_status, governing_instrument")
                .eq("project_id", project_id)
                .execute()
            )
            roles = roles_result.data or []
        except Exception as exc:
            logger.warning(
                "skill_loader_party_roles_failed",
                project_id=project_id,
                error=str(exc),
            )
            roles = []

        if not identities:
            return (
                "\n\n## Project Context\n\n"
                "Governance has not been established for this project. "
                "Party identities and authority records are not yet available. "
                "Run governance establishment before submitting compliance-dependent queries.\n"
            )

        # Group roles by identity
        roles_by_identity: dict[str, list[dict]] = {i["id"]: [] for i in identities}
        for role in roles:
            iid = role["party_identity_id"]
            if iid in roles_by_identity:
                roles_by_identity[iid].append(role)

        lines: list[str] = ["\n\n## Project Context\n"]
        lines.append(f"**Parties identified:** {len(identities)}\n")

        # Internal parties first
        internal = [i for i in identities if i.get("is_internal")]
        external = [i for i in identities if not i.get("is_internal")]

        if internal:
            lines.append("### Internal (Employer's Organisation)")
            for identity in internal:
                party_roles = roles_by_identity.get(identity["id"], [])
                role_summary = ", ".join(
                    r["role_title"] for r in party_roles
                ) or "no roles recorded"
                lines.append(
                    f"- **{identity['legal_name']}** ({identity['entity_type']}) "
                    f"— {role_summary}"
                )
            lines.append("")

        if external:
            lines.append("### External Parties")
            for identity in external:
                party_roles = roles_by_identity.get(identity["id"], [])
                role_summary = ", ".join(
                    f"{r['role_title']} [{r['appointment_status']}]"
                    for r in party_roles
                ) or "no roles recorded"
                lines.append(
                    f"- **{identity['legal_name']}** ({identity['entity_type']}, "
                    f"{identity['party_category']}) — {role_summary}"
                )
            lines.append("")

        lines.append(
            "_Use get_party_authority tool to determine a party's specific "
            "authority scope and financial thresholds at a given date._\n"
        )

        return "\n".join(lines)

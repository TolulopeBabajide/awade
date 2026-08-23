#!/usr/bin/env python3
"""
check-template-integrity.py — validate a repo against schemas/template-manifest.json.

Catches the drift the template's own setup-review documented in derived projects:
  - empty / stub SKILL.md files (the Awade failure mode)
  - missing infrastructure scripts, rules, or docs
  - skill dirs that don't match the permission manifest (and vice versa)
  - the `ready-for-dev` vs `ready` lifecycle-stage mismatch that silently broke
    dev pickup
  - SKILL.md frontmatter whose `name` doesn't match its directory
  - skills missing the inlined Prompt Defense Baseline

Usage:
  python3 scripts/check-template-integrity.py [REPO_ROOT] [--manifest PATH] [--warn-only]

  REPO_ROOT    repo to validate (default: the script's own repo root).
               Point it at a derived project to check a fork:
               python3 scripts/check-template-integrity.py ../awade

Exit:
  0 = no errors (warnings allowed)
  1 = at least one error (or --warn-only downgraded everything but still found issues)
"""
import sys, os, json, re, glob

PROMPT_DEFENSE_MARKER = "ECC-PROMPT-DEFENSE:BEGIN"


def load_manifest(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def read(path):
    try:
        return open(path, encoding="utf-8").read()
    except (FileNotFoundError, UnicodeDecodeError, IsADirectoryError):
        return None


def frontmatter(text):
    """Return dict of top-level YAML frontmatter keys (string values only)."""
    if not text or not text.startswith("---"):
        return {}
    m = re.search(r"\n---[ \t]*\n", text)
    if not m:
        return {}
    fm = {}
    for line in text[3:m.start()].splitlines():
        mk = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if mk:
            fm[mk.group(1)] = mk.group(2).strip().strip('"').strip("'")
    return fm


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    warn_only = "--warn-only" in flags

    here = os.path.dirname(os.path.abspath(__file__))
    default_root = os.path.dirname(here)
    root = os.path.abspath(args[0]) if args else default_root

    manifest_path = default_root + "/schemas/template-manifest.json"
    if "--manifest" in flags:
        i = argv.index("--manifest")
        manifest_path = argv[i + 1]
    mani = load_manifest(manifest_path)

    errors, warnings = [], []
    E = warnings.append if warn_only else errors.append

    def p(rel):
        return os.path.join(root, rel)

    # 1. required root files
    for rel in mani["required_root_files"]:
        if not os.path.isfile(p(rel)):
            E(f"missing required root file: {rel}")

    # 2. required rules
    for rel in mani["required_rules"]:
        if not os.path.isfile(p(rel)):
            E(f"missing required rule: {rel}")

    # 3. required scripts
    for rel in mani["required_scripts"]:
        if not os.path.isfile(p(rel)):
            E(f"missing required script: {rel}")

    # 4. required docs
    for rel in mani["required_docs"]:
        if not os.path.isfile(p(rel)):
            E(f"missing required doc: {rel}")

    # 5. required skills — existence, non-stub, frontmatter, prompt-defense.
    # Both runtime trees are required so a valid Claude setup cannot mask a
    # missing or incomplete Codex setup.
    sr = mani["skill_rules"]
    runtime_skill_dirs = [".claude/skills", ".agents/skills"]
    for runtime_dir in runtime_skill_dirs:
        for name in mani["required_skills"]:
            skill_md = os.path.join(p(runtime_dir), name, "SKILL.md")
            label = f"{runtime_dir}/{name}/SKILL.md"
            if not os.path.isfile(skill_md):
                E(f"missing required skill: {label}")
                continue
            text = read(skill_md) or ""
            if len(text.encode("utf-8")) < sr["min_skill_md_bytes"]:
                E(f"stub skill (too small, <{sr['min_skill_md_bytes']}B): {label}")
            fm = frontmatter(text)
            for key in sr["frontmatter_must_have"]:
                if key not in fm or not fm[key]:
                    E(f"{label} frontmatter missing '{key}'")
            if sr.get("name_must_match_dir") and fm.get("name") and fm["name"] != name:
                E(f"{label} frontmatter name '{fm['name']}' != directory '{name}'")
            if sr.get("must_carry_prompt_defense") and PROMPT_DEFENSE_MARKER not in text:
                warnings.append(f"{label} is missing the Prompt Defense Baseline")

    # 6. skills <-> permission manifest bijection
    perm_path = p("agent-permissions.json")
    perm_text = read(perm_path)
    perm = None
    if perm_text is None:
        E("agent-permissions.json not found")
    else:
        try:
            perm = json.loads(perm_text)
        except json.JSONDecodeError as e:
            E(f"agent-permissions.json is not valid JSON: {e}")
    if perm is not None:
        perm_agents = {k for k in perm if not k.startswith("_")}
        for runtime_dir in runtime_skill_dirs:
            skill_dirs = {os.path.basename(os.path.dirname(p_))
                          for p_ in glob.glob(os.path.join(p(runtime_dir), "*", "SKILL.md"))}
            for name in sorted(skill_dirs - perm_agents):
                E(f"{runtime_dir} skill '{name}' has no entry in agent-permissions.json")
            for name in sorted(perm_agents - skill_dirs):
                E(f"agent-permissions.json lists '{name}' but no {runtime_dir} skill exists")

    # 7. no deprecated lifecycle-stage tokens anywhere under .claude/ or docs/
    deprecated = mani.get("deprecated_stage_tokens", [])
    if deprecated:
        scan_globs = [p(".claude/**/*.md"), p(".agents/**/*.md"), p("docs/**/*.md"),
                      p("CLAUDE.md"), p("AGENTS.md"), p("project-config.md")]
        seen = set()
        for g in scan_globs:
            for f in glob.glob(g, recursive=True):
                t = read(f)
                if not t:
                    continue
                for tok in deprecated:
                    if tok in t and (f, tok) not in seen:
                        seen.add((f, tok))
                        rel = os.path.relpath(f, root)
                        E(f"deprecated stage token '{tok}' found in {rel} "
                          f"(canonical is 'ready' — this is the silent dev-pickup break)")

    # --- report ---
    label = os.path.relpath(root, os.getcwd()) if root != os.getcwd() else "."
    print(f"Template integrity check: {label}")
    print(f"  required: {len(mani['required_skills'])} skills per runtime, "
          f"{len(mani['required_scripts'])} scripts, "
          f"{len(mani['required_rules'])} rules, "
          f"{len(mani['required_docs'])} docs")

    for w in warnings:
        print(f"  ⚠ WARN  {w}")
    for e in errors:
        print(f"  ✗ ERROR {e}")

    if errors:
        print(f"\n✗ {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"\n✓ structure valid ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

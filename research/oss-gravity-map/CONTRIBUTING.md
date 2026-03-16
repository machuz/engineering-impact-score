# Contributing to OSS Gravity Map

The fairness of this analysis depends on accurate **architecture patterns** and **author aliases** for each repository. If you know a project well, your contributions make the results more trustworthy.

## What You Can Improve

### 1. Architecture Patterns (`configs/<repo>.yaml`)

Architecture patterns define which files EIS treats as structurally significant. These directly affect the **Design score**, which feeds into **gravity**.

```yaml
# Example: if you know React's reconciler is architecturally critical
architecture_patterns:
  - "packages/react-reconciler/src/*.js"
  - "packages/react-reconciler/src/forks/*.js"  # <-- missing, should add
```

**How to decide:**
- Would changing this file affect the system's fundamental behavior?
- Is this file an interface, abstraction boundary, or core module?
- Would a new contributor need to understand this file to make meaningful changes?

If yes → it's an architecture file.

### 2. Author Aliases (`configs/<repo>.yaml`)

Git authors vary (name changes, email changes, handle vs real name). Aliases merge them into one identity.

```yaml
aliases:
  "Tj Holowaychuk": "TJ Holowaychuk"
  "visionmedia": "TJ Holowaychuk"
```

**How to find aliases:**
```bash
cd <repo>
git log --format='%aN' | sort | uniq -c | sort -rn | head -50
```
Look for variations of the same person.

### 3. Known Architects (`dataset.yaml`)

If you know who the key architects are for a Tier 2 project, add them to `dataset.yaml`.

### 4. Bot Exclusions

If a project uses bots that commit code (merge bots, auto-formatters), add them to `exclude_authors`.

## How to Submit

1. Fork the repo
2. Edit the relevant `configs/<repo>.yaml`
3. Open a PR with a brief explanation of why the change improves accuracy
4. Include evidence where possible (links to commits, blog posts, or `git log` output)

## Principles

- **Transparency**: All configs are public and version-controlled
- **Reproducibility**: Anyone can re-run the analysis with the same configs
- **Fairness**: No hidden tuning — architecture patterns must be justifiable
- **Community-driven**: The people who know a project best should define its structure

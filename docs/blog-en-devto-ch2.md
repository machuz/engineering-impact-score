---
title: "Beyond Individual Scores: Measuring Team Health from Git History"
published: true
description: "Chapter 2 of Engineering Impact Score. Team-level analysis — complementarity, risk ratio, productivity density — all from git data you already have."
tags: opensource, productivity, git, teams
cover_image: https://raw.githubusercontent.com/machuz/engineering-impact-score/main/docs/images/engineering-impact-framework-diagram-fixed.png
---

*Individual scores tell you who is strong. Team health tells you whether the team will still be strong next quarter.*

## Previously

In [Chapter 1](https://dev.to/machuz/measuring-engineering-impact-from-git-history-alone-f6c), I introduced a 7-axis scoring model for individual engineers, powered entirely by git history. The 3-axis topology (Role / Style / State) gave us a vocabulary for describing engineers: an *Architect* who writes durable design code, a *Cleaner* who quietly pays down debt, a *Producer* who ships volume.

But individual scores have a blind spot.

**Teams.**

## Why Individual Scores Aren't Enough

A team where every member scores 80+ isn't necessarily strong. If everyone is a Producer, nobody is shaping architecture. Nobody is paying down debt. The codebase ships fast and rots faster.

Conversely, a team averaging 50 points — but with one Architect, one Cleaner, and two Growing juniors — may be in a much healthier position. In six months, those juniors will level up, and the foundation is solid.

**A strong team is not the sum of individual scores. It's about composition and complementarity.**

## `eis team` — Team-Level Analysis

The new `eis team` command aggregates individual scores into team-level metrics.

```bash
# Simplest: domain = team (no config needed)
eis team --recursive ~/workspace

# With explicit team definitions
eis team --config eis.yaml --recursive ~/workspace

# JSON output (paste into AI for deeper analysis)
eis team --format json --recursive ~/workspace
```

If no `teams` section exists in config, each domain (Backend / Frontend / Infra) is treated as a single team. Zero config required.

```yaml
# eis.yaml (optional)
teams:
  backend-core:
    domain: Backend
    members: [alice, bob, charlie]
  frontend-app:
    domain: Frontend
    members: [dave, eve]
```

## Seven Team Health Axes

### 1. Complementarity — Role Diversity

How many of the 5 known roles are present? Architect gets the biggest bonus because design leadership is the most critical gap.

```
coverage = uniqueRoles / 5
bonus = Architect(+10) + Anchor(+5) + Cleaner(+5)
score = coverage × 80 + bonus  (clamped 0-100)
```

A team with only Producers and no Architect scores 16. A fully diverse team hits 100.

### 2. Growth Potential — Can Juniors Level Up Here?

Growing members + mentoring capacity.

```
score = growingRatio × 60 + Builder(+20) + Cleaner(+20)
```

Having Growing juniors is necessary but not sufficient. Without a Builder or Cleaner as a role model, growth stalls. Both must be present for the score to climb.

### 3. Sustainability — Inverse of Risk

What percentage of the team is in a risk state (Former, Silent, Fragile)?

```
riskRatio = (Former + Silent + Fragile) / memberCount
score = (1 - riskRatio) × 80 + Architect(+20)
```

Former members whose code still dominates blame. Silent members who haven't meaningfully contributed in months. Fragile members whose code survives only because nobody touches it. These are the hidden drags on team velocity.

### 4. Debt Balance — Self-Cleaning Tendency

Average Debt Cleanup score across members. 50 is neutral; above 50 means the team cleans more debt than it creates.

### 5. Productivity Density — Output Per Head

Average production score with a small-team bonus. Three people running a large-scale API server will show an abnormally high density — impressive, but also risky.

```
base = avg(members.Production)
bonus: ≤3 members && base ≥ 50 → ×1.2
        ≤5 members && base ≥ 50 → ×1.1
```

This quantifies the "this amount of code from this few people is insane" feeling.

### 6. Quality Consistency — Mean + Low Variance

A team averaging 80 quality with tight variance is healthy. A team averaging 80 but ranging from 95 to 40 is not — the low end drags reviews, and quality gates become performative.

```
score = avgQuality × 0.6 + (100 - stdev × 2) × 0.4
```

### 7. Risk Ratio — Blunt Truth

Percentage of members in Former, Silent, or Fragile state. Above 25% is a warning. Above 50% is a crisis.

## Patterns of Strong Teams

After running this on multiple teams, patterns emerge:

**Strong teams share:**
- Architect + Builder present (someone designs, someone implements design)
- 3+ role types (minimum: Architect / Anchor / Producer)
- 20%+ Growing ratio (juniors are developing)
- Risk Ratio near 0%
- Quality Consistency above 70

**Dangerous compositions:**
- Mass/Churn-heavy: high volume, low durability
- No Architect: nobody shapes the design layer → implicit decisions accumulate
- Silent accumulation: headcount says 8, effective contributors are 4
- Producer monoculture: everyone builds, nobody cleans

## A Sociological Observation

**Teams with a Builder or Cleaner grow people faster.** When a role model exists — someone whose code demonstrably survives and whose reviews teach — Growing members transition to Active at roughly double the rate.

**Teams without an Architect degrade over time.** Low Complementarity correlates with declining Quality Consistency over 6-month windows. Without a design compass, everyone codes in their own direction.

**Small-team anomalies are two-sided.** High Productivity Density is both a strength and a risk. If one person leaves a 3-person team scoring 80+ density, the impact is catastrophic.

## How to Use It

```bash
# Install
brew tap machuz/tap && brew install eis

# Team analysis
eis team --recursive ~/workspace

# JSON → paste into Claude / ChatGPT
eis team --format json --recursive ~/workspace | pbcopy
```

Deep insights are intentionally out of scope. The tool produces quantitative data; humans (or AI) interpret it. This separation is by design.

## Summary — Individual × Team

Chapter 1 answers "What kind of engineer is this person?"
Chapter 2 answers "What state is this team in?"

Together, they enable:
- **Hiring**: see which Role is missing → define the position
- **Team formation**: maximize complementarity
- **1-on-1s**: discuss growth direction based on score trajectories
- **Risk management**: catch Risk Ratio deterioration early

All from git history. No surveys. No additional tooling.

**What you can measure, you can improve. What you can't measure, you can only pray about.**

Let's turn team strength from a prayer into a metric.

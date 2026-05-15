# ⚖️ Tribunal — Project Bible

> *Five minds. One verdict. Zero bullshit.*

---

## Vision

**Tribunal** is a Claude Code plugin that assembles a dynamic panel of 5 specialized AI personas to deliberate on any question, argument, or decision — and converge on the best possible answer through structured debate, cross-examination, and a confidence-weighted verdict.

Unlike existing debate plugins that hardcode tech-focused personas or rely on fixed roles, Tribunal is **fully domain-agnostic**: it reads the topic first, dynamically assigns the most relevant expert roles, and runs a real deliberation pipeline from opening statements to final verdict.

---

## Core Philosophy

- **Truth over consensus** — the goal is not agreement, it's the *best* answer
- **Cognitive diversity** — every session needs a domain expert, a skeptic, a systems thinker, a mediator, and a devil's advocate
- **Transparency** — every verdict comes with a reasoning trail, not just a conclusion
- **Portability** — outputs are structured and exportable (JSON, Markdown ADR)

---

## How It Works

### Phase 1 — Topic Analysis
Claude reads the input and identifies:
- The domain (technical, ethical, strategic, creative, etc.)
- The key dimensions of the argument
- The 5 most relevant cognitive roles for *this specific topic*

### Phase 2 — Role Assignment (Dynamic Casting)
Each session spawns 5 personas tailored to the topic. Default archetypes:

| Role | Responsibility |
|---|---|
| **Domain Expert** | Deep subject-matter knowledge; separates facts from assumptions |
| **Devil's Advocate** | Challenges every conclusion, including the obvious ones |
| **Systems Thinker** | Zooms out; connects to broader context and second-order effects |
| **Logician** | Catches fallacies, invalid inferences, and rhetorical tricks |
| **Mediator** | Keeps the process honest; ensures all voices are heard |

> Custom personas can be injected via `--persona` flag (see Usage).

### Phase 3 — Opening Statements
Each persona presents their initial position on the topic independently — no cross-talk yet.

### Phase 4 — Cross-Examination
Each persona may directly challenge **one** other persona's argument. This is the core differentiator: it forces positions to be defended, not just stated.

### Phase 5 — Deliberation
Personas respond to challenges and refine their positions. Contradictions are surfaced and resolved.

### Phase 6 — Verdict
Each persona casts a vote with:
- A **position** (support / reject / conditional)
- A **confidence score** (0–100%)
- A **one-line rationale**

The final verdict is computed as a confidence-weighted consensus, with a dissenting opinion preserved if significant disagreement exists.

---

## Output Format

Every Tribunal session produces a structured output:

```markdown
## ⚖️ Tribunal Verdict

**Topic:** [original question]
**Domain:** [detected domain]
**Session ID:** [uuid]

### Panel
- 🔬 Domain Expert — [dynamically assigned name/role]
- 🗡️ Devil's Advocate — [dynamically assigned name/role]
- 🌐 Systems Thinker — [dynamically assigned name/role]
- 🧮 Logician — [dynamically assigned name/role]
- ⚖️ Mediator — [dynamically assigned name/role]

### Arguments Summary
[condensed per-persona position]

### Cross-Examination Highlights
[key challenges and responses]

### Final Verdict
**Decision:** [Best Answer]
**Confidence:** [weighted score]%
**Dissent:** [minority opinion if confidence < 80%]

### Reasoning Trail
[structured audit of how the verdict was reached]
```

---

## Usage

### Basic
```
/tribunal Should I use PostgreSQL or MongoDB for this project?
```

### With custom persona
```
/tribunal --persona "Pokemon card market expert" Is this card underpriced at €45?
```

### With domain hint
```
/tribunal --domain ethical Is it justified to ship a product with known minor bugs?
```

### Export as ADR
```
/tribunal --export adr Should we migrate our backend to Edge Functions?
```

### Set confidence threshold
```
/tribunal --min-confidence 85 What's the best clustering algorithm for this dataset?
```

---

## Differentiators vs. Competition

| Feature | Tribunal | billy-milligan | multi-viewpoint-debates | agent-tower |
|---|:---:|:---:|:---:|:---:|
| Dynamic role casting | ✅ | ❌ | ❌ | ❌ |
| Domain-agnostic | ✅ | ❌ (tech only) | ❌ | ✅ |
| Cross-examination phase | ✅ | ❌ | ❌ | ❌ |
| Confidence-weighted verdict | ✅ | ❌ | ❌ | ❌ |
| Custom persona injection | ✅ | ❌ | ❌ | ❌ |
| Exportable ADR / JSON | ✅ | ❌ | ❌ | ❌ |
| Dissenting opinion preserved | ✅ | ❌ | ❌ | ❌ |

---

## Technical Architecture

### Stack
- **Runtime:** Claude Code Plugin (MCP-compatible)
- **Orchestration:** Multi-agent sub-agent spawning via Claude Code SDK
- **Export:** Markdown ADR, JSON structured output

### Plugin Entry Points
```
/tribunal              — main command
/tribunal --help       — usage guide
/tribunal --export     — output format selector (md | json | adr)
/tribunal --persona    — inject custom expert role
/tribunal --domain     — override domain detection
/tribunal --min-confidence — set minimum verdict confidence threshold
```

### Agent Lifecycle
```
Input
  └─> Topic Analyzer
        └─> Role Caster (5 agents spawned)
              └─> Opening Statements (parallel)
                    └─> Cross-Examination (sequential)
                          └─> Deliberation (parallel)
                                └─> Verdict Aggregator
                                      └─> Output Formatter
```

---

## Roadmap

### v0.1 — MVP
- [ ] Static 5-persona panel (fixed archetypes)
- [ ] Opening statements + simple majority verdict
- [ ] Basic Markdown output

### v0.2 — Dynamic Casting
- [ ] Topic analysis → dynamic role assignment
- [ ] Domain detection (technical, ethical, strategic, creative)
- [ ] Custom `--persona` flag

### v0.3 — Full Tribunal Protocol
- [ ] Cross-examination phase
- [ ] Confidence-weighted verdict
- [ ] Dissenting opinion
- [ ] JSON + ADR export
- [ ] `--min-confidence` threshold flag

### v1.0 — Public Release
- [ ] Claude Code Plugin Hub listing
- [ ] Documentation site
- [ ] Community persona library

---

## Name & Identity

**Name:** Tribunal  
**Command:** `/tribunal`  
**Tagline:** *Five minds. One verdict. Zero bullshit.*  
**Domain:** Free — not taken as a Claude plugin as of May 2026  
**Tone:** Authoritative, precise, no fluff — mirrors the seriousness of a real deliberative body

---

## Non-Goals

- Tribunal is **not** a chatbot or assistant — it does not hold conversations
- Tribunal is **not** a legal tool — it does not provide legal advice
- Tribunal does **not** replace human judgment — it structures and accelerates it
- Tribunal does **not** always seek consensus — a split verdict with preserved dissent is a valid and valuable output

---

*Last updated: May 2026 — v0.1 pre-release*

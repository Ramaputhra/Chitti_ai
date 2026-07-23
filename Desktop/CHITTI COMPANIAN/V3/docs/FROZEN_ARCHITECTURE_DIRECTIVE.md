# CHITTI V2 — PERMANENT ENGINEERING POLICY
# FROZEN ARCHITECTURE & SAFE EVOLUTION DIRECTIVE
**(Rules 260 – 269 Enforced Across All Future Sprints)**

======================================================================
## 1. POLICY DIRECTIVE ACKNOWLEDGMENT
======================================================================

The **FROZEN ARCHITECTURE & SAFE EVOLUTION DIRECTIVE** has been accepted as a **PERMANENT, NON-NEGOTIABLE ENGINEERING POLICY** for CHITTI V2. It is permanently appended to `.agents/AGENTS.md` (Rules 260 – 269) and governs all future design, implementation, and certification tasks.

---

======================================================================
## 2. THE 10 NON-NEGOTIABLE ENGINEERING RULES
======================================================================

### 🔒 Rule 260 — Repository Structure Lock
Repository structure is **LOCKED**. Never move folders, rename folders, rename canonical modules, reorganize packages, relocate runtimes, or relocate capabilities unless explicitly requested by the project owner.

### 🔍 Rule 261 — Comprehensive Dependency Analysis
Assume every canonical module has unknown downstream dependencies. Always perform dependency analysis before modifying any existing module.

### 📈 Rule 262 — Engineering Priority Escalation
Engineering priorities MUST strictly follow:
1. **Reuse existing implementation**
2. **Extend existing extension points**
3. **Use adapters**
4. **Use providers**
5. **Use composition**
6. **Minimal modification of canonical modules**
7. **Repository restructuring ONLY if absolutely unavoidable**

### 🛡️ Rule 263 — No Architectural Redesign for Convenience
Never redesign architecture for convenience. Cleanliness is **NOT** sufficient justification. Existing stable architecture always wins.

### 📋 Rule 264 — Refactoring Proof Mandate
Every proposal to move, rename, split, merge, or relocate modules MUST prove measurable engineering benefit, zero regression risk, zero dependency breakage, zero API breakage, and zero runtime breakage. If this cannot be proven, the proposal is automatically rejected.

### 🔌 Rule 265 — Extension Patterns Over Code Modification
When adding new functionality, prefer Provider, Adapter, Registry, Plugin, Extension, Strategy patterns instead of modifying stable code.

### 🎯 Rule 266 — Minimal Safe Changes
If modifying an existing module is unavoidable, the implementation SHALL minimize code changes, preserve public APIs, preserve file paths, preserve contracts, preserve EventBus topics, preserve configuration, and preserve canonical ownership.

### 🚫 Rule 267 — No Duplicate Implementations
Never create duplicate implementations. Always search the repository first to determine `Already Exists`, `Partially Exists`, or `Missing`. Only implement the missing portion.

### 🔄 Rule 268 — Standard 8-Step Engineering Pipeline
Every future implementation SHALL follow:
`Repository Discovery` $\rightarrow$ `Ownership Verification` $\rightarrow$ `Dependency Analysis` $\rightarrow$ `Gap Analysis` $\rightarrow$ `Architecture Safety Review` $\rightarrow$ `Implementation` $\rightarrow$ `Verification` $\rightarrow$ `Certification`.

### 🛑 Rule 269 — Default Structural Freeze
Any proposal that changes repository structure SHALL require explicit approval from the project owner before implementation. Default assumption: **REPOSITORY STRUCTURE IS FROZEN**.

---

======================================================================
## 3. POLICY ENFORCEMENT & COMPLIANCE STATUS
======================================================================

```
######################################################################
                    ENGINEERING POLICY ADOPTION

                                STATUS:
                           ENFORCED & ACTIVE
                             RULES 260 - 269

   CHITTI V2 has reached architectural maturity.
   Stability, compatibility, and zero-regression strictly govern all
   future engineering phases.
######################################################################
```

# ⚙️ Operating Model — Augmented Teams GPT

**Purpose:**  
To define how the GPT and human collaborators co-create, evolve, and maintain shared knowledge.

---

## 🧠 Roles
- **Human Partner:** Provides intent, context, and domain insight.  
- **GPT Partner:** Synthesizes, structures, and evolves ideas into reusable assets.  

---

## 🔄 Knowledge Lifecycle
1. **Create** → Generate or refine content through chat or Canvas.  
2. **Store** → Commit structured outputs to `instructions/`, `assets/`, or `tools/`.  
3. **Evolve** → Review, version, and enhance knowledge collaboratively.  
4. **Integrate** → Feed updated insights back into GPT configuration.

---

## 📦 Update Flow
1. Draft or edit in GPT (Canvas).
2. Export finalized artifacts to Git repo.
3. Tag with metadata (version, author, date).
4. Commit & push with clear message (`[update] Tool definition refined`).

---

## 🔁 Versioning Philosophy
- Treat *knowledge as code*.  
- Use Git commits as a record of intellectual evolution.  
- Prefer small, meaningful commits over large dumps.


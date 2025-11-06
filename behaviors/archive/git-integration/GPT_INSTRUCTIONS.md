### Git Operation Rules (for GPT)

#### Commit / Store / Save / Push
When user says: “add / save / store / push / commit” →  
Use one of the following based on file type or source:

- **Text-based content (Markdown, code, notes):** use `commit_text`.
- **Uploaded document (PDF, Word, PowerPoint, Excel, etc.):** use `commit_document` and save it under the `assets/` folder.

##### Document Handling Rules
If a user uploads or references a document in chat (for example, a file shared through the interface) and says any of the *save keywords* (“add,” “save,” “store,” “push,” or “commit”), then:
1. The GPT should automatically store the file in the `assets/` directory.
2. Use `commit_document` to commit it with an appropriate message (e.g., “add uploaded document to assets”).
3. Always show the file name, path, and commit summary to the user **before** committing.
4. Wait for explicit confirmation before executing the commit.

Always confirm before running any commit operation.  
Always **show the proposed change or file summary before committing** to Git.

---

#### Retrieve / Search / Get
When user says: “get / search / find / retrieve” →  
Use `get_folder`, `get_tree`, or `search_files`.  
These are **auto-confirmed and read-only**.

If the user references a document (e.g., “get that presentation from assets”),  
locate it in the `assets/` folder using `search_files` or `get_folder`.

---

#### Sync / Update
When user says: “sync / update / pull latest” →  
Use `sync_repository`.  
Auto-confirm these actions since they are non-destructive.

---

#### Safety Rules
- Always confirm **commit** or **delete** actions.  
- Always **show edits, file diffs, or document summaries before committing.**  
- Always show the **proposed file path and commit message** for review.  
- Auto-confirm all **read-only** operations (get, search, tree, sync).  
- Never push or delete automatically unless explicitly told to.  
- Always store user-uploaded documents under `assets/` unless a specific path is requested.  
- If a potential overwrite is detected, show a clear diff or warning before proceeding.  
- Never perform a destructive action without explicit confirmation.

---

#### Examples
- “Add this to folder src/features” → `commit_text`  
- “Save this presentation” → `commit_document` → saved to `assets/`  
- “Store this PDF report” → `commit_document` → saved to `assets/`  
- “Get all files in assets” → `get_folder`  
- “Sync repo” → `sync_repository`  
- “Push changes” → `push_changes`

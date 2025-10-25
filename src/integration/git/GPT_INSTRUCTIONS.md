### Git Operation Rules (for GPT)

#### Commit / Store / Save / Push
When user says: “add / save / store / push / commit” → use `commit_text` or `commit_document`.
Always confirm before running these.
Show the user the proposed change **before committing** to Git.

#### Retrieve / Search / Get
When user says: “get / search / find / retrieve” → use `get_folder`, `get_tree`, or `search_files`. Auto-confirm these.

#### Sync / Update
When user says: “sync / update / pull latest” → use `sync_repository`. Auto-confirm.

#### Safety
- Always confirm **commit** or **delete** actions.
- Always **show edits or file diffs before committing**.
- Auto-confirm all **read-only** operations.
- Never push changes automatically unless explicitly told to.

#### Examples
- “Add this to folder src/features” → `commit_text`
- “Get all files in assets” → `get_folder`
- “Sync repo” → `sync_repository`
- “Push changes” → `push_changes`

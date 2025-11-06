# @update-code-docs

Ensure code files follow the documentation standard defined in `@code-documentation.mdc`.

## Purpose
- Review code files for a top-of-file Table of Contents and hierarchical section headers.
- Cross-check against `.cursor/rules/code-document,mdc` requirements.
- update the TOC and functional organization of code
- high lite changes to user for feednback

## How to Use
- Invoke this command during reviews or before commits to verify documentation compliance.
- Use alongside `@code-document,mdc` while editing files.

## Checklist (per file)
- [ ] TOC present at top with hierarchical numbering (1, 1.1, 1.1.1)
- [ ] Section headers mirror the TOC entries with the same numbering
- [ ] Behavior-oriented naming (WHAT happens WHEN)
- [ ] Functions/methods placed under the lowest applicable feature section
- [ ] COMMON/SHARED section lists cross-feature requirements supported
- [ ] TOC synchronized with code changes

## Notes
- Keep `code-document.mdc` open while applying fixes for quick reference.

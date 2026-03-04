# Update Script Maintenance Report

Date: 2026-03-04

- Hardened `scripts/process.py` request handling and URL joining logic to avoid malformed URL errors when WIPO returns absolute links.
- Added guardrails for upstream layout changes:
  - if treaty result links are not discovered, the script now exits cleanly without corrupting existing dataset files,
  - if no parsed rows are produced, the script preserves the current committed CSV.
- Updated GitHub Actions workflow at `.github/workflows/actions.yml`:
  - schedule + manual dispatch only,
  - explicit `permissions: contents: write`,
  - upgraded action versions and simplified execution steps.
- Current WIPO site structure has changed compared to legacy `ShowResults` parsing assumptions, so a full data-source migration is still required for fresh treaty updates.

# SQL Parser Verification Plan

Goal: certify the DDL parser as production-ready for PostgreSQL schema dumps by validating functionality, resilience, and documentation.

## 1. Coverage Inventory
- [x] Map documented requirements (`docs/parser_requirements.md`, README) to concrete parser behaviors.
- [x] Confirm that each construct (CREATE TABLE, ALTER TABLE, constraints, defaults, identifiers) has at least one automated test.

## 2. Edge-Case Test Expansion
- Add unit tests for:
  - [x] Quoted identifiers in schemas/tables/columns.
  - [x] Inline FOREIGN KEY clauses with `ON DELETE`/`ON UPDATE`, `MATCH`, and `DEFERRABLE` keywords.
  - [x] ALTER TABLE statements including ADD PRIMARY KEY/UNIQUE without explicit `CONSTRAINT name`.
  - [x] Multi-line CHECK constraints with nested parentheses and casts.
  - [x] Statements to skip (CREATE VIEW, CREATE INDEX, SET, psql meta commands) to ensure parser ignores them gracefully.
  - [x] Self-referencing FKs, circular references, isolated tables, schema inference (already covered) – reassert via regression suite.

## 3. Large Fixture Validation
- [x] Parse `examples/large_schema.sql` (3.7k synthetic lines) and assert table/constraint counts to catch regressions.
- [x] Capture golden snapshot (JSON) for a trimmed but complex fixture if performance allows.

## 4. Documentation & Diagnostics
- [x] Update README with summary of edge handling plus limitations.
- [x] Expand `docs/parser_requirements.md` with verification notes and known gaps.
- [x] Ensure logging guidance (debug-level) is mentioned for unsupported constructs.

## 5. Test Execution & Sign-off
- [x] Run full `pytest` suite inside the project venv.
- [x] Summarize verification results (tests added, behaviors confirmed, outstanding limitations) before sign-off.

### Sign-off Summary — 2026-02-26
- Added 10+ new parser unit tests covering quoted identifiers, inline FK options, ALTER TABLE variants, multiline checks, skip statements, schema inference, and a golden snapshot fixture.
- Confirmed `examples/large_schema.sql` integration test plus fixture snapshot catch regressions; parser handles self-references, circular dependencies, isolated tables, schema-qualified collisions.
- Documentation updated (README, requirements audit, verification plan) and CLI now exposes `WIZERD_LOG_LEVEL` knob for debugging unsupported statements.
- Outstanding limits: COPY/INSERT, GRANT/REVOKE, table inheritance remain out-of-scope but documented.

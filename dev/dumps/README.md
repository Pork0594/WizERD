Drop private SQL dumps in this directory while testing.

- Files inside `dumps/` are ignored automatically, so they will never be committed.
- Reference them via absolute or relative paths, e.g. `python wizerd.py generate dumps/my_db.sql -o outputs/diagrams/my_db.svg`.
- Keep the `.gitkeep` file so the directory itself stays in version control.
- Files inside `dumps/examples` are the example files for demoing the system **do not put private SQL dumps in the `examples` directory**.

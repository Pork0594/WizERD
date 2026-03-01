This folder stores ad-hoc ER diagram exports generated while developing WizERD.

- Anything ending in `.svg` is ignored by git so you can keep as many snapshots as you like.
- Point the CLI at this directory, e.g. `python wizerd.py generate examples/simple_schema.sql -o outputs/diagrams/demo.svg`.
- Leave the `.gitkeep` file in place so the folder stays in version control even when it’s empty.

# Task completion checklist
- Run the relevant Django validation command(s) after changes, at minimum `rtk python manage.py check` and any targeted tests available for the touched area.
- If migrations or model changes were made, run `rtk python manage.py makemigrations --check` or create and review migrations as appropriate.
- If new tooling is added later, record the exact lint/format/test commands in `suggested_commands.md`.
- Keep changes aligned with Django scaffold conventions unless the repository adopts stronger local standards.
- After onboarding, future work should use Serena symbol navigation for existing code instead of broad file reads when possible.
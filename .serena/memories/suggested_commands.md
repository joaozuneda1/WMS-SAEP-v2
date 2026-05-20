# Suggested commands
- Shell commands should be prefixed with `rtk` on this machine, per `/Users/jmzr/.codex/RTK.md`.
- Inspect repo files: `rtk rg --files`
- Run Django dev server: `rtk python manage.py runserver`
- Run Django checks: `rtk python manage.py check`
- Run migrations: `rtk python manage.py migrate`
- Create migrations: `rtk python manage.py makemigrations`
- Run tests: `rtk python -m pytest` if pytest is available in the environment, otherwise use the repo's chosen test command once defined.
- Format/lint commands are not yet defined in the repository scaffold; add them when the project introduces tooling.
- Useful system commands on Darwin: `rtk git status`, `rtk ls`, `rtk find`, `rtk sed`, `rtk rg`.
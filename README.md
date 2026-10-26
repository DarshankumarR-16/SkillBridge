# SkillBridge

SkillBridge is a VTU CSE mini-project for project recommendations, skill-gap analysis, personalized learning roadmaps, and student team matching.

## Phase 1 scope
This phase creates a Flask application factory, configuration, a responsive landing page, a health-check endpoint, and a custom 404 page. Database and recommendation features are intentionally deferred until Phase 1 is verified.

## Requirements
- Windows 10/11
- Python 3.11 or 3.12 recommended
- VS Code

## Setup on Windows PowerShell
```powershell
py --version
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

If PowerShell blocks activation for this terminal, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Then open http://127.0.0.1:5000 and http://127.0.0.1:5000/health.

## Security note
`.env` is ignored by Git. The fallback secret in `config.py` is only for local development; set a strong random `SECRET_KEY` in `.env` before sharing or deploying the app.

## Planned phases
1. Environment and working Flask page
2. MySQL, models, migrations, and seed data
3. Authentication and profiles
4. Skills and project catalogue
5. Recommendations
6. Skill gaps and learning roadmap
7. Teams and join requests
8. Dashboards and optional AI
9. Security and tests
10. Documentation, report, presentation, and viva

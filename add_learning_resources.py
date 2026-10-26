from app import create_app, db
from app.models import LearningResource

app = create_app()

resources = [
    {
        "title": "Flask Application Development",
        "description": "Learn Flask routing, templates, forms, and application structure.",
        "resource_type": "tutorial",
        "url": "https://flask.palletsprojects.com/en/stable/tutorial/",
        "difficulty": "intermediate",
    },
    {
        "title": "Git Branching and Collaboration",
        "description": "Practice branches, merging, and collaborative Git workflows.",
        "resource_type": "tutorial",
        "url": "https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell",
        "difficulty": "intermediate",
    },
    {
        "title": "SQLAlchemy ORM Tutorial",
        "description": "Learn ORM models, relationships, and database queries.",
        "resource_type": "tutorial",
        "url": "https://docs.sqlalchemy.org/en/20/tutorial/",
        "difficulty": "intermediate",
    },
    {
        "title": "Python Asyncio Documentation",
        "description": "Explore asynchronous programming, coroutines, and event loops.",
        "resource_type": "documentation",
        "url": "https://docs.python.org/3/library/asyncio.html",
        "difficulty": "advanced",
    },
    {
        "title": "Advanced SQL Query Techniques",
        "description": "Study window functions, common table expressions, and advanced queries.",
        "resource_type": "tutorial",
        "url": "https://www.postgresql.org/docs/current/tutorial-window.html",
        "difficulty": "advanced",
    },
    {
        "title": "Machine Learning Engineering for Production",
        "description": "Explore production machine learning systems and deployment concepts.",
        "resource_type": "course",
        "url": "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops",
        "difficulty": "advanced",
    },
]

with app.app_context():
    existing_titles = {
        title.lower()
        for (title,) in db.session.query(LearningResource.title).all()
    }

    added = 0

    try:
        for resource in resources:
            if resource["title"].lower() in existing_titles:
                print(f"Already exists: {resource['title']}")
                continue

            db.session.add(LearningResource(**resource))
            existing_titles.add(resource["title"].lower())
            added += 1

        db.session.commit()
        print(f"\nDone. Added {added} learning resources.")

    except Exception:
        db.session.rollback()
        raise

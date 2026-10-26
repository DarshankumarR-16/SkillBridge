
from app import create_app, db
from app.models import (
    Skill,
    Project,
    ProjectSkill,
    LearningResource,
)


def seed_skills():
    """Create the initial list of skills."""
    skills_data = [
        ("Python", "Programming", "Python programming fundamentals"),
        ("Java", "Programming", "Java programming and OOP"),
        ("SQL", "Database", "Relational databases and SQL queries"),
        ("HTML", "Web Development", "HTML page structure"),
        ("CSS", "Web Development", "CSS styling and layouts"),
        ("JavaScript", "Web Development", "JavaScript programming"),
        ("Flask", "Backend Development", "Python web development using Flask"),
        ("MySQL", "Database", "MySQL database management"),
        ("Machine Learning", "AI/ML", "Machine learning fundamentals"),
        ("Git", "Tools", "Version control using Git"),
    ]

    for name, category, description in skills_data:
        skill = Skill.query.filter_by(name=name).first()

        if skill is None:
            skill = Skill(
                name=name,
                category=category,
                description=description,
            )
            db.session.add(skill)

    db.session.flush()
    print("Skills added or already exist.")


def seed_projects():
    """Create sample projects and their required skills."""
    projects_data = [
        {
            "title": "Personal Portfolio Website",
            "description": "Build a personal website to showcase projects and skills.",
            "difficulty": "beginner",
            "category": "Web Development",
            "skills": [("HTML", 1), ("CSS", 1), ("JavaScript", 1)],
        },
        {
            "title": "Library Management System",
            "description": "Create a system to manage books, members, and borrowing records.",
            "difficulty": "intermediate",
            "category": "Application Development",
            "skills": [("Java", 2), ("MySQL", 2), ("SQL", 2)],
        },
        {
            "title": "SkillBridge Project Recommender",
            "description": "Recommend projects based on student skills and identify missing skills.",
            "difficulty": "intermediate",
            "category": "AI and Web Development",
            "skills": [("Python", 2), ("Flask", 2), ("MySQL", 2), ("SQL", 2)],
        },
        {
            "title": "Student Performance Prediction",
            "description": "Explore student data and build a basic machine learning model.",
            "difficulty": "advanced",
            "category": "Machine Learning",
            "skills": [("Python", 3), ("Machine Learning", 3), ("SQL", 2)],
        },
    ]

    for item in projects_data:
        project = Project.query.filter_by(title=item["title"]).first()

        if project is None:
            project = Project(
                title=item["title"],
                description=item["description"],
                difficulty=item["difficulty"],
                category=item["category"],
                is_active=True,
            )
            db.session.add(project)
            db.session.flush()

        for skill_name, required_level in item["skills"]:
            skill = Skill.query.filter_by(name=skill_name).first()

            if skill is None:
                raise ValueError(f"Required skill not found: {skill_name}")

            project_skill = ProjectSkill.query.filter_by(
                project_id=project.id,
                skill_id=skill.id,
            ).first()

            if project_skill is None:
                db.session.add(
                    ProjectSkill(
                        project_id=project.id,
                        skill_id=skill.id,
                        required_level=required_level,
                    )
                )

    print("Projects and project-skill requirements added or already exist.")


def seed_learning_resources():
    """Create learning resources for selected skills."""
    resources_data = [
        (
            "Python Official Tutorial",
            "Learn Python programming fundamentals.",
            "documentation",
            "https://docs.python.org/3/tutorial/",
            "Python",
            "beginner",
        ),
        (
            "W3Schools HTML Tutorial",
            "Learn the basics of HTML.",
            "tutorial",
            "https://www.w3schools.com/html/",
            "HTML",
            "beginner",
        ),
        (
            "W3Schools CSS Tutorial",
            "Learn CSS styling and layouts.",
            "tutorial",
            "https://www.w3schools.com/css/",
            "CSS",
            "beginner",
        ),
        (
            "Java Tutorials",
            "Learn Java programming fundamentals.",
            "tutorial",
            "https://dev.java/learn/",
            "Java",
            "beginner",
        ),
        (
            "MySQL Documentation",
            "Learn about MySQL databases and SQL.",
            "documentation",
            "https://dev.mysql.com/doc/",
            "MySQL",
            "beginner",
        ),
        (
            "Flask Documentation",
            "Learn to build web applications with Flask.",
            "documentation",
            "https://flask.palletsprojects.com/",
            "Flask",
            "beginner",
        ),
        (
            "Git Handbook",
            "Learn Git version control.",
            "guide",
            "https://docs.github.com/en/get-started/using-git/about-git",
            "Git",
            "beginner",
        ),
        (
            "Google Machine Learning Crash Course",
            "Study foundational machine learning concepts.",
            "course",
            "https://developers.google.com/machine-learning/crash-course",
            "Machine Learning",
            "beginner",
        ),
        (
            "MDN JavaScript Guide",
            "Learn JavaScript language fundamentals.",
            "documentation",
            "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
            "JavaScript",
            "beginner",
        ),
        (
            "SQL Tutorial",
            "Practice basic SQL concepts and queries.",
            "tutorial",
            "https://www.w3schools.com/sql/",
            "SQL",
            "beginner",
        ),
    ]

    for title, description, resource_type, url, skill_name, difficulty in resources_data:
        resource = LearningResource.query.filter_by(title=title).first()

        if resource is None:
            skill = Skill.query.filter_by(name=skill_name).first()

            if skill is None:
                raise ValueError(f"Required skill not found: {skill_name}")

            db.session.add(
                LearningResource(
                    title=title,
                    description=description,
                    resource_type=resource_type,
                    url=url,
                    skill_id=skill.id,
                    difficulty=difficulty,
                    is_active=True,
                )
            )

    print("Learning resources added or already exist.")


def main():
    app = create_app()

    with app.app_context():
        try:
            seed_skills()
            seed_projects()
            seed_learning_resources()
            db.session.commit()
            print("\nSUCCESS: SkillBridge sample data has been seeded.")
        except Exception:
            db.session.rollback()
            raise


if __name__ == "__main__":
    main()

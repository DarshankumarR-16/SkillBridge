
from app import db


class ProjectSkill(db.Model):
    __tablename__ = "project_skills"

    id = db.Column(db.Integer, primary_key=True)

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    skill_id = db.Column(
        db.Integer,
        db.ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
    )

    required_level = db.Column(
        db.Integer,
        nullable=False,
        default=1,
    )

    __table_args__ = (
        db.UniqueConstraint(
            "project_id",
            "skill_id",
            name="uq_project_skill",
        ),
    )

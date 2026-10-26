
from datetime import datetime, timezone

from app import db


class LearningResource(db.Model):
    __tablename__ = "learning_resources"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    resource_type = db.Column(
        db.String(30),
        nullable=False,
        default="tutorial",
    )
    url = db.Column(db.String(500), nullable=False)

    skill_id = db.Column(
        db.Integer,
        db.ForeignKey("skills.id", ondelete="SET NULL"),
        nullable=True,
    )

    difficulty = db.Column(
        db.String(20),
        nullable=False,
        default="beginner",
    )

    is_active = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<LearningResource {self.title}>"

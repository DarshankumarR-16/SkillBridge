
from datetime import datetime, timezone

from app import db


class UserSkill(db.Model):
    __tablename__ = "user_skills"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    skill_id = db.Column(
        db.Integer,
        db.ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
    )

    proficiency_level = db.Column(
        db.Integer,
        nullable=False,
        default=1,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "skill_id",
            name="uq_user_skill",
        ),
        db.CheckConstraint(
            "proficiency_level BETWEEN 1 AND 5",
            name="ck_user_skill_proficiency",
        ),
    )

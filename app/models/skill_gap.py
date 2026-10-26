
from datetime import datetime, timezone

from app import db


class SkillGap(db.Model):
    __tablename__ = "skill_gaps"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

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

    current_level = db.Column(db.Integer, nullable=False, default=0)
    required_level = db.Column(db.Integer, nullable=False, default=1)

    analyzed_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "project_id",
            "skill_id",
            name="uq_user_project_skill_gap",
        ),
        db.CheckConstraint(
            "current_level BETWEEN 0 AND 5",
            name="ck_skill_gap_current_level",
        ),
        db.CheckConstraint(
            "required_level BETWEEN 1 AND 5",
            name="ck_skill_gap_required_level",
        ),
    )

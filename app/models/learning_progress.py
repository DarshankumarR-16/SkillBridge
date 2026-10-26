
from datetime import datetime, timezone

from app import db


class LearningProgress(db.Model):
    __tablename__ = "learning_progress"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    resource_id = db.Column(
        db.Integer,
        db.ForeignKey("learning_resources.id", ondelete="CASCADE"),
        nullable=False,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="not_started",
    )

    progress_percent = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    started_at = db.Column(db.DateTime(timezone=True), nullable=True)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "resource_id",
            name="uq_learning_progress_user_resource",
        ),
        db.CheckConstraint(
            "progress_percent BETWEEN 0 AND 100",
            name="ck_learning_progress_percent",
        ),
        db.CheckConstraint(
            "status IN ('not_started', 'in_progress', 'completed')",
            name="ck_learning_progress_status",
        ),
    )

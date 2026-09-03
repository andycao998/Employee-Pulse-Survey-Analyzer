""" Audit table schema as represented in database """

from datetime import datetime, timezone
from employee_survey_analyzer.extensions import db
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

class AuditLog(db.Model):
    __tablename__ = "audit_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    method: Mapped[str] = mapped_column(String(10), nullable=False)         # GET/PUT/POST...
    action: Mapped[str] = mapped_column(String(20), nullable=False)         # endpoint hit
    actor: Mapped[str] = mapped_column(String(20), nullable=False, default="ADMIN")
    event: Mapped[str] = mapped_column(String(50), nullable=False)          # message of success/failure
    correlation_id: Mapped[str] = mapped_column(String(50), nullable=False) # UUID of request
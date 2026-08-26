from datetime import date, datetime, timezone
from employee_survey_analyzer.extensions import db
from sqlalchemy import ForeignKey, String, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

class SurveyRecord(db.Model):
    __tablename__ = "surveys"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    department: Mapped[str] = mapped_column(String(50), nullable=False)
    open_date: Mapped[date] = mapped_column(Date, nullable=False)
    close_date: Mapped[date] = mapped_column(Date, nullable=False)

    # each survey will contain a list of associated responses
    responses: Mapped[list["SurveyResponses"]] = relationship(
        back_populates="survey",
        cascade="all, delete-orphan"
    )

class SurveyResponses(db.Model):
    __tablename__ = "survey_responses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    # establishing the FK to the surveys table
    survey_id: Mapped[int] = mapped_column(ForeignKey("surveys.id"), nullable=False)

    survey: Mapped["SurveyRecord"] = relationship(back_populates="responses")
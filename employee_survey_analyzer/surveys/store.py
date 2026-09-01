""" Database layer for operations needed for business logic in service layer """

from datetime import datetime, timedelta
from employee_survey_analyzer.surveys.db_models import SurveyRecord, SurveyResponses
from employee_survey_analyzer.extensions import db
from sqlalchemy import ScalarResult, select, func

# ======================== SURVEY QUERIES ========================

def get_all_surveys(department: str | None) -> ScalarResult[SurveyRecord]:
    stmt = select(SurveyRecord).order_by(SurveyRecord.id)

    if department:
        stmt = stmt.where(func.lower(SurveyRecord.department) == department.lower())
    
    return db.session.execute(stmt).scalars()

def get_survey_by_id(survey_id: int) -> SurveyRecord | None:
    return db.session.get(SurveyRecord, survey_id)

def create_survey(record: SurveyRecord) -> None:
    db.session.add(record)
    db.session.flush() # flush to get the generated PK id before validating

def commit_change() -> None:
    db.session.commit()

def delete_survey(record: SurveyRecord) -> None:
    db.session.delete(record)
    db.session.commit()

# ======================== RESPONSE QUERIES ========================

def get_response_by_id(response_id: int) -> SurveyResponses | None:
    return db.session.get(SurveyResponses, response_id)

def get_all_responses(survey_id: int, sentiment: str | None, submission_date: datetime | None) -> ScalarResult[SurveyResponses]:
    stmt = select(SurveyResponses).where(SurveyResponses.survey_id == survey_id).order_by(SurveyResponses.id)

    if sentiment:
        stmt = stmt.where(SurveyResponses.sentiment == sentiment.upper())
    if submission_date:
        # filter on date range
        stmt = stmt.where(
            SurveyResponses.created_at >= submission_date,
            SurveyResponses.created_at < submission_date + timedelta(days=1)
        )
    
    return db.session.execute(stmt).scalars()

def create_response(record: SurveyResponses) -> None:
    db.session.add(record)
    db.session.flush() # flush to get the generated PK id before validating

def delete_response(record: SurveyResponses) -> None:
    db.session.delete(record)
    db.session.commit()
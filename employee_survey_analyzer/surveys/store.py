from employee_survey_analyzer.surveys.db_models import SurveyRecord, SurveyResponses
from employee_survey_analyzer.extensions import db
from sqlalchemy import ScalarResult, select

def get_all_surveys() -> ScalarResult[SurveyRecord]:
    stmt = select(SurveyRecord).order_by(SurveyRecord.id)
    return db.session.execute(stmt).scalars()

def get_survey_by_id(survey_id: int) -> SurveyRecord | None:
    return db.session.get(SurveyRecord, survey_id)

def create_survey(record: SurveyRecord) -> None:
    db.session.add(record)
    db.session.flush()

def commit_change() -> None:
    db.session.commit()

def delete_survey(record: SurveyRecord) -> None:
    db.session.delete(record)
    db.session.commit()




def get_response_by_id(response_id: int) -> SurveyResponses | None:
    return db.session.get(SurveyResponses, response_id)

def get_all_responses(survey_id: int) -> ScalarResult[SurveyResponses]:
    stmt = select(SurveyResponses).where(SurveyResponses.survey_id == survey_id).order_by(SurveyResponses.id)
    return db.session.execute(stmt).scalars()

def create_response(record: SurveyResponses) -> None:
    db.session.add(record)
    db.session.flush() # flush to get the generated PK id before validating

def delete_response(record: SurveyResponses) -> None:
    db.session.delete(record)
    db.session.commit()
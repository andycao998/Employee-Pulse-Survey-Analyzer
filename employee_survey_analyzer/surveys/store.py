from datetime import date
from employee_survey_analyzer.surveys.db_models import SurveyRecord, SurveyResponses
from employee_survey_analyzer.extensions import db
from employee_survey_analyzer.surveys.models import Survey, CreateSurveyDTO, UpdateSurveyDTO, Response, CreateResponseDTO
from employee_survey_analyzer.representations import SurveyNotFoundError, SurveyUnavailableError, SurveyUnmodifiableError
from sqlalchemy import select
from typing import Literal

Status = Literal["draft", "open", "closed"]

def get_survey_status(survey: Survey) -> Status:
    today = date.today()

    if today < survey.open_date:
        return "draft"
    elif today < survey.close_date:
        return "open"

    return "closed"

def get_all_surveys() -> list[dict[str, str]]:
    stmt = select(SurveyRecord).order_by(SurveyRecord.id)
    rows = db.session.execute(stmt)

    surveys = [Survey.model_validate(row[0]) for row in rows]

    return [
        {
            **survey.model_dump(),
            "status": get_survey_status(survey)
        }
        for survey in surveys
    ]

def get_survey_by_id(survey_id: int) -> Survey:
    row = db.session.get(SurveyRecord, survey_id)

    if row is None:
        raise SurveyNotFoundError(code="NOT_FOUND", status=404, detail=f"Survey (ID={survey_id}) not found")

    return Survey.model_validate(row)

def create_survey(survey_details: dict[str, str]) -> Survey:
    valid_survey = CreateSurveyDTO.model_validate(survey_details)

    record = SurveyRecord(**valid_survey.model_dump())

    survey = Survey.model_validate(record)

    db.session.add(record)
    db.session.commit()

    return survey

def update_survey(survey_id: int, survey_details: dict[str, str]) -> Survey:
    valid_survey = UpdateSurveyDTO.model_validate(survey_details)

    record = db.session.get(SurveyRecord, survey_id)
    if record is None:
        raise SurveyNotFoundError(code="NOT_FOUND", status=404, detail=f"Survey (ID={survey_id}) not found")
    if len(record.responses) > 0:
        raise SurveyUnmodifiableError(code="FORBIDDEN", status=403, detail="Survey has responses and can't be updated")

    record.title = valid_survey.title
    record.prompt = valid_survey.prompt
    record.close_date = valid_survey.close_date

    survey = Survey.model_validate(record)

    db.session.commit()

    return survey

def delete_survey(survey_id: int):
    record = db.session.get(SurveyRecord, survey_id)
    if record is None:
        return False

    db.session.delete(record)
    db.session.commit()
    return True






def get_all_responses(survey_id: int) -> list[Response]:
    stmt = select(SurveyResponses).where(SurveyResponses.survey_id == survey_id).order_by(SurveyResponses.id)
    rows = db.session.execute(stmt)

    return [Response.model_validate(row[0]) for row in rows]

def validate_response(survey_id: int) -> None:
    survey = get_survey_by_id(survey_id)

    today = date.today()
    if today < survey.open_date or today >= survey.close_date:
        raise SurveyUnavailableError(code="FORBIDDEN", status=403, detail=f"Survey (ID={survey_id}) not open")

def create_response(survey_id: int, response_details: dict[str, str]) -> Response:
    validate_response(survey_id)

    valid_response = CreateResponseDTO.model_validate({
        **response_details, 
        "survey_id": survey_id
    })

    record = SurveyResponses(**valid_response.model_dump())
    db.session.add(record)
    db.session.flush() # flush to get the generated PK id before validating

    response = Response.model_validate(record)

    db.session.commit()

    return response
from datetime import date
from employee_survey_analyzer.surveys.db_models import SurveyRecord, SurveyResponses
from employee_survey_analyzer.surveys.models import Survey, CreateSurveyDTO, UpdateSurveyDTO, Response, CreateResponseDTO
from employee_survey_analyzer.surveys import store
from employee_survey_analyzer.representations import SurveyNotFoundError, SurveyUnavailableError, SurveyUnmodifiableError, InvalidAuthorizationError
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
    rows = store.get_all_surveys()

    surveys = [Survey.model_validate(row) for row in rows]

    return [
        {
            **survey.model_dump(),
            "status": get_survey_status(survey)
        }
        for survey in surveys
    ]

def get_survey_by_id(survey_id: int) -> Survey:
    row = store.get_survey_by_id(survey_id)

    if row is None:
        raise SurveyNotFoundError(code="NOT_FOUND", status=404, detail=f"Survey (ID={survey_id}) not found")

    return Survey.model_validate(row)

def create_survey(survey_details: dict[str, str]) -> Survey:
    valid_survey = CreateSurveyDTO.model_validate(survey_details)

    record = SurveyRecord(**valid_survey.model_dump())
    store.create_survey(record)

    survey = Survey.model_validate(record)

    store.commit_change()

    return survey

def update_survey(survey_id: int, survey_details: dict[str, str]) -> Survey:
    valid_survey = UpdateSurveyDTO.model_validate(survey_details)

    record = store.get_survey_by_id(survey_id)
    if record is None:
        raise SurveyNotFoundError(code="NOT_FOUND", status=404, detail=f"Survey (ID={survey_id}) not found")
    if len(record.responses) > 0:
        raise SurveyUnmodifiableError(code="FORBIDDEN", status=403, detail="Survey has responses and can't be updated")

    record.title = valid_survey.title
    record.prompt = valid_survey.prompt
    record.close_date = valid_survey.close_date

    survey = Survey.model_validate(record)

    store.commit_change()

    return survey

def delete_survey(survey_id: int) -> None:
    record = store.get_survey_by_id(survey_id)
    if record is None:
        raise SurveyNotFoundError(code="NOT_FOUND", status=404, detail=f"Survey (ID={survey_id}) not found")

    store.delete_survey(record)





def get_all_responses(survey_id: int) -> list[Response]:
    rows = store.get_all_responses(survey_id)
    return [Response.model_validate(row) for row in rows]

def validate_response(survey_id: int) -> None:
    survey = get_survey_by_id(survey_id)

    today = date.today()
    if today < survey.open_date:
        raise SurveyUnavailableError(code="FORBIDDEN", status=403, detail=f"Survey (ID={survey_id}) not open yet")
    if today >= survey.close_date:
        raise SurveyUnavailableError(code="FORBIDDEN", status=403, detail=f"Survey (ID={survey_id}) already closed")

def create_response(survey_id: int, response_details: dict[str, str]) -> Response:
    validate_response(survey_id)

    valid_response = CreateResponseDTO.model_validate({
        **response_details, 
        "survey_id": survey_id
    })

    record = SurveyResponses(**valid_response.model_dump())
    store.create_response(record)

    response = Response.model_validate(record)

    store.commit_change()

    return response

def validate_response_deletion(body: dict[str, str]) -> None:
    confirm_deletion = body.get("confirm_deletion")

    # missing confirmation in body will cause deletion to fail
    if confirm_deletion is None or confirm_deletion != "true":
        raise InvalidAuthorizationError(code="FORBIDDEN", status=403, detail=f"Invalid confirmation")

def delete_response(response_id: int, body: dict[str, str]):
    validate_response_deletion(body)

    record = store.get_response_by_id(response_id)
    if record is None:
        raise SurveyNotFoundError(code="NOT_FOUND", status=404, detail=f"Response (ID={response_id}) not found")

    store.delete_response(record)
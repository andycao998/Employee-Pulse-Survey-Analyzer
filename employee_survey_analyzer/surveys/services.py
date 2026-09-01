""" Business logic for performing validation and directing database operations on surveys and responses"""

from datetime import date, datetime
from employee_survey_analyzer.surveys.db_models import SurveyRecord, SurveyResponses
from employee_survey_analyzer.surveys.models import Survey, CreateSurveyDTO, UpdateSurveyDTO, Response, CreateResponseDTO
from employee_survey_analyzer.surveys import store
from employee_survey_analyzer.representations import SurveyNotFoundError, SurveyUnavailableError, SurveyUnmodifiableError, InvalidAuthorizationError
from employee_survey_analyzer.analysis.service import analyze_sentiment, redact_pii, summarize_key_phrases
from typing import Literal, TypedDict

# ======================== SURVEY LOGIC ========================

Status = Literal["draft", "open", "closed"]

def get_survey_status(survey: Survey) -> Status:
    """ Determine survey status based on dates since it isn't stored in survey model """

    today = date.today()

    if today < survey.open_date:
        return "draft"
    elif today < survey.close_date:
        return "open"

    return "closed"

def get_all_surveys(department: str | None) -> list[dict[str, str]]:
    """ Retrieve all surveys and append their open/closed status to output """

    rows = store.get_all_surveys(department)

    surveys = [Survey.model_validate(row) for row in rows]

    return [
        {
            **survey.model_dump(),
            "status": get_survey_status(survey)
        }
        for survey in surveys
    ]

def get_survey_by_id(survey_id: int) -> Survey:
    """ Validate survey exists and return output """

    row = store.get_survey_by_id(survey_id)

    if row is None:
        raise SurveyNotFoundError(code="NOT_FOUND", status=404, detail=f"Survey (ID={survey_id}) not found")

    return Survey.model_validate(row)

class Summary(TypedDict):
    survey_id: int
    response_count: int
    sentiment_distribution: dict[str, float]
    top_phrases: list[dict[str, str | int]]

def generate_survey_summary(survey_id: int) -> Summary:
    """ Compile a survey's overall response mood, tracking sentiment and key phrase breakdowns """

    record = store.get_survey_by_id(survey_id)
    if record is None:
        raise SurveyNotFoundError(code="NOT_FOUND", status=404, detail=f"Survey (ID={survey_id}) not found")
    
    responses = record.responses
    response_count = len(responses)
    sentiment_counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0, "MIXED": 0}
    response_bodies = []
    for response in responses:
        response_bodies.append(response.body)
        sentiment = response.sentiment
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

    sentiment_dist = {
        sentiment: round(count / response_count, 3)
        for sentiment, count in sentiment_counts.items()
    }

    top_phrases = summarize_key_phrases(response_bodies)

    return {
        "survey_id": survey_id,
        "response_count": len(responses),
        "sentiment_distribution": sentiment_dist,
        "top_phrases": top_phrases
    }

def create_survey(survey_details: dict[str, str]) -> Survey:
    """ Validate inputted survey information before delegating survey creation in database """

    valid_survey = CreateSurveyDTO.model_validate(survey_details)

    record = SurveyRecord(**valid_survey.model_dump())
    store.create_survey(record)

    survey = Survey.model_validate(record)

    store.commit_change()

    return survey

def update_survey(survey_id: int, survey_details: dict[str, str]) -> Survey:
    """ Only allow survey title, prompt, and close dates to be updated for surveys with no responses """

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
    """ Validate survey exists before deletion """

    record = store.get_survey_by_id(survey_id)
    if record is None:
        raise SurveyNotFoundError(code="NOT_FOUND", status=404, detail=f"Survey (ID={survey_id}) not found")

    store.delete_survey(record)

# ======================== RESPONSE LOGIC ========================

def get_all_responses(survey_id: int, sentiment: str | None, submission_date: str | None) -> list[Response]:
    """ Retrieve all responses for a given survey """

    # Convert from string to datetime expected in DB
    submission_datetime = None
    if submission_date:
        submission_datetime = datetime.strptime(submission_date, "%Y-%m-%d")

    rows = store.get_all_responses(survey_id, sentiment, submission_datetime)
    return [Response.model_validate(row) for row in rows]

def validate_response(survey_id: int) -> None:
    """ Validate survey response eligibility with separate errors for not-yet-open surveys and already-closed surveys """

    survey = get_survey_by_id(survey_id)

    today = date.today()
    if today < survey.open_date:
        raise SurveyUnavailableError(code="FORBIDDEN", status=403, detail=f"Survey (ID={survey_id}) not open yet")
    if today >= survey.close_date:
        raise SurveyUnavailableError(code="FORBIDDEN", status=403, detail=f"Survey (ID={survey_id}) already closed")

def create_response(survey_id: int, response_details: dict[str, str]) -> Response:
    """ Validate response fields and survey status before creation """

    validate_response(survey_id)

    response_details["body"] = redact_pii(response_details["body"])
    sentiment, score = analyze_sentiment(response_details["body"])

    valid_response = CreateResponseDTO.model_validate({
        **response_details, 
        "survey_id": survey_id,
        "sentiment": sentiment,
        "confidence_score": score
    })

    record = SurveyResponses(**valid_response.model_dump())
    store.create_response(record)
    
    response = Response.model_validate(record)

    store.commit_change()

    return response

def validate_response_deletion(body: dict[str, str]) -> None:
    """ Additional check for confirmation of deletion """

    confirm_deletion = body.get("confirm_deletion")

    # missing confirmation in body will cause deletion to fail
    if confirm_deletion is None or confirm_deletion != "true":
        raise InvalidAuthorizationError(code="FORBIDDEN", status=403, detail=f"Invalid confirmation")

def delete_response(response_id: int, body: dict[str, str]):
    """ Removal response for admins only with additional step """

    validate_response_deletion(body)

    record = store.get_response_by_id(response_id)
    if record is None:
        raise SurveyNotFoundError(code="NOT_FOUND", status=404, detail=f"Response (ID={response_id}) not found")

    store.delete_response(record)
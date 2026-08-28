""" Envelopes for uniform JSON responses for outputs and errors """

from employee_survey_analyzer.surveys.models import Survey, Response
from flask import jsonify

def dashboard_envelope(surveys: list[dict[str, str]]):
    return jsonify(count=len(surveys), items=surveys)

def list_envelope(surveys: list[Survey] | list[Response]):
    return jsonify(count=len(surveys), items=[s.model_dump(mode="json") for s in surveys])

def single_envelope(survey: Survey | Response):
    return jsonify(survey.model_dump(mode="json"))

def error_response(code: str, status: int, request_id: str, detail: str | None = None):
    return jsonify(error=code, detail=detail, request_id=request_id), status

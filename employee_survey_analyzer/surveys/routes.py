from flask import Blueprint, jsonify, request
from employee_survey_analyzer.surveys import services
from employee_survey_analyzer.responses import dashboard_envelope, list_envelope, single_envelope
from employee_survey_analyzer.decorators import requires_admin

surveys_bp = Blueprint("surveys", __name__)

# GET /api/v1/surveys/dashboard
@surveys_bp.get("/dashboard")
def view_all_surveys():
    return dashboard_envelope(services.get_all_surveys())

# GET /api/v1/surveys/{id}
@surveys_bp.get("/<int:survey_id>")
def view_survey_by_id(survey_id: int):
    survey = services.get_survey_by_id(survey_id)
    return single_envelope(survey)

# POST /api/v1/surveys
@surveys_bp.post("")
@requires_admin
def create_new_survey():
    body: dict[str, str] = request.get_json(silent=True) or {}
    return single_envelope(services.create_survey(body)), 201

# PUT /api/v1/surveys/{id}
@surveys_bp.put("/<int:survey_id>")
@requires_admin
def update_existing_survey(survey_id: int):
    body: dict[str, str] = request.get_json(silent=True) or {}

    survey = services.update_survey(survey_id, body)
    return single_envelope(survey), 200

# DELETE /api/v1/surveys/{id}
@surveys_bp.delete("/<int:survey_id>")
@requires_admin
def delete_existing_survey(survey_id: int):
    services.delete_survey(survey_id)
    return jsonify(status="DELETED"), 204 # TODO: this msg no longer shows on successful deletion



# GET /api/v1/surveys/{id}/responses
@surveys_bp.get("/<int:survey_id>/responses")
def view_all_responses(survey_id: int):
    return list_envelope(services.get_all_responses(survey_id))

# POST /api/v1/surveys/{id}/responses
@surveys_bp.post("/<int:survey_id>/responses")
def create_new_response(survey_id: int):
    body: dict[str, str] = request.get_json(silent=True) or {}
    return single_envelope(services.create_response(survey_id, body)), 201

@surveys_bp.delete("/responses/<int:response_id>")
@requires_admin
def authorized_delete_response(response_id: int):
    body: dict[str, str] = request.get_json(silent=True) or {}

    services.delete_response(response_id, body)
    return jsonify(status="DELETED"), 204
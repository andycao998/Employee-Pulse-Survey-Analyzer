from flask import Blueprint, jsonify, request
from employee_survey_analyzer.surveys import store
from employee_survey_analyzer.responses import dashboard_envelope, list_envelope, single_envelope

surveys_bp = Blueprint("surveys", __name__)

# GET /api/v1/surveys/dashboard
@surveys_bp.get("/dashboard")
def view_all_surveys():
    return dashboard_envelope(store.get_all_surveys())

# GET /api/v1/surveys/{id}
@surveys_bp.get("/<int:survey_id>")
def view_survey_by_id(survey_id: int):
    survey = store.get_survey_by_id(survey_id)
    return single_envelope(survey)

# POST /api/v1/surveys
@surveys_bp.post("")
def create_new_survey():
    body: dict[str, str] = request.get_json(silent=True) or {}
    return single_envelope(store.create_survey(body)), 201

# PUT /api/v1/surveys/{id}
@surveys_bp.put("/<int:survey_id>")
def update_existing_survey(survey_id: int):
    body: dict[str, str] = request.get_json(silent=True) or {}

    survey = store.update_survey(survey_id, body)
    return single_envelope(survey), 200

# DELETE /api/v1/surveys/{id}
@surveys_bp.delete("/<int:survey_id>")
def delete_existing_survey(survey_id: int):
    success = store.delete_survey(survey_id)
    if success:
        return jsonify(status="DELETED"), 204
    
    return jsonify(error="NOT_FOUND"), 404



# GET /api/v1/surveys/{id}/responses
@surveys_bp.get("/<int:survey_id>/responses")
def view_all_responses(survey_id: int):
    return list_envelope(store.get_all_responses(survey_id))

# POST /api/v1/surveys/{id}/responses
@surveys_bp.post("/<int:survey_id>/responses")
def create_new_response(survey_id: int):
    body: dict[str, str] = request.get_json(silent=True) or {}
    return single_envelope(store.create_response(survey_id, body)), 201
""" Endpoint for viewing audit table """

from flask import Blueprint, jsonify, Response
from employee_survey_analyzer.logging import store

logging_bp = Blueprint("logs", __name__)

# ======================== SURVEY ENDPOINTS ========================

# GET /logs
@logging_bp.get("")
def view_all_logs() -> Response:
    rows = store.view_audit_logs()

    return jsonify([
        {
            "id": row.id,
            "timestamp": row.timestamp.isoformat(),
            "method": row.method,
            "action": row.action,
            "actor": row.actor,
            "event": row.event,
            "correlation_id": row.correlation_id,
        }
        for row in rows
    ])
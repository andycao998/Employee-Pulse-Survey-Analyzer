""" Health-check endpoints for application liveness and readiness """

from flask import Blueprint, jsonify
from employee_survey_analyzer.health.store import ping_db

health_bp = Blueprint("health", __name__)

# GET /health/live
@health_bp.get("/live")
def liveness():
    """ Check if application process is alive """

    return jsonify(status="OK"), 200

# GET /health/ready
@health_bp.get("/ready")
def readiness():
    """ Check if downstream database is reachable and nothing else """

    if ping_db():
        return jsonify(status="READY"), 200

    return jsonify(status="NOT_READY"), 503
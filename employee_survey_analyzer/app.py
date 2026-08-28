import os
import uuid
import time
from flask import Flask, g, request, Response
from flask_migrate import Migrate
from pydantic import ValidationError
from employee_survey_analyzer.surveys.routes import surveys_bp
from employee_survey_analyzer.health.routes import health_bp
from employee_survey_analyzer.extensions import db
from employee_survey_analyzer.responses import error_response
from employee_survey_analyzer.representations import SurveyNotFoundError, SurveyInvalidDateRangeError, SurveyUnavailableError, SurveyUnmodifiableError, InvalidAuthorizationError
from employee_survey_analyzer.logging import logger

migrate = Migrate()

def create_app():
    app = Flask(__name__)

    app.register_blueprint(health_bp, url_prefix="/health")
    app.register_blueprint(surveys_bp, url_prefix="/api/v1/surveys")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"] 
    db.init_app(app) 
    migrate.init_app(app, db) 

    @app.before_request
    def start_request():
        g.request_id = str(uuid.uuid4())
        g.start_time = time.perf_counter()

    @app.after_request
    def log_request(response: Response) -> Response:
        duration = time.perf_counter() - g.start_time

        logger.info(
            "request completed",
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration=duration,
            correlation_id=g.request_id
        )

        return response

    # Error Handlers
    @app.errorhandler(SurveyInvalidDateRangeError)
    def handle_survey_date_error(error: SurveyInvalidDateRangeError):
        return error_response(code=error.code, status=error.status, detail=error.detail, request_id=g.request_id)

    @app.errorhandler(SurveyUnavailableError)
    def handle_survey_unavailable_error(error: SurveyUnavailableError):
        return error_response(code=error.code, status=error.status, detail=error.detail, request_id=g.request_id)

    @app.errorhandler(SurveyUnmodifiableError)
    def handle_survey_unmodifiable_error(error: SurveyUnmodifiableError):
        return error_response(code=error.code, status=error.status, detail=error.detail, request_id=g.request_id)

    @app.errorhandler(SurveyNotFoundError)
    def handle_api_error(error: SurveyNotFoundError):
        return error_response(code=error.code, status=error.status, detail=error.detail, request_id=g.request_id)

    @app.errorhandler(InvalidAuthorizationError)
    def handle_authorization_error(error: InvalidAuthorizationError):
        return error_response(code=error.code, status=error.status, detail=error.detail, request_id=g.request_id)

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        first_error = error.errors()[0]
        detail_str = f"{first_error['loc']}: {first_error['msg']}"

        # 422 - UNPROCESSABLE_CONTENT > more specific than a 400
        return error_response(code="VALIDATION_FAILED", status=422, detail=detail_str, request_id=g.request_id)

    @app.errorhandler(Exception)
    def handle_unhandled_exception(error: Exception):
        return error_response(code="INTERNAL", status=500, detail="An unexpected error occurred", request_id=g.request_id)

    @app.errorhandler(404)
    def handle_resource_not_found(error: Exception):
        return error_response(code="NOT_FOUND", status=404, detail="No route for the given path", request_id=g.request_id)

    return app
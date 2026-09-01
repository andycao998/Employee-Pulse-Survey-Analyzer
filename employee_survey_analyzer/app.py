""" App factory for registering blueprints, starting logging, and global exception handling """

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
from employee_survey_analyzer.representations import SurveyError, InvalidAuthorizationError
from employee_survey_analyzer.logging import logger
from botocore.exceptions import BotoCoreError, ClientError

# Common AWS errors and their codes
_CLIENT_FAULT_STATUS = {
    "AccessDeniedException": 403,
    "AccessDenied": 403,
    "UnrecognizedClientException": 403,
    "ValidationException": 422,
    "InvalidParameterException": 422,
    "InvalidParameterValueException": 422,
    "TextSizeLimitExceededException": 422,
    "InvalidRequestException": 422,
    "UnsupportedLanguagePairException": 422,
    "ThrottlingException": 429,
    "TooManyRequestsException": 429,
    "ResourceNotFoundException": 404,
}

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
        g.request_event = "Request completed"

    @app.after_request
    def log_request(response: Response) -> Response:
        duration = time.perf_counter() - g.start_time

        logger.info(
            event=g.request_event,
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration=duration,
            correlation_id=g.request_id
        )

        return response

    # Error Handlers

    # catches SurveyInvalidDateRangeError, SurveyUnavailableError, SurveyUnmodifiableError, SurveyNotFoundError
    @app.errorhandler(SurveyError)
    def handle_survey_error(error: SurveyError):
        g.request_event = f"Request failed: {type(error).__name__}"
        return error_response(code=error.code, status=error.status, detail=error.detail, request_id=g.request_id)

    @app.errorhandler(InvalidAuthorizationError)
    def handle_authorization_error(error: InvalidAuthorizationError):
        g.request_event = "Request failed: InvalidAuthorizationError"
        return error_response(code=error.code, status=error.status, detail=error.detail, request_id=g.request_id)

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        first_error = error.errors()[0]
        detail_str = f"{first_error['loc']}: {first_error['msg']}"
        g.request_event = "Request failed: ValidationError"
        return error_response(code="VALIDATION_FAILED", status=422, detail=detail_str, request_id=g.request_id)

    @app.errorhandler(ClientError)
    def handle_aws_client_error(error):
        # only extracting the code from aws so we don't reveal too much info to client
        aws_code = error.response.get("Error", {}).get("Code", "UnknownAwsError")
        status = _CLIENT_FAULT_STATUS.get(aws_code, 502)
        g.request_event = f"AWS call failed: {type(error).__name__}" # internal log to see error
        return error_response(code="AWS_ERROR", status=status, detail=aws_code, request_id=g.request_id)

    @app.errorhandler(BotoCoreError)
    def handle_botocore_error(error):
        details = "AWS SDK/configuration error"
        g.request_event = details + ": " + type(error).__name__
        return error_response(code="AWS_CONFIGURATION_ERROR", status=500, detail=details, request_id=g.request_id)

    @app.errorhandler(Exception)
    def handle_unhandled_exception(error: Exception):
        g.request_event = f"Request failed: {type(error).__name__}"
        return error_response(code="INTERNAL", status=500, detail="An unexpected error occurred", request_id=g.request_id)

    @app.errorhandler(404)
    def handle_resource_not_found(error: Exception):
        g.request_event = "Invalid request path"
        return error_response(code="NOT_FOUND", status=404, detail="No route for the given path", request_id=g.request_id)

    return app
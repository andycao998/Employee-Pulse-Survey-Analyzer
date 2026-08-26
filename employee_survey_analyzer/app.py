import os
from flask import Flask
from flask_migrate import Migrate
from pydantic import ValidationError
from employee_survey_analyzer.surveys.routes import surveys_bp
from employee_survey_analyzer.extensions import db
from employee_survey_analyzer.responses import error_response
from employee_survey_analyzer.representations import SurveyNotFoundError, SurveyInvalidDateRangeError, SurveyUnavailableError, SurveyUnmodifiableError

migrate = Migrate()

def create_app():
    app = Flask(__name__)

    app.register_blueprint(surveys_bp, url_prefix="/api/v1/surveys")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"] 
    db.init_app(app) 
    migrate.init_app(app, db) 


    # Error Handlers
    @app.errorhandler(SurveyInvalidDateRangeError)
    def handle_survey_date_error(error: SurveyInvalidDateRangeError):
        return error_response(error.code, error.status, error.detail)

    @app.errorhandler(SurveyUnavailableError)
    def handle_survey_unavailable_error(error: SurveyUnavailableError):
        return error_response(error.code, error.status, error.detail)

    @app.errorhandler(SurveyUnmodifiableError)
    def handle_survey_unmodifiable_error(error: SurveyUnmodifiableError):
        return error_response(error.code, error.status, error.detail)

    @app.errorhandler(SurveyNotFoundError)
    def handle_api_error(error: SurveyNotFoundError):
        return error_response(error.code, error.status, error.detail)

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        first_error = error.errors()[0]
        detail_str = f"{first_error['loc']}: {first_error['msg']}"

        # 422 - UNPROCESSABLE_CONTENT > more specific than a 400
        return error_response("VALIDATION_FAILED", 422, detail_str)

    @app.errorhandler(Exception)
    def handle_unhandled_exception(error: Exception):
        return error_response("INTERNAL", 500, "An unexpected error occurred")

    @app.errorhandler(404)
    def handle_resource_not_found(error):
        return error_response("NOT_FOUND", 404, "No route for the given path")

    return app
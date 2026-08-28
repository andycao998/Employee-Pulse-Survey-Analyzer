""" Database layer check for health """

from employee_survey_analyzer.extensions import db
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError

def ping_db() -> bool:
    try:
        db.session.execute(select(1))
        return True
    except DBAPIError:
        return False
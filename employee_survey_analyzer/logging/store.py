""" Database layer for interactions with audit table and logs """

from employee_survey_analyzer.extensions import db
from employee_survey_analyzer.logging.db_models import AuditLog
from sqlalchemy import ScalarResult, select, func

def create_audit_log(log: AuditLog):
    db.session.add(log)
    db.session.commit()

def view_audit_logs() -> ScalarResult[AuditLog]:
    stmt = select(AuditLog).order_by(AuditLog.timestamp.desc())
    return db.session.execute(stmt).scalars()
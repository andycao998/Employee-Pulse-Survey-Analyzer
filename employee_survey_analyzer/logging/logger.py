""" Accept logging requests and audit admin operations """

import time
from employee_survey_analyzer.logging.log_config import logger
from employee_survey_analyzer.logging.db_models import AuditLog
from employee_survey_analyzer.logging import store

def log_request(event: str, method: str, path: str, status_code: int, start_time: float, correlation_id: str):
    duration = time.perf_counter() - start_time

    logger.info(
        event=event,
        method=method,
        path=path,
        status_code=status_code,
        duration=duration,
        correlation_id=correlation_id
    )

    log_details = {
        "method": method,
        "action": path,
        "event": event,
        "correlation_id": correlation_id
    }

    if create_audit_log(method, path):
        audit_log = AuditLog(          
            **log_details
        )

        store.create_audit_log(audit_log)

def create_audit_log(method: str, path: str) -> bool:
    admin_ops = ["POST", "PUT", "DELETE"]
    is_create_response = path[-10:] == "/responses" # POST create response is explicitly not logged

    if is_create_response:
        return False

    if "api/v1/surveys" in path and method in admin_ops:
        return True

    return False
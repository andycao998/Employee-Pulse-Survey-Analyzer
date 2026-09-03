""" Simple configuration for logging requests in console output """

import structlog

structlog.configure(processors=[structlog.processors.JSONRenderer()])

logger = structlog.get_logger()
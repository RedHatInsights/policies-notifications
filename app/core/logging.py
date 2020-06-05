import logging


class PrometheusAccessLogFilter(logging.Filter):
    """
    If the uvicorn access log includes /metrics access log, do not log it to access log
    """
    def filter(self, record: logging.LogRecord):
        return "/metrics" not in record.scope["path"] and super().filter(record)

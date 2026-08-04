from __future__ import annotations
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "time": self.formatTime(record, self.datefmt),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage()
        }
        if hasattr(record, "contract_id"):
            log_data["contract_id"] = record.contract_id
        if hasattr(record, "agent_name"):
            log_data["agent_name"] = record.agent_name
        return json.dumps(log_data)

def get_logger(name: str, use_json: bool = False) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        if use_json:
            handler.setFormatter(JSONFormatter())
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

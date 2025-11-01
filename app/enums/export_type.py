from enum import Enum


class ExportType(str, Enum):
    CSV = "csv"
    JSON = "json"

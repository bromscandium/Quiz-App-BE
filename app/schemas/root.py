from pydantic import BaseModel


class RootResponse(BaseModel):
    status_code: int
    detail: str
    result: str

from pydantic import BaseModel


class Base(BaseModel):
    model_config = {"from_attributes": True}

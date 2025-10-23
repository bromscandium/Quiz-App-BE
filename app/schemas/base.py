from pydantic import ConfigDict, BaseModel


class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

from pydantic import BaseModel


class UserIdentification(BaseModel):
    utilizador_id: int
    utilizador: str

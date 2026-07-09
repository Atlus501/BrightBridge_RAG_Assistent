from pydantic import BaseModel

#data structure for requests
class RAG_Request_Body(BaseModel):
    past_conv: list[str]
    prompt: str

class Context_Request_Body(BaseModel):
    session_id: str | None
    password: str
    actor_id: str
    conv_to_be_saved: list[str] | str
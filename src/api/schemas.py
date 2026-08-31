from pydantic import BaseModel

class ChatRequest(BaseModel):
    query:str


class Source(BaseModel):
    chunk_id:str
    score:float
    chunk:str|None

class ChatResponse(BaseModel):
    answer:str
    sources:list[Source]
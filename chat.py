from typing import Any, Dict, List

from pydantic import BaseModel
from agent import AgentResponse
from gemma import Gemma

class ChatResponse(BaseModel):
    agent: Dict[str, Any]
    steps: List[str]

class Chat:
    
    @classmethod
    def invoke(cls, input_text: str):
        res = Gemma.llm.invoke(input_text)
        return ChatResponse(agent={"output": res}, steps=[])
    
if __name__ == "__main__":
    print(Gemma.llm.invoke("こんにちわ！"))
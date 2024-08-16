from typing import Any, Dict, List

from pydantic import BaseModel
from agent import AgentResponse
# from gemma import Gemma as ModelClass
from gpt_4o_mini import Gpt4oMini as ModelClass

class ChatResponse(BaseModel):
    agent: Dict[str, Any]
    steps: List[str]

class Chat:
    
    @classmethod
    def invoke(cls, input_text: str):
        res = ModelClass.llm.invoke(input_text)
        return ChatResponse(agent={"output": res.content}, steps=[])
    
if __name__ == "__main__":
    print(ModelClass.llm.invoke("こんにちわ！"))
from typing import Any, Union
from langchain_openai import ChatOpenAI
from config import openai_api_key
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult
import datetime

class CustomHandler(BaseCallbackHandler):

    def __init__(self) -> None:
        super().__init__()
        self.started_at: datetime.datetime = None


    def on_llm_start(self, serialized, prompts, **kwargs):
        self.started_at = datetime.datetime.now()
        print("#### on_llm_start ####")
        print(f"Start at {self.started_at}")
        print(f"{prompts=}")
        print("######################")
        
    def on_llm_end(self, result: LLMResult, **kwargs):
        print("#### on_llm_end ####")
        print(f"LLM Output: {result.generations[0][0].text}")
        print(f"{datetime.datetime.now()- self.started_at.second=}")
        print("####################")

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when LLM errors."""
        print("### on_llm_error ###")
        print(f"{error=}")
        print("####################")


class Gpt4oMini:

    llm = ChatOpenAI(
        model='gpt-4o-mini',
        temperature=0.7,
        openai_api_key=openai_api_key,
        callbacks=[CustomHandler()],
        streaming=False,
        timeout=60)

if __name__ == '__main__':
    print(Gpt4oMini.llm)
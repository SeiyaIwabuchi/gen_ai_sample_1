from typing import Any, Union
from langchain_openai import ChatOpenAI
from config import openai_api_key
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult

class CustomHandler(BaseCallbackHandler):

    def on_llm_start(self, serialized, prompts, **kwargs):
        print("LLM is starting...")
        print(f"{prompts=}")
        
    def on_llm_end(self, result: LLMResult, **kwargs):
        print(f"LLM Output: {result.generations[0][0].text}")

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
        callbacks=[CustomHandler()])

if __name__ == '__main__':
    print(Gpt4oMini.llm)
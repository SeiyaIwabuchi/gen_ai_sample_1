import asyncio
import queue
from typing import Any, AsyncIterable, Dict, List, Union
from fastapi import WebSocket
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.callbacks.base import BaseCallbackHandler
from pydantic import BaseModel
from langchain import hub
from langchain.schema import (
    AgentFinish,
)

# from gemma import Gemma
from gpt_4o_mini import Gpt4oMini as ModelClass
# from gemma import Gemma as ModelClass
# from tools.shell_tool import ShellTool
from tools.create_file import FileCreationTool
from tools.shell_tool import ShellTool


class AgentResponse(BaseModel):
    agent: Dict[str, Any]
    steps: List[str]


class CustomHandler(BaseCallbackHandler):
    def __init__(self):
        self.steps = []

    def on_agent_action(self, action, **kwargs):
        self.steps.append(f"Action: {action}")
        print("### on_agent_action ###")
        print(f"{action=}")
        print("#######################\n")

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Run on agent end."""
        print("### on_agent_finish ###")
        print(f"{finish=}")
        print("#######################\n")

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> Any:
        """Run when tool starts running."""
        print("### on_tool_start ###")
        print(f"{input_str=}")
        print("#####################\n")

    def on_tool_end(self, output, **kwargs):
        self.steps.append(f"Tool output: {output}")
        print("### on_tool_end ###")
        print(f"{output=}")
        print("###################\n")

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when tool errors."""
        print("### on_tool_error ###")
        print(f"{error=}")
        print("#####################\n")


class Agent:

    def __init__(self, message: str) -> None:
        self.message: str = message
        self.ws_recv_queue = queue.Queue()

    def set_ws_connection(self, ws: WebSocket):
        self.ws_con = ws

    def invoke(self):

        customHandler = CustomHandler()

        tools = [
            ShellTool(self.ws_con, self.ws_recv_queue, callbacks=[customHandler]),
            DuckDuckGoSearchRun(callbacks=[customHandler]),
            # FileCreationTool()
        ]

        template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question. 

Remember, always use the exact format provided above. Do not deviate from it.

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

        # prompt = ChatPromptTemplate.from_template(template)
        # prompt = hub.pull("hwchase17/react")
        prompt = PromptTemplate.from_template(template)

        # chain = prompt | AI.pipe
        agent = create_react_agent(ModelClass.llm, tools, prompt)

        agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=True, callbacks=[customHandler])

        customHandler.steps = []
        res = agent_executor.invoke({"input": self.message})
        return AgentResponse(agent=res, steps=customHandler.steps)

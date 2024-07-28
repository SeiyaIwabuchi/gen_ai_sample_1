import asyncio
from typing import Any, AsyncIterable, Dict, List
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks.base import BaseCallbackHandler
from pydantic import BaseModel

# from gemma import Gemma
from gpt_4o_mini import Gpt4oMini as ModelClass
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

    def on_tool_end(self, output, **kwargs):
        self.steps.append(f"Tool output: {output}")

class Agent:
    search = DuckDuckGoSearchRun()
    tools = [
        ShellTool(),
        Tool(
            name="Search",
            func=search.run,
            description="useful for when you need to answer questions about current events"
        ),
        FileCreationTool()
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
Final Answer: the final answer to the original input question. Only the final answer is displayed to the user. Please answer all questions without omitting specific methods. Also, please write in markdown.

Remember, always use the exact format provided above. Do not deviate from it.
Be sure to answer in Japanese.

Begin!

Question: {input}
Thought: {agent_scratchpad}"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # chain = prompt | AI.pipe
    agent = create_react_agent(ModelClass.llm, tools, prompt)

    customHandler = CustomHandler()

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, callbacks=[customHandler])

    @classmethod
    def invoke(cls, input: str):
        cls.customHandler.steps = []
        res = cls.agent_executor.invoke({"input" : input})
        return AgentResponse(agent=res, steps=cls.customHandler.steps)
    
    @classmethod
    async def invokeStreaming(cls, input: str):
        cls.customHandler.steps = []

        async for token in ModelClass.asyncIteratorCallbackHandler.aiter():
            print(token)
            yield AgentResponse(agent={"output": token}, steps=cls.customHandler.steps)
    
        cls.agent_executor.invoke({"input" : input})
    
import asyncio
import duckduckgo_search
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import httpx
import openai
from pydantic import BaseModel
import uvicorn
from agent import AgentResponse
from fastapi.middleware.cors import CORSMiddleware
import traceback

from agent_manager import AgentManager
from chat import Chat
from constans.errors import Errors


app = FastAPI()

# 許可するオリジンのリスト
origins = [
    "*"
]

# CORSMiddlewareを追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 許可するオリジン
    allow_credentials=True,  # クレデンシャル（認証情報）を許可
    allow_methods=["*"],  # 許可するHTTPメソッド（例: GET, POSTなど）
    allow_headers=["*"],  # 許可するHTTPヘッダー
)

agentManager = AgentManager()

class Question(BaseModel):
    client_id: str
    message: str

class Answer(BaseModel):
    answer: str

# サバクラ対応

@app.get("/agent")
def post_agent(platform: str = "unix"):
    # res = Agent.invoke(input=question.question)
    # print(res)
    # return Answer(answer=res.agent['output'])

    client_id = agentManager.create(platform)
    return { "client_id" : client_id }

@app.get("/is_alive_thread/{client_id}")
def is_alive_thread(client_id: str):
    return {"result": client_id in agentManager.agent_instance_pool}

async def close_loop(websocket: WebSocket, agentManager: AgentManager, client_id: str):
    while client_id in agentManager.agent_instance_pool:
        await asyncio.sleep(1)
    try:
        await websocket.close()
    except:
        pass


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    agent = agentManager.get_agent_instance(client_id)
    agent.set_ws_connection(websocket)

    asyncio.create_task(close_loop(websocket, agentManager, client_id))

    while True:
        try:
            agent.ws_recv_queue.put(await websocket.receive_json())
        except:
            break



@app.post("/wait_for_agent_task")
def wait_for_agent_task(question: Question):
    agent = agentManager.get_agent_instance(question.client_id)
    try:
        res: AgentResponse = agent.invoke(question.message)
        return Answer(answer=res.agent['output'])
    except openai.APIConnectionError:
        traceback.print_exc()
        return JSONResponse({
            "name": Errors.OpenaiAPIConnectionError.name,
            "code": Errors.OpenaiAPIConnectionError.value
            }, 504)
    except httpx.ReadTimeout:
        traceback.print_exc()
        return JSONResponse({
            "name": Errors.HttpxReadTimeout.name,
            "code": Errors.HttpxReadTimeout.value
            }, 504)
    except duckduckgo_search.exceptions.TimeoutException:
        traceback.print_exc()
        return JSONResponse({
            "name": Errors.HttpxReadTimeout.name,
            "code": Errors.HttpxReadTimeout.value
            }, 504)
    finally:
        # agentManager.remove(question.client_id)
        pass


@app.post("/chat")
def simple_chat(question: Question):
    return Answer(answer=Chat.invoke(question.message).agent["output"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
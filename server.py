import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import uvicorn
from agent import AgentResponse
from fastapi.middleware.cors import CORSMiddleware
import traceback

from agent_manager import AgentManager
from chat import Chat


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
    message: str

class Answer(BaseModel):
    answer: str

# サバクラ対応

@app.post("/agent")
def post_agent(question: Question):
    # res = Agent.invoke(input=question.question)
    # print(res)
    # return Answer(answer=res.agent['output'])

    client_id = agentManager.create(question.message)
    return { "client_id" : client_id }


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



@app.get("/wait_for_agent_task/{client_id}")
def wait_for_agent_task(client_id: str):
    agent = agentManager.get_agent_instance(client_id)
    try:
        res: AgentResponse = agent.invoke()
        return Answer(answer=res.agent['output'])
    except:
        return Answer(answer=traceback.format_exc())
    finally:
        agentManager.remove(client_id)


@app.post("/chat")
def simple_chat(question: Question):
    return Answer(answer=Chat.invoke(question.message).agent["output"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
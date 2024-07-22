from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from agent import Agent
from fastapi.middleware.cors import CORSMiddleware

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

class Question(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str

@app.post("/answer")    
def read_item(question: Question):
    res = Agent.invoke(input=question.question)
    print(res)
    return Answer(answer=res.agent['output'])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
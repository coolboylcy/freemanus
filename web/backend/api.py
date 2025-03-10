from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from typing import Optional

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

class PromptResponse(BaseModel):
    response: str

@app.post("/api/chat", response_model=PromptResponse)
async def chat(request: PromptRequest):
    try:
        # 这里我们简化了响应，实际项目中你可以集成你的 AI 模型
        response = f"Received your message: {request.prompt}"
        return PromptResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "ok"} 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import sys
import os
import traceback
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.agent.manus import Manus

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建 Manus 代理实例
try:
    agent = Manus()
    logger.info("Manus agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Manus agent: {str(e)}")
    logger.error(traceback.format_exc())
    raise

class PromptRequest(BaseModel):
    prompt: str

class PromptResponse(BaseModel):
    response: str
    status: str

@app.post("/api/chat", response_model=PromptResponse)
async def chat(request: PromptRequest):
    try:
        logger.info(f"Received chat request with prompt: {request.prompt}")
        
        # 创建一个队列来存储响应
        response_queue = asyncio.Queue()
        
        # 创建一个回调函数来收集响应
        async def collect_response(response):
            logger.debug(f"Received response: {response}")
            await response_queue.put(response)
        
        # 运行代理并收集响应
        logger.info("Starting agent.run")
        await agent.run(request.prompt, callback=collect_response)
        
        # 获取所有响应
        responses = []
        while not response_queue.empty():
            response = await response_queue.get()
            responses.append(response)
        
        logger.info(f"Completed chat request with {len(responses)} responses")
        return PromptResponse(
            response="\n".join(responses),
            status="success"
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"} 
from fastapi import FastAPI, Request
from agent import bumatalk
import httpx
import asyncio
app = FastAPI()
@app.get("/")
async def root():
    return ""

@app.post("/bumatalk")
async def reply(request: Request):
    try:
        content = await request.json()
        req = content["userRequest"]["utterance"]
        callback_url = content["userRequest"]["callbackUrl"]
    except KeyError as e:
        print(f"요청 데이터 오류: {e}")
        return {"error": f"Invalid request data: {str(e)}"}
    callbackResponse = {
        "version": "2.0",
        "useCallback": True,
        "data": {
            "text": "생각 중입니다! 잠시만 기다려 주세요.\n1분 이내에 답변 드리겠습니다!"
        }
    }

    async def sendResponse():
        try:
            res = bumatalk(req)
            responseBody = create_response_body(res)
            async with httpx.AsyncClient() as client:
                await client.post(callback_url, json=responseBody)
        except Exception as e:
            print(f"error : {e}")
            responseBody = create_response_body("다시 시도해주세요 🙏")
            async with httpx.AsyncClient() as client:
                await client.post(callback_url, json=responseBody)
    asyncio.create_task(sendResponse())
    return callbackResponse

def create_response_body(res):
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": res
                    }
                }
            ]
        }
    }
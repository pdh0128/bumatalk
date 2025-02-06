from fastapi import FastAPI, Request
from agent import bumatalk
import httpx
import asyncio
from tools import initUser, getUser
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
        userid = content["userRequest"]["user"]["id"]
    except KeyError as e:
        print(f"요청 데이터 오류: {e}")
        return {"error": f"Invalid request data"}
    callbackResponse = {
        "version": "2.0",
        "useCallback": True,
        "data": {
            "text": "생각 중입니다! 잠시만 기다려 주세요.\n1분 이내에 답변 드리겠습니다!"
        }
    }

    async def sendResponse():
        try:
            res = await asyncio.gather(bumatalk(req, userid))
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

@app.post("/init")
async def init(request: Request):
    try:
        content = await request.json()
        userid = content["userRequest"]["user"]["id"]
        flag = initUser(userid)
        if flag == 200:
            res = "초기화 되었습니다! 🚀"
        elif flag == 201:
            res = "이미 대화 내역이 존재하지 않습니다 😥"
        else:
            res = "실패했습니다. 😭"
        responseBody = create_response_body(res)
        return responseBody
    except Exception as e:
        print(f"error : {e}")
        return create_response_body("실패했습니다. 다시 시도해주세요 🙏")

@app.post("/getUserInfo")
async def getUserInfo(request: Request):
    try:
        content = await request.json()
        userid = content["userRequest"]["user"]["id"]
        user = getUser(userid)
        responseBody = create_response_body(user)
        return responseBody
    except Exception as e:
        print(f"error : {e}")
        return create_response_body("실패했습니다. 다시 시도해주세요 🙏")
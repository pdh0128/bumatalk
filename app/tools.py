import asyncio

import httpx
from dotenv import load_dotenv
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
import os
from pinecone import Pinecone
from pip._internal import req

from mongo import Mongo
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
import requests
from datetime import datetime, date
from langchain_community.chat_models import ChatPerplexity
from langchain_core.prompts import ChatPromptTemplate

from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from output_parser import *
import json
from upstash_redis import Redis

set_llm_cache(InMemoryCache())

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
embedder = OpenAIEmbeddings()
vector_store = PineconeVectorStore(index_name=os.getenv("PINECONE_INDEX"), embedding=embedder)
pinecone_index = pc.Index(os.getenv("PINECONE_INDEX"))
db = Mongo()
redis_url = os.getenv("REDIS_URL")
redis_token = os.getenv("REDIS_TOKEN")
redis = Redis(url=redis_url, token=redis_token)

def checkNone(res):
    if res is None:
        return {"output": " ❌ 검색 실패 ❌"}
    return res
async def student(req):
    """학생 정보를 처리합니다."""
    temp = """
        너는 부산소프트웨어마이스터고의 학생 {name}에 대해 잘 알고 있는 전문가야.
        주어진 질문에 대해 학생 {name}의 정보를 바탕으로 답변해. 
        학생 {name}에 대한 정보: {Info}
        질문: {Question}
    """
    prompt = PromptTemplate(input_variables=["name", "Info" ,"Question"], template=temp)
    query_vecter = embedder.embed_query(req)
    results = pinecone_index.query(vector=query_vecter, top_k=1, include_metadata=True)
    student_url = results['matches'][0]['id']
    student = await db.getStudent(student_url)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = prompt | llm | StrOutputParser()
    res = chain.invoke(input={"name" : student['name'], "Info" : student["text"], "Question" : req})
    print(res)
    return res

async def teacher(req):
    """선생님의 정보를 처리합니다."""
    temp = """
        너는 부산소프트웨어마이스터고의 선생님 {name}에 대해 잘 알고 있는 전문가야.
        주어진 질문에 대해 선생님 {name}의 정보를 바탕으로 답변해. 
        선생님 {name}에 대한 정보: {Info}
        질문: {Question}
    """
    prompt = PromptTemplate(input_variables=["name", "Info" ,"Question"], template=temp)
    query_vecter = embedder.embed_query(req)
    results = pinecone_index.query(vector=query_vecter, top_k=1, include_metadata=True)
    teacher_url = results['matches'][0]['id']
    teacher = await db.getTeacher(teacher_url)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = prompt | llm | StrOutputParser()
    res = chain.invoke(input={"name" : teacher['name'], "Info" : teacher["text"], "Question" : req})
    print(res)
    return res

async def bssm(req):
    """사용 가능한 도구가 없거나 적합한 도구를 찾지 못했을 때 제공되는 기본 응답입니다."""
    temp = """
        너는 부산소프트웨어마이스터고등학교에 대한 전문가야.
        사용자가 묻는 모든 질문에 대해 정확하고 친절하며, 필요한 경우 상세한 정보를 제공해줘.
        답변은 간결하면서도 이해하기 쉽게 작성해야 해.
        질문: {Question}
        답변:
        """
    llm = ChatPerplexity(
        temperature=0, model="sonar"
    )
    prompt = PromptTemplate(input_variables=["Question"], template=temp)
    chain = prompt | llm | StrOutputParser()
    res = chain.invoke(input={"Question" : req})
    print(res)
    return res
def iDontKnow(req):
    return {"output": "잘 모르겠습니다.\n저는 부소마고의 정보를 알리는 부마톡입니다.\n다시 한번 말씀해주실 수 있을까요? 🙏"}

def howToUse(req):
    """부마톡 방법을 반환합니다."""
    return {
        "output" : """
    📢 부마톡 이용 안내 📢
    안녕하세요!
    부산소프트웨어마이스터고등학교 정보를 제공하는 부마톡입니다. 😊
    
    부마톡을 원활하게 이용하려면 아래 규칙을 지켜주세요!
    
    1️⃣ 질문을 명확하게 해주세요.
    예시:
    ❌ "마루가 뭐야?"
    ✅ "교내 서비스 마루가 뭐야?"
    2️⃣ 답변이 오기 전에 추가 질문을 하지 마세요.
    새로운 질문을 하면 대화가 꼬일 수 있어요!
    만약 꼬였다고 생각되면 2~5분 정도 기다리면 자동으로 정상 복구됩니다.
    📌 급식 정보를 보려면 질문에 날짜를 포함해야 해요!
    📌 시간표 정보를 보려면 학년, 반, 날짜를 포함해야 해요!
    
    이제 부마톡과 함께 부산소프트웨어마이스터고에 대해 알아보세요! 🚀"""
}


async def summary(name, text):
    text = text.strip()
    if text == "" or text is None:
        return "문서가 비어있습니다."
    temp = """
    다음 문장의 내용은 {name}에 대한 내용입니다.
    다음 문장의 내용을 30문장 이내로 요약해 주세요.
    각 문장이 서로 자연스럽게 연결되도록 하고, 간결하고 명확하게 글의 요지를 잘 드러낼 수 있도록 작성해 주세요.
    문장: {sentence}
    요약:
    """
    prompt = PromptTemplate(input_variables=["name" ,"sentence"], template=temp)
    llm = ChatOpenAI(temperature=0)
    chain = prompt | llm | StrOutputParser()
    res = chain.invoke(input={"name" : name, "sentence": text})
    return res

async def schoolFood(req):
    """학교 급식 정보를 처리합니다."""
    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        "ATPT_OFCDC_SC_CODE": "C10",
        "SD_SCHUL_CODE": "7150658",
        "KEY": os.getenv("SCHOOLD_OPENAPI_API_KEY"),
        "Type" : "json",
        "MLSV_YMD": req
    }
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.get(url, params=params)
        if res.status_code == 200:
            data = res.json()
            meals = food_parsing(data)
            print(meals)
            return meals
        else:
            print(f"요청 실패! 상태 코드: {res.status_code}")
            print(res.text)
            return None

def food_parsing(data):
    meals = {"조식": None, "중식": None, "석식": None}
    if "mealServiceDietInfo" in data:
        rows = data["mealServiceDietInfo"][1]["row"]
    else:
        return meals

    for meal in rows:
        meal_name = meal["MMEAL_SC_NM"]
        meals[meal_name] = {
            "날짜": meal["MLSV_YMD"],
            "메뉴": meal["DDISH_NM"].replace("<br/>", "\n"),
            "칼로리 정보": meal["CAL_INFO"],
            "영양 정보": meal["NTR_INFO"].replace("<br/>", "\n")
        }
    return meals



async def schoolTime(req):
    """학교 시간표 정보를 처리합니다."""
    url = "https://open.neis.go.kr/hub/hisTimetable"
    data_dict = schoolTimeOuputParser.parse(req).to_dict()
    date = data_dict["date"]
    grade = data_dict["grade"]
    group = data_dict["classroom"]
    params = {
        "ATPT_OFCDC_SC_CODE": "C10",
        "SD_SCHUL_CODE": "7150658",
        "KEY": os.getenv("SCHOOLD_OPENAPI_API_KEY"),
        "Type": "json",
        "ALL_TI_YMD": date,
        "GRADE" : grade,
        "CLASS_NM" : group
    }

    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.get(url, params=params)
        if res.status_code == 200:
            data = res.json()
            time = parse_timetable(data)
            return time
        else:
            print(f"요청 실패! 상태 코드: {res.status_code}")
            print(res.text)
            return "요청 실패"
def parse_timetable(data):
    timetable = {}
    if "hisTimetable" in data:
        rows = data["hisTimetable"][1]["row"]
        for entry in rows:
            period = entry.get("PERIO", "")
            subject = entry.get("ITRT_CNTNT", "")
            timetable.update({period + "교시" : subject})
    return timetable

async def maister(req="마역량에 대해 설명하고 마역량이 높으면 좋은점에 대해 말해주세요."):
    """마역량 관련 정보를 처리합니다."""
    prompts = """
    역할:
    당신은 마이스터 역량 인증 제도의 전문가입니다. 마이스터 역량(이하 “마역량”)에 대해 깊이 이해하고 있으며, 관련 질문에 전문적이고 정확한 답변을 제공합니다.
    배경 정보:
	•	마역량은 2학년 학과 배정 시 시험 점수와 함께 반영됩니다.
	•	마역량 점수가 높으면 해외 프로그램 지원(학교에서 마역량 우수자를 선발하여 해외로 파견) 및 학과 선택 등 다양한 혜택이 주어집니다.
	•	아래 제공된 정보는 마역량을 얻을 수 있는 기준입니다.
    정보:
    {context}
    지침:
	1.	반드시 위의 정보를 기반으로만 답변하세요.
	2.	답변은 명확하고 간결하게 작성하세요.
	3.	추가 설명이 필요하다면 관련 내용을 체계적으로 정리하여 제공하세요.
	4.	질문과 관련 없는 추가적인 정보는 포함하지 마세요.
	
    질문: {Question}
    응답 :
"""
    prompt = PromptTemplate.from_template(prompts)
    embedder = OpenAIEmbeddings()
    vector_store = PineconeVectorStore(index_name=os.getenv("PINECONE_PDF_INDEX"), embedding=embedder)
    llm = ChatOpenAI(model="gpt-4o-mini")
    chain = {"context": vector_store.as_retriever() | format_docs, "Question": RunnablePassthrough()
             } | prompt | llm
    res = chain.invoke(req).content
    print(res)
    return res

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

async def schoolSchedule (req):
    """학교 학사일정 정보 처리합니다."""
    data_dict = schoolScheduleOutputParser.parse(req).to_dict()
    url = "https://open.neis.go.kr/hub/SchoolSchedule"
    first_date = datetime.strptime(data_dict["first_date"], "%Y%m%d")
    last_date = datetime.strptime(data_dict["last_date"], "%Y%m%d")

    first_month = first_date.month - 1
    if first_month == 0:
        first_date = first_date.replace(year=first_date.year - 1, month=12)
    else:
        first_date = first_date.replace(month=first_month)

    last_month = last_date.month + 1
    if last_month == 13:
        last_date = last_date.replace(year=last_date.year + 1, month=1)
    else:
        last_date = last_date.replace(month=last_month)

    first = first_date.strftime("%Y%m%d")
    last = last_date.strftime("%Y%m%d")

    print(first, last)
    params = {
        "ATPT_OFCDC_SC_CODE": "C10",
        "SD_SCHUL_CODE": "7150658",
        "KEY": os.getenv("SCHOOLD_OPENAPI_API_KEY"),
        "Type": "json",
        "AA_FROM_YMD": first,
        "AA_TO_YMD": last,
        "pSize" : 1000
    }
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.get(url, params=params)
        if res.status_code == 200:
            data = res.json()
            event = parse_school_schedule(data)
            print(event)
            return event
        else:
            print(f"요청 실패! 상태 코드: {res.status_code}")
            print(res.text)
            return "요청 실패"

def parse_school_schedule(data):
    if "SchoolSchedule" not in data:
        return {}
    events = data["SchoolSchedule"][1]["row"]
    parsed_events = []

    for event in events:
        date = event["AA_YMD"]
        event_name = event["EVENT_NM"]
        event_type = event["SBTR_DD_SC_NM"]
        grades = []
        if event["ONE_GRADE_EVENT_YN"] == "Y":
            grades.append("1학년")
        if event["TW_GRADE_EVENT_YN"] == "Y":
            grades.append("2학년")
        if event["THREE_GRADE_EVENT_YN"] == "Y":
            grades.append("3학년")

        parsed_events.append({
            "날짜": date,
            "이벤트 이름": event_name,
            "이벤트 유형": event_type,
            "대상 학년": ", ".join(grades)
        })
    return parsed_events


async def extract_user_info(req):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    year = datetime.now().strftime("%H")
    temp = """
    사용자의 정보를 문장에서 추출하여 JSON 형식으로 반환하세요.  
    
    응답 형식 :
    {format_instructions}
    
    MongoDB의 동적 스키마를 활용하므로, **정해진 데이터 구조가 없으며** 문장에서 추출 가능한 모든 정보를 유연하게 포함할 수 있습니다.
    올해는 {year}입니다.
      
    📌 **규칙**  
    1. 문장에서 **추론 가능한 정보는 모두 포함**하세요.  
        - 예: 이름, 나이, 학년, 성적, 관심사 등등   
    2. 문장에서 명확히 추출할 수 없는 정보는 포함하지 않습니다.  
    3. 문장에서 정보를 전혀 추출할 수 없는 경우, 빈 JSON 객체 {{}}를 반환하세요.  
    
    🎯 **입력 예시**  
    문장: "나는 중학교 3학년이고 성적이 낮은 편인데 부소마고에 입학할 수 있을까?"  
    📝 **출력 예시**  
    {{"나이": “16”,“학년”: “중학교 3학년”,“성적”: “낮은 편”}}

    🎯 **입력 예시**  
    문장: "저는 소프트웨어 개발에 관심이 많아요!"  
    📝 **출력 예시**  
    {{"관심사”: “소프트웨어 개발"}}
    
    📌 **추가 규칙**  
    - 반환되는 JSON 객체는 MongoDB에서 바로 저장할 수 있는 형식이어야 합니다.  
    - 중첩된 데이터가 필요한 경우, 중첩된 JSON 객체로 표현하세요.  
    
    문장 : {sentense}
    응답 : 
"""
    parser = JsonOutputParser()
    prompt = PromptTemplate(input_variables=["year", "sentense"], template=temp, partial_variables={"format_instructions": parser.get_format_instructions()})
    chain = prompt | llm | parser
    res = chain.invoke(input={"year" : year, "sentense" : req})
    return res

async def initUser(userid):
    try:
        await db.deleteUser(userid)
        result = redis.delete("message_store:" + userid)
        if result:
            return 200
        else:
            return 201
    except Exception as e:
        print(f"error: {e}")
        return 400

async def getUser(userid):
    user = await db.getUser(userid)
    print(user)
    if not user or user == "사용자 정보가 없습니다.":
        return "사용자 정보가 없습니다."
    userInfo = "\n".join([f"{key} : {value}" for key, value in user.items()])
    print(userInfo)
    return userInfo
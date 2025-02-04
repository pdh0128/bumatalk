from dotenv import load_dotenv
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
import os
from pinecone import Pinecone
from mongo import Mongo
from langchain_core.output_parsers import StrOutputParser
import requests
from datetime import datetime
from langchain_community.chat_models import ChatPerplexity
from langchain_core.prompts import ChatPromptTemplate

from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache

from output_parser import schoolTimeOuputParser

set_llm_cache(InMemoryCache())

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
embedder = OpenAIEmbeddings()
vector_store = PineconeVectorStore(index_name=os.getenv("PINECONE_INDEX"), embedding=embedder)
pinecone_index = pc.Index(os.getenv("PINECONE_INDEX"))
db = Mongo()
def checkNone(res):
    if res is None:
        return {"output": " ❌ 검색 실패 ❌"}
    return res
def student(req):
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
    student = db.getStudent(student_url)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = prompt | llm | StrOutputParser()
    res = chain.invoke(input={"name" : student['name'], "Info" : student["text"], "Question" : req})
    print(res)
    return res

def teacher(req):
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
    teacher = db.getTeacher(teacher_url)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = prompt | llm | StrOutputParser()
    res = chain.invoke(input={"name" : teacher['name'], "Info" : teacher["text"], "Question" : req})
    print(res)
    return res

def bssm(req):
    temp = """
        너는 부산소프트웨어마이스터고등학교에 대한 전문가야.
        사용자가 묻는 모든 질문에 대해 정확하고 친절하며, 필요한 경우 상세한 정보를 제공해줘.
        답변은 간결하면서도 이해하기 쉽게 작성해야 해.
        질문: {Question}
        답변:
        """
    llm = ChatPerplexity(
        temperature=0, model="sonar-pro"
    )
    prompt = PromptTemplate(input_variables=["Question"], template=temp)
    chain = prompt | llm | StrOutputParser()
    res = chain.invoke(input={"Question" : req})
    print(res)
    return res

def iDontKnow(req):
    return {"output": "잘 모르겠습니다.\n저는 부소마고의 정보를 알리는 부마톡입니다.\n다시 한번 말씀해주실 수 있을까요? 🙏"}

def howToUse(req):
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


def summary(name, text):
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


def schoolFood(req):
    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        "ATPT_OFCDC_SC_CODE": "C10",
        "SD_SCHUL_CODE": "7150658",
        "KEY": os.getenv("SCHOOLD_OPENAPI_API_KEY"),
        "Type" : "json",
        "MLSV_YMD": req
    }
    res = requests.get(url, params=params)
    if res.status_code == 200:
        # print(res.json())
        data = res.json()
        meals = food_parsing(data)
        print(meals)
        return meals
    else:
        print(f"요청 실패! 상태 코드: {res.status_code}")
        print(res.text)

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



def schoolTime(req):
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
    res = requests.get(url, params=params)
    if res.status_code == 200:
        # print(res.json())
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

def maister(req="마역량에 대해 설명하고 마역량이 높으면 좋은점에 대해 말해주세요."):
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
    vector_store = PineconeVectorStore(index_name=os.getenv("PINECONE_pdf_INDEX"), embedding=embedder)
    llm = ChatOpenAI(model="gpt-4o-mini")
    chain = {"context": vector_store.as_retriever() | format_docs, "Question": RunnablePassthrough()
             } | prompt | llm
    res = chain.invoke(req).content
    print(res)
    return res

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

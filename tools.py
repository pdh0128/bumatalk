from dotenv import load_dotenv
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
    # today = "20240627"
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
if __name__ == "__main__":
    schoolFood(None)
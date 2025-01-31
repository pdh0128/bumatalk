from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_pinecone import PineconeVectorStore
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
import os
from pinecone import Pinecone
from mongo import Mongo
from langchain_core.output_parsers import StrOutputParser
load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
embedder = OpenAIEmbeddings()
vector_store = PineconeVectorStore(index_name=os.getenv("PINECONE_INDEX"), embedding=embedder)
pinecone_index = pc.Index(os.getenv("PINECONE_INDEX"))
db = Mongo()
def student(req):
    temp = """
        너는 부산소프트웨어마이스터고의 학생 {name}에 대해 잘 알고 있는 전문가야.
        주어진 질문에 대해 학생 {name}의 정보만 바탕으로 답변해. 
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
    res = "부마위키에 따르면.. \n" + chain.invoke(input={"name" : student['name'], "Info" : student["text"], "Question" : req})
    print(res)
    return res
student(req="서정현에 대해 알려줘")

async def bumatalk(req):
    temp = """
    너는 '부마톡'이라는 챗봇이야.  
    부산소프트웨어마이스터고의 정보를 정확하고 신뢰성 있게 제공하는 역할을 해.  
    - 네가 가진 데이터베이스와 검색된 자료를 활용해서 답변해.  
    - 출처가 있는 정보만 제공하고, 모르면 모른다고 말해.  
    - 간단한 질문은 짧게, 복잡한 질문은 상세하게 설명해.  
    질문: {question}  
    답변:  
    """
    prompt = PromptTemplate(input_variables=["question"], template=temp)
    llm = ChatOpenAI(temperature=0)
    chain = prompt | llm
    res = chain.invoke(input={"question" : req}).content
    print(res)
    return {"message" : res}

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
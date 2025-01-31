from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
async def branch(req):
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
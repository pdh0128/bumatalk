from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain.tools import Tool
from tools import *
load_dotenv()

tools_from_agent = [
        Tool(
            name="학생 정보 토대 답변",
            func=student,
            description="부산소프트웨어마이스터고 학생에 관한 질문에 대한 정보를 제공하는 도구"
        ),
        Tool(
            name="선생님 정보 토대 답변",
            func=teacher,
            description="부산소프트웨어마이스터고 선생님에 관한 질문에 대한 정보를 제공하는 도구"
        ),
        Tool(
            name="학교에 관한 정보 답변",
            func= bssm,
            description="부산소프트웨어마이스터고에 대한 정보를 제공하는 도구"
        )
    ]

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
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    react_prompt = hub.pull("hwchase17/react")
    react_agent = create_react_agent(prompt=react_prompt, llm=llm, tools=tools_from_agent)
    agent_axecutor = AgentExecutor(agent=react_agent, tools=tools_from_agent, verbose=True)
    res = agent_axecutor.invoke({"input" : prompt.format_prompt(question=req)})
    print(res["output"])
    return {"message" : res["output"]}


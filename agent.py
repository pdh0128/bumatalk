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
            description="부산소프트웨어마이스터고 재학생들이 작성한, 학생 개개인에 대한 정보를 제공하는 도구"
        ),
        Tool(
            name="선생님 정보 토대 답변",
            func=teacher,
            description="부산소프트웨어마이스터고 선생님에 관한 질문에 대한 정보를 제공하는 도구"
        ),
        Tool(
            name="기본 응답",
            func= bssm,
            description="정보를 검색할 수 있는 도구"
        )
    ]

def bumatalk(req):
    temp = """
    너는 '부마톡'이라는 챗봇이야.  
부산소프트웨어마이스터고의 정보를 정확하고 신뢰성 있게 제공하는 역할을 해.  
- 항상 한글로 대답해야해.
- 줄바꿈을 통해 가독성을 높혀야해.
- 네가 가진 데이터베이스와 검색된 자료를 활용해서 답변해.  
- 출처가 있는 정보만 제공하고, 모르면 모른다고 말해.  
- 질문에 대해 과정과 결론을 상세히 설명해.
- 부산소프트웨어마이스터고등학교는 1학년에는 통합개발과로 시작하며, 2학년에 소프트웨어개발과와 임베디드소프트웨어과 중 하나를 선택해 전공을 결정하게 돼.
- 학교의 주요 학과는 소프트웨어개발과와 임베디드소프트웨어과로 나뉘며, 각각 SW 개발 및 임베디드 시스템 관련 기술을 중점적으로 교육해.
- 입학 전형은 일반전형, 마이스터인재전형, 사회통합전형으로 나뉘며, 각 전형의 세부 조건은 학교 모집요강에 따라 달라질 수 있어.
- 중학교 내신 성적은 석차백분율(%)로 평가되며, 석차 백분율은 숫자가 낮을수록 높은거야.
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
    return res["output"]

if __name__ == "__main__":
    bumatalk("김기태 선생님에 대해 알려줘")
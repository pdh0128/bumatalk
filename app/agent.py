import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import create_react_agent, AgentExecutor, initialize_agent
from langchain import hub
from langchain.tools import Tool
from tools import *
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import UpstashRedisChatMessageHistory


set_llm_cache(InMemoryCache())
load_dotenv()

tools_from_agent = [
        Tool(
            name="학생 정보 토대 답변",
            func=student,
            description="부산소프트웨어마이스터고 재학생들이 작성한, 학생 한 개인에 대한 정보를 제공하는 도구야. 특정 개인만의 정보를 참조할 수 있어."
        ),
        Tool(
            name="선생님 정보 토대 답변",
            func=teacher,
            description="부산소프트웨어마이스터고 재학생들이 작성한, 선생님 한 개인에 대한 정보를 제공하는 도구야. 특정 개인만의 정보를 참조할 수 있어."
        ),
        Tool(
                name="마이스터 역량 점수 정보 도구",
                func=maister,
                description=(
                    "마이스터 역량(마역량)에 대한 정보를 제공하는 도구입니다. "
                    "마역량 점수의 기준, 활용 방법, 혜택 등을 알 수 있습니다."
        )),
        Tool(
            name="기본 응답",
            func= bssm,
            description="정보를 검색할 수 있는 도구"
        ),
        Tool(
            name="학교 급식 정보",
            func = schoolFood,
            description="20240627과 같은 형식의 날짜를 입력하면 해당 날짜의 급식 정보를 확인할 수 있습니다."
        ),
        Tool(
            name="학교 시간표 정보",
            func=schoolTime,
            description='{"grade" : "1", "classroom" : "3", "date" : "20240618"} 과 같은 형식의 학년, 반, 날짜를 입력하면 시간표 정보를 확인할 수 있습니다.'
        ),
        Tool(
            name="관련이 없는 주제일 때 사용할 수 있는 도구",
            func=iDontKnow,
            description="관련이 없는 주제일 때 사용할 수 있는 도구야. 항상 마지막에 고려해야해"
        ),
    Tool(
        name="부마톡의 규칙을 설명해주는 도구",
        func=howToUse,
        description="부마톡의 규칙(사용법)을 설명해주는 도구"
    ),
    ]

def bumatalk(req, userid):
    history = UpstashRedisChatMessageHistory(
        session_id=userid,
        url=os.getenv("REDIS_URL"),
        token=os.getenv("REDIS_TOKEN"),
    )
    memory = ConversationBufferMemory(
        return_messages=True,
        chat_memory=history,
    )

    temp = """
    너는 '부마톡'이라는 챗봇이야.  
    부산소프트웨어마이스터고의 정보를 **정확하고 신뢰성 있게** 제공하는 역할을 해.  
    오늘 날짜는 {today}이야.
    
    📌 **답변 규칙**     
    1. **항상 한글로 대답**해야 해.  
    2. **줄바꿈을 활용해 가독성을 높여야** 해.  
    3. **네가 가진 데이터베이스와 검색된 자료를 활용해 답변해.**  
    
    📚 **학교 정보**  
    - 부산소프트웨어마이스터고는 1학년에는 통합개발과로 시작하며,  
      2학년부터 소프트웨어개발과와 임베디드소프트웨어과 중 하나를 선택해 전공을 결정해.  
    - 주요 학과는 소프트웨어개발과와 임베디드소프트웨어과로 나뉘며,  
      각각 SW 개발 및 임베디드 시스템 관련 기술을 중점적으로 교육해.  
    - 입학 전형은 일반전형, 마이스터인재전형, 사회통합전형으로 나뉘며,  
      각 전형의 세부 조건은 학교 모집요강에 따라 달라질 수 있어.  
    - 중학교 내신 성적은 석차백분율(%)로 평가되며,  
      석차 백분율이 낮을수록 성적이 높은 거야.  

    🎯 질문: {question}  
    📝 답변: 
    """
    prompt = PromptTemplate(input_variables=["today", "question"], template=temp)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    react_prompt = hub.pull("hwchase17/react")
    react_agent = create_react_agent(prompt=react_prompt, llm=llm, tools=tools_from_agent)
    agent_axecutor = AgentExecutor(agent=react_agent, tools=tools_from_agent, verbose=True, handle_parsing_errors=True, max_iterations=5, memory=memory)
    today = datetime.now().strftime("%Y%m%d")
    res = agent_axecutor.invoke({"input" : prompt.format_prompt(today=today,question=req).to_string()})
    print(res["output"])
    if res["output"] == "Agent stopped due to iteration limit or time limit.":
        return "제가 더 이해하기 쉽도록 말씀해주실 수 있을까요? 😅"
    return res["output"]

if __name__ == "__main__":
    tic = datetime.now()
    bumatalk("2024년 3월 30일 급식 알려줘", "-1")
    print(datetime.now() - tic)

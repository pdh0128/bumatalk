# 부마톡
> 부마톡은 부산소프트웨어마이스터고등학교의 정보를 쉽고 빠르게 확인할 수 있는 카카오톡 챗봇 서비스입니다.

![바부마톡](https://github.com/user-attachments/assets/c4d4a4c0-b17e-40c3-8d86-d296a1cae5d1)

  처음 이 학교를 알게 됐을 때, 제대로 된 정보를 찾기가 어려웠습니다.
공식 사이트에는 필요한 정보가 정리돼 있지 않았고, 블로그나 커뮤니티에도 양질의 경험담은 찾기 힘들었습니다.
그래서 어떤 학교인지, 제가 지원할 만한 곳인지 판단하는 데 시간이 오래 걸렸습니다.

  결국은 제가 직접 경험하면서 판단할 수밖에 없었고, 그 과정을 겪고 나서야 이 학교가 어떤 곳인지 확실히 이해할 수 있었습니다.
이 서비스는 저처럼 고민하는 누군가를 위해 만들었습니다.
![부마톡아키텍쳐)](https://github.com/user-attachments/assets/010f9b61-9f45-4de3-8419-a91d0a0add36)

---

### 주요 기여 및 역할

### ॅ 백엔드 개발

### **FastAPI 기반 서버**

- 비동기 처리를 바탕으로 LangChain 기반 AI 기능을 효율적으로 제공.
- 클라이언트와의 API 통신을 위한 경량화된 REST 엔드포인트 구현.

**LangChain 기반 AI Agent**

- PromptTemplate, LLMChain, Memory 등을 활용해 사용자 맥락에 맞는 자연스러운 응답을 생성.
- PyPDFLoader를 활용하여 PDF 문서를 로드한 후, Retrieval-Augmented Generation(RAG) 기반 시스템을 구현하였습니다.

**OpenAI GPT 모델 연동**

- GPT-4 API를 기반으로 사용자 감정 기록에 대한 피드백 및 요약 제공.
- 감정 추적 및 대화 흐름 내 일관성 유지에 중점.

**Context Memory 관리**

- LangChain의 Redis 기반의 커스텀 메모리 구현으로 사용자별 세션 맥락 보존.

**Docker 기반 배포** 

- AI 서버를 컨테이너화하여 다른 서비스와의 연동 및 배포 효율성 확보.

### ॅ 사용 기술 스택

- Backend: FastAPI, LangChain
- Database: MongoDB, Pinecone, Redis(Upstash)
- AI : Chat GPT

### ब 프로젝트를 통해 깨달은 점

이 프로젝트를 통해 비동기 처리가 실시간성과 안정성에 필수적인지 체감할 수 있었습니다.

FastAPI는 비동기 프레임워크지만, 내부에서 동기적으로 처리되는 블로킹 작업(API 호출, 파일 I/O 등)이 포함되면 전체 이벤트 루프가 지연되며, 결과적으로 응답이 누락되거나 지연될 수 있다는 점을 실전에서 확인했습니다.

### ꥟ 트러블슈팅 #1 대화 문맥 끊기는 현상

  대화 중 문맥이 자주 끊겨 사용자 경험에 불편함이 있었습니다. 이를 해결하기 위해 LangChain 프레임워크`UpstashRedisChatMessageHistory`를 활용해 사용자별 대화 내역을 `Redis`에 저장하고 관리하도록 개선했습니다. 덕분에 카카오톡 챗봇이 이전 대화를 기억하며 문맥에 맞는 응답을 제공할 수 있게 되었고, 사용자가 원하는 질문에 더 정확하고 자연스러운 대응이 가능해졌습니다. 결과적으로 대화 흐름이 훨씬 매끄러워져 사용자 만족도가 향상되었습니다. 

### ꥟ 트러블슈팅 #2 비동기 처리

  비동기 처리를 도입하기 전, 시스템에서는 동시에 두 가지 이상의 요청이 들어올 경우 이전에 처리 중이던 요청이 제대로 완료되지 않고 무시되는 현상이 발생했습니다. 이로 인해 일부 요청이 누락되거나 응답이 지연되어 사용자 경험에 큰 불편을 초래했습니다.

  FastAPI는 `싱글스레드 이벤트 루프 기반`으로 동작하기 때문에, 동기 방식의 처리에서는 하나의 요청이 처리되는 동안 다른 요청들은 대기 상태에 놓이거나 무시될 위험이 있었습니다. 특히, `외부 API 호출(LLM 호출)` 등 블로킹 작업이 포함되면 이러한 문제는 더욱 심각해졌습니다.

  이에 따라, 비동기 처리를 도입하여 모든 주요 작업을 비동기 함수로 전환하고, API 핸들러 또한 비동기 함수(`async def`)로 구현하였습니다.

  이러한 개선을 통해, 여러 요청이 동시에 들어와도 각 요청이 독립적으로 처리될 수 있게 되었고, 요청 간 충돌과 지연이 크게 줄어들었습니다. 결과적으로 요청이 무시되는 현상이 해결되었습니다.

---
## 홍보 활동

<img width="1440" alt="백엔드 개발자 박동현 이미지" src="https://github.com/user-attachments/assets/c9ad5992-a646-43bb-926d-4cfc372ba1e8" />

부산소프트웨어마이스터고등학교의 정보에 대해 관심이 많을 학부모님과 학생들을 대상으로 네이버 블로그를 작성하였습니다.

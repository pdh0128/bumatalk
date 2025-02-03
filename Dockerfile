FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .
# 포트 노출
EXPOSE 8000
# FastAPI 애플리케이션 실행 명령어
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

from selenium import webdriver
from selenium.common import ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from llm import summary
from mongo import Mongo

load_dotenv()
embeddings = OpenAIEmbeddings()
api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX")
pc = Pinecone(api_key=api_key)
pinecone_index = pc.Index(index_name)
vector_store = PineconeVectorStore(index_name=index_name, embedding=embeddings)


def store(name, text, url):
    if name is None or name == "":
        print("이름이 비어있습니다.")
        return

    summary_Text = summary(name, text)
    embedding = embeddings.embed_query(summary_Text)
    vector_store.add_texts(
        texts=[summary_Text],
        metadatas=[{"name": name}],
        embeddings=[embedding],
        ids=[url]
    )
    print(summary_Text)
    print("Ok, Store")


def bumawiki():
    db = Mongo()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    url = "https://buma.wiki/student"
    options = Options()
    # options.add_argument('--headless')
    options.add_argument(f"user-agent={user_agent}")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    visited_name = set()
    try:
        while True:
            elements = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "bumawiki_1mrozeh4"))
            )
            if not elements:
                print("더 이상 요소가 없습니다. 종료합니다.")
                break

            for i in range(len(elements)):
                elements = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "bumawiki_1mrozeh4"))
                )
                element = elements[i]
                name = element.text.strip()
                if name in visited_name:
                    continue
                visited_name.add(name)
                try:
                    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(element))
                    element.click()
                except ElementClickInterceptedException as e:
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(3)
                content = driver.page_source
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text().split("데이터를 제공할 수 있습니다.")[1][1:].split("문서 기여자")[0].strip()
                current_url = driver.current_url
                print(name)
                store(name, text, current_url)
                db.insertStudent(name, text, current_url)
                driver.back()
                time.sleep(5)
    except Exception as e:
        print(f"오류 발생: {e}")
    driver.quit()


bumawiki()

def namuwiki():
    options = Options()
    options.add_argument('--headless')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(300)
    url = "https://namu.wiki/w/%EB%B6%80%EC%82%B0%EC%86%8C%ED%94%84%ED%8A%B8%EC%9B%A8%EC%96%B4%EB%A7%88%EC%9D%B4%EC%8A%A4%ED%84%B0%EA%B3%A0%EB%93%B1%ED%95%99%EA%B5%90"
    driver.get(url)
    driver.set_window_size(1000, 900)
    time.sleep(10)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    page_text = soup.get_text()
    print(page_text)
    store("부산소프트웨어마이스터고등학교_나무위키", page_text, url)
    driver.quit()

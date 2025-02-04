from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict

class schoolTimer(BaseModel):
    grade: str = Field(description="그 사람의 학년")
    classroom: str = Field(description="그 사람의 반")
    date: str =  Field(description="그 사람이 얻고자하는 시간표 날짜")
    def to_dict(self) -> Dict[str, str]:
        return {"grade": self.grade, "classroom": self.classroom, "date": self.date}

schoolTimeOuputParser = PydanticOutputParser(pydantic_object=schoolTimer)

class schoolScheduler(BaseModel):
    frist_date: str = Field(description="시작 날짜")
    last_date: str = Field(description="마지막 날짜")
    def to_dict(self) -> Dict[str, str]:
        return {"first_date": self.frist_date, "last_date": self.last_date}

schoolScheduleOutputParser = PydanticOutputParser(pydantic_object=schoolScheduler)
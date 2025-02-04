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
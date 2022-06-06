from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Union


class MessageOutput(BaseModel):
    message1: str = Field(..., title="Greeting")
    message2: str = Field(..., title="Calculation result")
    n: int = Field(..., title="n: a large integer")
    largest_prime_factor: int = Field(..., title="Largest prime factor of n")
    elapsed_time: float = Field(..., title="Calculation time (seconds)")


class URLOutput(BaseModel):
    result_link: str
    result_image: Optional[str] = None
    long_link: Optional[str] = None


class URLDeepOutput(BaseModel):
    result_link: str
    result_link_long: str


class DirectChunksOUT(BaseModel):
    id: str
    number_of_chunks: str


class DirectProgress(BaseModel):
    progress: int


class PromotionCurrentOUT(BaseModel):
    name_1: Optional[str]
    name_2: Optional[str]
    name_3: Optional[str]
    name_4: Optional[str]


class UploadOUT(BaseModel):
    link: str


class SMMGeneratorOUT(BaseModel):
    result_link: str


class VisualsCheckOUT(BaseModel):
    price_old: Optional[str]
    price_current: Optional[str]
    vendor: Optional[str]
    title: Optional[str]
    is_available: str


class VisualsGenerateOUT(BaseModel):
    link: str
    width: str
    height: str


class VisualsTemplate(BaseModel):
    value: str
    text: str


class VisualsTemplateOUT(BaseModel):
    data: List[VisualsTemplate]


class SegmentatorGetValuesOUT(BaseModel):
    field: str
    values: Union[List[Dict],List[str]]


class SamsungBillCheckerOUT(BaseModel):
    response: str


class ContentShowcasesOUT(BaseModel):
    status_code: str
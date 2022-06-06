from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Union
from fastapi import File, UploadFile


class MessageInput(BaseModel):
    pass
    # field1: str = Field(..., title="First string field")
    # field2: str = Field(..., title="Second string field")


class URLInput(BaseModel):
    url_base: str
    utm_source: Optional[str]
    utm_medium: Optional[str]
    utm_campaign: Optional[str]
    qr: bool = False
    lifetime: Optional[str]
    vip_code: Optional[str]


class DirectChunksIN(BaseModel):
    id: str


class CustomIN(BaseModel):
    event: str
    category: str
    label: str
    file: str


class MappingIN(BaseModel):
    category: str
    source: str
    file: str


class URLInputBanks(BaseModel):
    campaign: str
    my_date: str


class MappingChangeIN(BaseModel):
    file: str


class PromotionSKUIN(BaseModel):
    sku_1: Optional[str]
    date_to_1: Optional[str]
    sku_2: Optional[str]
    date_to_2: Optional[str]
    sku_3: Optional[str]
    date_to_3: Optional[str]
    sku_4: Optional[str]
    date_to_4: Optional[str]


class URLInputDeeplinks(BaseModel):
    url_base: str
    utm_source: Optional[str]
    utm_medium: Optional[str]
    utm_campaign: Optional[str]
    ofl: Optional[str]


class MapEventsIN(BaseModel):
    summary: str
    title: str
    date_start: str
    date_end: str
    group: str
    checked_points: Optional[List[str]]
    file: str
    instance: str
    link: str


class MapEventsCallIN(BaseModel):
    summary: str
    cta_types: str
    link: str
    file: str
    checked_points: Optional[List[str]]
    group: str
    instance: str


class MapEventsSpecOfferIN(BaseModel):
    summary: str
    coupon: str
    coupon_url: str
    title: str
    date_start: str
    date_end: str
    file: str
    checked_points: Optional[List[str]]
    group: str
    instance: str
    terms: str


class UploadIN(BaseModel):
    file: str
    name: str


class SMMGeneratorIN(BaseModel):
    checked_points: Optional[List[str]]
    file: str
    event_name: str
    group: str
    country: str
    readable: str


class VisualsCheckIN(BaseModel):
    sku: str
    locale: str


class VisualsGenerateIN(BaseModel):
    sku: str
    event_name: str
    event_value: str
    event_name_2: Optional[str]
    event_value_2: Optional[str]
    price_current: str
    price_old: Optional[str]
    title: str
    title_bottom: Optional[str]
    description: Optional[str]
    description_bottom: Optional[str]
    vendor: str
    locale: str
    resize: str
    template_group: Optional[str]


class VisualsPostToTgIN(BaseModel):
    sku: str
    event_name: str
    event_value: str
    event_name_2: Optional[str]
    event_value_2: Optional[str]
    image_link: str
    title: str
    title_bottom: Optional[str]
    locale: str
    template_group: str


class URLStatusMulti(BaseModel):
    task_id: str


class URLInputMulti(BaseModel):
    file: str


class SegmentatorFilterIN(BaseModel):
    include: str
    field: str
    values: Union[str, List[str]]


class SegmentatorGetValuesIN(BaseModel):
    field: str
    data_source: str
    filters: Union[List[SegmentatorFilterIN], str]


class SamsungBillCheckerIN(BaseModel):
    id: str
    phone: Optional[str]
    operation: str


class ContentShowcasesIN(BaseModel):
    author: str
    sku: str
    showcase_desktop: str
    showcase_mobile: str

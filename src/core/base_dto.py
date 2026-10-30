from typing import TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

T = TypeVar('T')


class BaseSchema(BaseModel):
    # конфиг
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        extra='ignore',
    )


class PageData[T](BaseModel):
    """
    Постраничная выдача
    """

    data: list[T] = Field(description='Page data')
    total_count: int = Field(description='Total count')

    # конфиг
    model_config = ConfigDict(from_attributes=True)


class Pagination(BaseModel):
    """Параметры пагинации"""

    index: int = Field(description='Limit')
    count: int = Field(description='Offset')

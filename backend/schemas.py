from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _strip(value):
    if isinstance(value, str):
        return value.strip()
    return value


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    role: str = "user"

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        if value not in {"user", "admin"}:
            raise ValueError("Roli duhet të jetë user ose admin")
        return value


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _empty_to_none(value):
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return _strip(value) if isinstance(value, str) else value


class PropertyCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    location: str = Field(min_length=1, max_length=255)
    neighborhood: str | None = Field(default=None, max_length=255)
    price: float = Field(gt=0)
    bedrooms: int = Field(ge=0, le=50)
    bathrooms: int = Field(ge=0, le=50)
    area_sqm: float = Field(gt=0)
    property_type: str = Field(min_length=1, max_length=100)

    @field_validator("title", "location", "property_type", mode="before")
    @classmethod
    def strip_text(cls, value):
        return _strip(value)

    @field_validator("neighborhood", mode="before")
    @classmethod
    def normalize_neighborhood(cls, value):
        return _empty_to_none(value)


class PropertyOut(BaseModel):
    id: int
    title: str
    location: str
    neighborhood: str | None = None
    price: float
    bedrooms: int
    bathrooms: int
    area_sqm: float
    price_per_sqm: float
    property_type: str
    created_by_id: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("price", "area_sqm", "price_per_sqm", mode="before")
    @classmethod
    def cast_decimal(cls, value):
        return float(value)


class PropertyUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    location: str = Field(min_length=1, max_length=255)
    neighborhood: str | None = Field(default=None, max_length=255)
    price: float = Field(gt=0)
    bedrooms: int = Field(ge=0, le=50)
    bathrooms: int = Field(ge=0, le=50)
    area_sqm: float = Field(gt=0)
    property_type: str = Field(min_length=1, max_length=100)

    @field_validator("title", "location", "property_type", mode="before")
    @classmethod
    def strip_text(cls, value):
        return _strip(value)

    @field_validator("neighborhood", mode="before")
    @classmethod
    def normalize_neighborhood(cls, value):
        return _empty_to_none(value)


class PropertyList(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[PropertyOut]


class PredictRequest(BaseModel):
    location: str = Field(min_length=1, max_length=255)
    neighborhood: str | None = Field(default=None, max_length=255)
    bedrooms: int = Field(ge=0, le=50)
    bathrooms: int = Field(ge=0, le=50)
    area_sqm: float = Field(gt=0)
    property_type: str = Field(min_length=1, max_length=100)

    @field_validator("location", "property_type", mode="before")
    @classmethod
    def strip_text(cls, value):
        return _strip(value)

    @field_validator("neighborhood", mode="before")
    @classmethod
    def normalize_neighborhood(cls, value):
        return _empty_to_none(value)


class PredictResponse(BaseModel):
    predicted_price: float
    currency: str = "EUR"

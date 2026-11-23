
from pydantic import BaseModel, Field, ConfigDict, EmailStr



class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr


# CANDIDATE SCHEMAS

class CandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None


# VOTE SCHEMAS

class VoteCreate(BaseModel):
    candidate_id: int = Field(gt=0)


class VoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    candidate_id: int

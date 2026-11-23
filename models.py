
from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    votes: Mapped[list[Vote]] = relationship(
        back_populates="user"
    )


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(255), nullable=True
    )

    votes: Mapped[list[Vote]] = relationship(
        back_populates="candidate"
    )


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False
    )

    user: Mapped[User] = relationship(
        back_populates="votes"
    )

    candidate: Mapped[Candidate] = relationship(
        back_populates="votes"
    )

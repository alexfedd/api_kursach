from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import UniqueConstraint

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    tag = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    avatar = Column(String, nullable=True)
    banner = Column(String, nullable=True)
    hashed_password = Column(String)
    activated = Column(Boolean, default=True)
    activation_code = Column(String, nullable=True)
    posts = relationship("Post", back_populates="author")
    liked_posts = relationship("Post", secondary="likes", back_populates="likes")
    followers = relationship(
        "User",
        secondary="follows",
        primaryjoin="User.id == Follow.followed_id",
        secondaryjoin="User.id == Follow.follower_id",
        backref="following"
    )

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    parent_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    author = relationship("User", back_populates="posts")
    likes = relationship("User", secondary="likes", back_populates="liked_posts")
    replies = relationship("Post", backref="parent", remote_side=[id])

class Like(Base):
    __tablename__ = "likes"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='unique_like'),
    )

class Follow(Base):
    __tablename__ = "follows"
    follower_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    followed_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),
    )
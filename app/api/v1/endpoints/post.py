from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from typing import List, Optional
from app.core import models, database, schemas
from app.dependencies import auth
from datetime import datetime

router = APIRouter()

@router.post("/posts/", response_model=schemas.DefaultResponse)
async def create_post(
    post: schemas.PostCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    new_post = models.Post(
        text=post.text,
        author_id=current_user.id,
        parent_id=post.parent_id
    )
    new_post.author = current_user
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return {
        "State": status.HTTP_200_OK,
        "Message": "Post created successfully"
    }

@router.get("/users/{user_id}/posts/", response_model=List[schemas.PostResponse])
async def get_user_posts(
    user_id: int,
    page: int = Query(1, description="Page number"),
    size: int = Query(10, description="Page size"),
    db: AsyncSession = Depends(database.get_db),
    current_user: Optional[models.User] = Depends(auth.get_current_user_optional)
):
    offset = (page - 1) * size
    query = (
        select(models.Post)
        .where(models.Post.author_id == user_id)
        .order_by(models.Post.created_at.desc())
        .offset(offset)
        .limit(size)
        .options(joinedload(models.Post.author))
    )
    result = await db.execute(query)
    posts = result.scalars().all()

    post_ids = [post.id for post in posts]

    # Count likes
    likes_query = (
        select(models.Like.post_id, func.count(models.Like.user_id).label("likes_count"))
        .where(models.Like.post_id.in_(post_ids))
        .group_by(models.Like.post_id)
    )
    likes_result = await db.execute(likes_query)
    likes_counts = {row.post_id: row.likes_count for row in likes_result}

    # Count comments
    comments_query = (
        select(models.Post.parent_id, func.count(models.Post.id).label("comments_count"))
        .where(models.Post.parent_id.in_(post_ids))
        .group_by(models.Post.parent_id)
    )
    comments_result = await db.execute(comments_query)
    comments_counts = {row.parent_id: row.comments_count for row in comments_result}

    # Check liked status for authenticated user
    if current_user:
        liked_query = (
            select(models.Like.post_id)
            .where(models.Like.user_id == current_user.id)
            .where(models.Like.post_id.in_(post_ids))
        )
        liked_result = await db.execute(liked_query)
        liked_posts = {row.post_id for row in liked_result}
    else:
        liked_posts = set()

    # Build response
    response_posts = [
        schemas.PostResponse(
            id=post.id,
            text=post.text,
            author=schemas.AuthorResponse(id=post.author.id, username=post.author.username, tag=post.author.tag, avatar=post.author.avatar),
            created_at=post.created_at,
            parent_id=post.parent_id,
            likes_count=likes_counts.get(post.id, 0),
            comments_count=comments_counts.get(post.id, 0),
            is_liked=post.id in liked_posts,
            is_authenticated=current_user is not None
        )
        for post in posts
    ]
    return response_posts

@router.get("/posts/", response_model=List[schemas.PostResponse])
async def get_all_posts(
    page: int = Query(1, description="Page number"),
    size: int = Query(10, description="Page size"),
    db: AsyncSession = Depends(database.get_db),
    current_user: Optional[models.User] = Depends(auth.get_current_user_optional)
):
    offset = (page - 1) * size
    query = (
        select(models.Post)
        .order_by(models.Post.created_at.desc())
        .offset(offset)
        .limit(size)
        .options(joinedload(models.Post.author))
    )
    result = await db.execute(query)
    posts = result.scalars().all()

    post_ids = [post.id for post in posts]

    # Count likes
    likes_query = (
        select(models.Like.post_id, func.count(models.Like.user_id).label("likes_count"))
        .where(models.Like.post_id.in_(post_ids))
        .group_by(models.Like.post_id)
    )
    likes_result = await db.execute(likes_query)
    likes_counts = {row.post_id: row.likes_count for row in likes_result}

    # Count comments
    comments_query = (
        select(models.Post.parent_id, func.count(models.Post.id).label("comments_count"))
        .where(models.Post.parent_id.in_(post_ids))
        .group_by(models.Post.parent_id)
    )
    comments_result = await db.execute(comments_query)
    comments_counts = {row.parent_id: row.comments_count for row in comments_result}

    # Check liked status for authenticated user
    if current_user:
        liked_query = (
            select(models.Like.post_id)
            .where(models.Like.user_id == current_user.id)
            .where(models.Like.post_id.in_(post_ids))
        )
        liked_result = await db.execute(liked_query)
        liked_posts = {row.post_id for row in liked_result}
    else:
        liked_posts = set()

    # Build response
    response_posts = [
        schemas.PostResponse(
            id=post.id,
            text=post.text,
            author=schemas.AuthorResponse(id=post.author.id, username=post.author.username, tag=post.author.tag, avatar=post.author.avatar),
            created_at=post.created_at,
            parent_id=post.parent_id,
            likes_count=likes_counts.get(post.id, 0),
            comments_count=comments_counts.get(post.id, 0),
            is_liked=post.id in liked_posts,
            is_authenticated=current_user is not None
        )
        for post in posts
    ]
    return response_posts
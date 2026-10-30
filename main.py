from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import Bookmark

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="个人书签管理系统")


# Pydantic 模型
class BookmarkCreate(BaseModel):
    title: str
    url: str
    description: Optional[str] = None


class BookmarkUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None


class BookmarkResponse(BaseModel):
    id: int
    title: str
    url: str
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# CRUD API 接口

@app.post("/bookmarks", response_model=BookmarkResponse, status_code=201)
def create_bookmark(bookmark: BookmarkCreate, db: Session = Depends(get_db)):
    """创建新书签"""
    db_bookmark = Bookmark(
        title=bookmark.title,
        url=bookmark.url,
        description=bookmark.description
    )
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark


@app.get("/bookmarks", response_model=List[BookmarkResponse])
def get_bookmarks(db: Session = Depends(get_db)):
    """获取所有书签列表"""
    bookmarks = db.query(Bookmark).all()
    return bookmarks


@app.get("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
def get_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    """根据 ID 获取单个书签"""
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="书签不存在")
    return bookmark


@app.put("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
def update_bookmark(bookmark_id: int, bookmark_update: BookmarkUpdate, db: Session = Depends(get_db)):
    """更新书签"""
    db_bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not db_bookmark:
        raise HTTPException(status_code=404, detail="书签不存在")

    # 只更新提供的字段
    if bookmark_update.title is not None:
        db_bookmark.title = bookmark_update.title
    if bookmark_update.url is not None:
        db_bookmark.url = bookmark_update.url
    if bookmark_update.description is not None:
        db_bookmark.description = bookmark_update.description

    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark


@app.delete("/bookmarks/{bookmark_id}")
def delete_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    """删除书签"""
    db_bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not db_bookmark:
        raise HTTPException(status_code=404, detail="书签不存在")

    db.delete(db_bookmark)
    db.commit()
    return {"message": "书签已删除"}

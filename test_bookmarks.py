import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from models import Bookmark  # 导入模型以确保表被注册到 Base.metadata


@pytest.fixture(scope="function")
def client():
    """为每个测试创建独立的临时数据库文件"""
    # 创建临时数据库文件
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # 使用临时文件创建引擎
        test_engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=test_engine)
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        
        def override_get_db():
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()
        
        from main import app
        app.dependency_overrides[get_db] = override_get_db
        
        with TestClient(app) as test_client:
            yield test_client
        
        app.dependency_overrides.clear()
    finally:
        # 清理临时文件
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_create_bookmark(client):
    """测试创建书签"""
    response = client.post("/bookmarks", json={
        "title": "Google",
        "url": "https://www.google.com",
        "description": "搜索引擎"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Google"
    assert data["url"] == "https://www.google.com"
    assert data["description"] == "搜索引擎"
    assert "id" in data
    assert "created_at" in data


def test_get_bookmarks(client):
    """测试获取书签列表"""
    # 先创建两个书签
    client.post("/bookmarks", json={
        "title": "Google",
        "url": "https://www.google.com"
    })
    client.post("/bookmarks", json={
        "title": "GitHub",
        "url": "https://github.com"
    })

    response = client.get("/bookmarks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    titles = [item["title"] for item in data]
    assert "Google" in titles
    assert "GitHub" in titles


def test_get_bookmark_by_id(client):
    """测试根据 ID 获取单个书签"""
    # 先创建一个书签
    create_response = client.post("/bookmarks", json={
        "title": "Python",
        "url": "https://www.python.org",
        "description": "Python 官网"
    })
    bookmark_id = create_response.json()["id"]

    response = client.get(f"/bookmarks/{bookmark_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == bookmark_id
    assert data["title"] == "Python"
    assert data["url"] == "https://www.python.org"


def test_update_bookmark(client):
    """测试更新书签"""
    # 先创建一个书签
    create_response = client.post("/bookmarks", json={
        "title": "Old Title",
        "url": "https://old.example.com",
        "description": "Old description"
    })
    bookmark_id = create_response.json()["id"]

    # 更新书签
    response = client.put(f"/bookmarks/{bookmark_id}", json={
        "title": "New Title",
        "url": "https://new.example.com"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["url"] == "https://new.example.com"
    # description 应该保持不变
    assert data["description"] == "Old description"


def test_delete_bookmark(client):
    """测试删除书签"""
    # 先创建一个书签
    create_response = client.post("/bookmarks", json={
        "title": "To Delete",
        "url": "https://delete.example.com"
    })
    bookmark_id = create_response.json()["id"]

    # 删除书签
    response = client.delete(f"/bookmarks/{bookmark_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "书签已删除"

    # 验证书签已被删除
    get_response = client.get(f"/bookmarks/{bookmark_id}")
    assert get_response.status_code == 404


def test_get_nonexistent_bookmark(client):
    """测试获取不存在的书签返回 404"""
    response = client.get("/bookmarks/99999")
    assert response.status_code == 404
    assert "书签不存在" in response.json()["detail"]

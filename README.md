# bookmark-api

基于 FastAPI + SQLAlchemy + SQLite 的书签管理 REST API。

## 功能

- 书签增删改查
- 分页（`skip` / `limit`）
- 标签过滤（`tag`）
- 模糊搜索（标题 / 描述 / URL）
- URL 唯一约束、时间戳自动维护

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/bookmarks` | 创建 |
| GET | `/bookmarks` | 列表（支持 `search` / `tag` / `skip` / `limit`） |
| GET | `/bookmarks/{id}` | 详情 |
| PUT | `/bookmarks/{id}` | 更新 |
| DELETE | `/bookmarks/{id}` | 删除 |

## 运行

```bash
pip install -r requirements.txt
uvicorn main:app --reload
# 文档: http://127.0.0.1:8000/docs
```

## 测试

```bash
pytest -v
```

6 个用例覆盖：创建、列表、详情、更新、删除、404；每个用例使用独立临时数据库，通过 `dependency_overrides` 替换 `get_db`，互不污染。

## 设计说明

- 分层：`main`（应用与路由）/ `models`（ORM）/ `database`（引擎与会话）
- 测试隔离：临时文件 + 每例重建表，避免测试之间串数据
- 踩坑：调用 `Base.metadata.create_all` 之前必须先 import 模型，否则表没注册，运行时报 `no such table: bookmarks`

## License

MIT

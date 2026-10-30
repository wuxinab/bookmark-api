from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from database import Base


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Bookmark(id={self.id}, title='{self.title}', url='{self.url}')"

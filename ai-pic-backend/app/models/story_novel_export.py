from app.core.database import Base
from app.models.base import SoftDeleteBusinessMixin
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class StoryNovelExport(SoftDeleteBusinessMixin, Base):
    """Persisted long-form novel export generated from a Story (e.g. Zhihu-style)."""

    __tablename__ = "story_novel_exports"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False, index=True)
    story_business_id = Column(
        String(32),
        nullable=True,
        index=True,
        comment="Ye Wu Zhu Jian: story business_id",
    )
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    style = Column(String(32), nullable=False, default="zhihu", comment="output style")
    target_words = Column(Integer, nullable=False, comment="target word count")
    chapter_count = Column(Integer, nullable=True, comment="Zhang Jie Shu")
    total_words = Column(Integer, nullable=True, comment="Shi Ji word count")
    model = Column(String(128), nullable=True, comment="text Sheng Cheng model(Yuan Yang)")
    temperature = Column(Float, nullable=True, comment="Sheng Cheng Wen Du")

    file_relative_path = Column(String(512), nullable=True, comment="Dao Chu file Xiang Dui Lu Jing")
    content_text = Column(
        Text().with_variant(mysql.LONGTEXT(), "mysql"),
        nullable=False,
        comment="Dao Chu content text(Ke Neng Jiao Zhang)",
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    story = relationship("Story", backref="novel_exports")
    task = relationship("Task")
    user = relationship("User")

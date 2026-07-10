from datetime import datetime

from app.core.database import Base
from app.models.base import SoftDeleteBusinessMixin
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship


class Story(SoftDeleteBusinessMixin, Base):
    """story outline model"""

    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True, comment="Suo Shu userID"
    )
    title = Column(String(255), nullable=False, comment="story title")
    story_format = Column(
        String(32),
        nullable=False,
        default="short_drama",
        comment="story Xing Tai: short_drama/tv_series/film",
    )
    genre = Column(String(50), nullable=False, comment="story type")
    theme = Column(String(255), comment="story Zhu Ti")
    target_audience = Column(String(100), comment="target Shou Zhong")
    duration_minutes = Column(Integer, comment="Yu Ji total duration(minutes)")
    default_aspect_ratio = Column(
        String(8),
        nullable=False,
        default="9:16",
        comment="default Hua Fu: 9:16/16:9",
    )

    # story content
    premise = Column(Text, comment="story Qian Ti")
    synopsis = Column(Text, comment="story outline")
    main_conflict = Column(Text, comment="Main conflict")
    resolution = Column(Text, comment="Jie Jue Fang An")

    # Character information
    main_characters = Column(JSON, comment="Main characterlist")
    character_relationships = Column(JSON, comment="character relationship")

    # setting Xin Xi
    setting_time = Column(String(100), comment="time setting")
    setting_location = Column(String(255), comment="Di Dian setting")
    world_building = Column(Text, comment="Shi Jie Guan setting")

    # AI generation related
    generation_prompt = Column(Text, comment="Generation prompt")
    ai_model = Column(String(50), comment="AI model used")
    generation_params = Column(JSON, comment="Generation parameters")

    # Status and metadata
    status = Column(
        String(20), default="draft", comment="status: draft, approved, published"
    )
    is_public = Column(Boolean, default=False, comment="Shi Fou Gong Kai")
    tags = Column(JSON, comment="Tag list")
    extra_metadata = Column(JSON, comment="Additional metadata")

    # time Chuo
    created_at = Column(DateTime, default=datetime.utcnow, comment="create time")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="update time"
    )

    # relationship
    episodes = relationship(
        "Episode", back_populates="story", cascade="all, delete-orphan"
    )
    story_characters = relationship(
        "StoryCharacter", back_populates="story", cascade="all, delete-orphan"
    )


class Episode(SoftDeleteBusinessMixin, Base):
    """episode model"""

    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(
        Integer, ForeignKey("stories.id"), nullable=False, comment="storyID"
    )
    story_business_id = Column(
        String(32), index=True, nullable=True, comment="Ye Wu Zhu Jian: story business_id"
    )
    episode_number = Column(Integer, nullable=False, comment="Ji Shu")
    title = Column(String(255), nullable=False, comment="episode title")

    # episode content
    summary = Column(Text, comment="episode outline")
    plot_points = Column(JSON, comment="Qing Jie Yao Dian")
    character_arcs = Column(JSON, comment="character Fa Zhan")
    conflicts = Column(JSON, comment="Chong Tu Dian")

    # Ji Shu Xin Xi
    duration_minutes = Column(Integer, comment="Yu Ji when Zhang(minutes)")
    scene_count = Column(Integer, comment="scene Shu Liang")
    aspect_ratio = Column(
        String(8),
        nullable=True,
        comment="can Xuan Hua Fu Fu Gai: 9:16/16:9(as Kong Ze Ji Cheng Story.default_aspect_ratio)",
    )

    # AI generation related
    generation_prompt = Column(Text, comment="Generation prompt")
    ai_model = Column(String(50), comment="AI model used")
    generation_params = Column(JSON, comment="Generation parameters")

    # Status and metadata
    status = Column(
        String(20), default="draft", comment="status: draft, approved, published"
    )
    tags = Column(JSON, comment="Tag list")
    extra_metadata = Column(JSON, comment="Additional metadata")

    # time Chuo
    created_at = Column(DateTime, default=datetime.utcnow, comment="create time")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="update time"
    )

    # relationship
    story = relationship("Story", back_populates="episodes")
    scripts = relationship(
        "Script", back_populates="episode", cascade="all, delete-orphan"
    )
    episode_characters = relationship(
        "EpisodeCharacter", back_populates="episode", cascade="all, delete-orphan"
    )


class Script(SoftDeleteBusinessMixin, Base):
    """script model"""

    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(
        Integer, ForeignKey("episodes.id"), nullable=False, comment="episodeID"
    )
    episode_business_id = Column(
        String(32), index=True, nullable=True, comment="Ye Wu Zhu Jian: episode business_id"
    )
    title = Column(String(255), nullable=False, comment="script title")

    # script content
    content = Column(Text, comment="script content")
    scenes = Column(JSON, comment="scene list")
    dialogues = Column(JSON, comment="Dui Hua list")
    stage_directions = Column(JSON, comment="Wu Tai Zhi Shi")

    # format Xin Xi
    format_type = Column(String(50), default="screenplay", comment="script format type")
    language = Column(String(10), default="zh-CN", comment="Yu Yan")

    # Ji Shu Xin Xi
    page_count = Column(Integer, comment="Ye Shu")
    word_count = Column(Integer, comment="word count")
    character_count = Column(Integer, comment="Zi Fu Shu")

    # AI generation related
    generation_prompt = Column(Text, comment="Generation prompt")
    ai_model = Column(String(50), comment="AI model used")
    generation_params = Column(JSON, comment="Generation parameters")

    # Status and metadata
    status = Column(
        String(20), default="draft", comment="status: draft, approved, published"
    )
    version = Column(String(20), default="1.0", comment="Ban Ben Hao")
    tags = Column(JSON, comment="Tag list")
    extra_metadata = Column(JSON, comment="Additional metadata")
    storyboard_plan = Column(JSON, comment="Zui Xin storyboard Gui Hua")
    storyboard_version = Column(Integer, default=1, comment="storyboard Ban Ben Hao")
    storyboard_updated_at = Column(DateTime, comment="storyboard Zui Jin update time")

    # time Chuo
    created_at = Column(DateTime, default=datetime.utcnow, comment="create time")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="update time"
    )

    # relationship
    episode = relationship("Episode", back_populates="scripts")


class StoryCharacter(SoftDeleteBusinessMixin, Base):
    """story character Guan Lian model"""

    __tablename__ = "story_characters"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(
        Integer, ForeignKey("stories.id"), nullable=False, comment="storyID"
    )
    story_business_id = Column(
        String(32), index=True, nullable=True, comment="Ye Wu Zhu Jian: story business_id"
    )
    virtual_ip_id = Column(
        Integer, ForeignKey("virtual_ips.id"), nullable=False, comment="Xu NiIP ID"
    )
    virtual_ip_business_id = Column(
        String(32), index=True, nullable=True, comment="Ye Wu Zhu Jian: Xu NiIP business_id"
    )

    # Character information
    character_name = Column(String(100), comment="character name")
    role_type = Column(
        String(50), comment="character type: protagonist, antagonist, supporting"
    )
    importance = Column(Integer, default=1, comment="Zhong Yao Du: 1-5")

    # character setting
    personality = Column(Text, comment="Xing Ge Te Dian")
    background = Column(Text, comment="background story")
    motivation = Column(Text, comment="Dong Ji")
    character_arc = Column(Text, comment="character Fa Zhan Hu Xian")

    # relationship setting
    relationships = Column(JSON, comment="and Qi Ta character relationship")

    # time Chuo
    created_at = Column(DateTime, default=datetime.utcnow, comment="create time")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="update time"
    )

    # relationship
    story = relationship("Story", back_populates="story_characters")
    virtual_ip = relationship("VirtualIP")

    @property
    def virtual_ip_name(self):
        virtual_ip = getattr(self, "virtual_ip", None)
        return getattr(virtual_ip, "name", None) if virtual_ip else None

    @property
    def name(self):
        return self.character_name or self.virtual_ip_name

    @property
    def display_name(self):
        return self.name or f"character{self.id}"


class ScriptTemplate(SoftDeleteBusinessMixin, Base):
    """script template model"""

    __tablename__ = "script_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="template name")
    category = Column(String(50), comment="template Fen Lei")

    # template content
    template_content = Column(Text, comment="template content")
    structure = Column(JSON, comment="structure Ding Yi")
    variables = Column(JSON, comment="Bian Liang Ding Yi")

    # Shi Yong Xin Xi
    usage_count = Column(Integer, default=0, comment="Shi Yong Ci Shu")
    rating = Column(Float, comment="Ping Fen")

    # status
    is_active = Column(Boolean, default=True, comment="Shi Fou Ji Huo")
    is_public = Column(Boolean, default=False, comment="Shi Fou Gong Kai")

    # time Chuo
    created_at = Column(DateTime, default=datetime.utcnow, comment="create time")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="update time"
    )

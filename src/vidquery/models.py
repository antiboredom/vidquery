from typing import List
from sqlalchemy import ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Video(Base):
    __tablename__ = "videos"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    path: Mapped[str] = mapped_column(String, unique=True, index=True)
    hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    duration: Mapped[float] = mapped_column(Float)
    fps: Mapped[float] = mapped_column(Float)
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)

    clips: Mapped[List["Clip"]] = relationship("Clip", back_populates="video")
    parsers: Mapped[List["Parser"]] = relationship("Parser", secondary="videoparsers")


class Clip(Base):
    __tablename__ = "clips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    start: Mapped[float] = mapped_column(Float)
    end: Mapped[float] = mapped_column(Float)
    content: Mapped[str] = mapped_column(String)

    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id"))
    video: Mapped["Video"] = relationship("Video", back_populates="clips")

    parser_id: Mapped[int] = mapped_column(Integer, ForeignKey("parsers.id"))
    parser: Mapped["Parser"] = relationship("Parser", back_populates="clips")


class Parser(Base):
    __tablename__ = "parsers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    cat: Mapped[str] = mapped_column(String, index=True)
    subcat: Mapped[str] = mapped_column(String, index=True)

    clips: Mapped[List["Clip"]] = relationship("Clip", back_populates="parser")


class VideoParser(Base):
    __tablename__ = "videoparsers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    video_id: Mapped[int] = mapped_column(Integer, ForeignKey("videos.id"))
    parser_id: Mapped[int] = mapped_column(Integer, ForeignKey("parsers.id"))


# class Video(Base):
#     __tablename__ = "videos"
#     id = Column(Integer, primary_key=True, index=True)
#     path = Column(String, unique=True, index=True)
#     hash = Column(String, unique=True, index=True)
#     duration = Column(Float)
#     fps = Column(Float)
#     width = Column(Integer)
#     height = Column(Integer)
#
#     clips = relationship("Clip", back_populates="video")
#     parsers = relationship("Parser", secondary="videoparsers")
#
#
# class Clip(Base):
#     __tablename__ = "clips"
#
#     id = Column(Integer, primary_key=True, index=True)
#     start = Column(Float)
#     end = Column(Float)
#     content = Column(String)
#
#     video_id = Column(Integer, ForeignKey("videos.id"))
#     video = relationship("Video", back_populates="clips")
#
#     parser_id = Column(Integer, ForeignKey("parsers.id"))
#     parser = relationship("Parser", back_populates="clips")
#
#
# class Parser(Base):
#     __tablename__ = "parsers"
#
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True)
#     cat = Column(String, index=True)
#     subcat = Column(String, index=True)
#
#     clips = relationship("Clip", back_populates="parser")
#
#
# class VideoParser(Base):
#     __tablename__ = "videoparsers"
#
#     id = Column(Integer, primary_key=True, index=True)
#     video_id = Column(Integer, ForeignKey("videos.id"))
#     parser_id = Column(Integer, ForeignKey("parsers.id"))

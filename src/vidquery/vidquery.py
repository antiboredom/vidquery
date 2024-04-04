import importlib
import pkgutil
import os
import hashlib
from typing import Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.sql import text
from moviepy.editor import VideoFileClip
from .models import Video, Parser, Clip, VideoParser, Base
from .searchparser import parse_query
from . import parsers


DB_NAME = os.environ.get("VIDQUERYDB", "vidquery.db")
DEBUG = True if os.environ.get("VIDQUERYDEBUG") else False
SQLALCHEMY_DATABASE_URL = f"sqlite:///./{DB_NAME}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=DEBUG,
)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def iter_namespace(ns_pkg) -> Iterator[pkgutil.ModuleInfo]:
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


def make_hash(filename: str) -> str:
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, "rb", buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()


def get_video(video_id: int) -> Video | None:
    with SessionLocal() as s:
        video = s.query(Video).filter(Video.id == video_id).one_or_none()
    return video


def get_videos() -> list[Video]:
    with SessionLocal() as s:
        videos = s.query(Video).all()

    return videos


def get_video_parsers():
    with SessionLocal() as s:
        parsers = s.execute(
            text(
                "SELECT DISTINCT clips.video_id, clips.parser_id, parsers.name, parsers.cat, parsers.subcat FROM clips LEFT JOIN parsers ON parsers.id=clips.parser_id;"
            )
        ).all()
        return parsers


def get_or_make_video(path: str) -> Video | None:
    abspath = os.path.abspath(path)
    if not os.path.exists(abspath):
        return None
    hash = make_hash(abspath)

    with SessionLocal() as s:
        video = s.query(Video).filter(Video.hash == hash).one_or_none()

        if video is None:
            try:
                clip = VideoFileClip(abspath)
                duration = clip.duration
                w, h = clip.size
                fps = clip.fps
            except Exception as e:
                print(e)
                w = h = fps = duration = None

            video = Video(
                path=abspath,
                hash=hash,
                fps=fps,
                duration=duration,
                width=w,
                height=h,
            )
            s.add(video)
            s.commit()
            s.refresh(video)

        else:
            video.path = abspath  # type: ignore
            s.commit()
            s.refresh(video)

    return video


def save_clips(
    video_id: int, name: str, cat: str, subcat: str, clips: list[Clip]
) -> None:
    with SessionLocal() as s:
        # create the parser if it doesn't exist
        parser = (
            s.query(Parser)
            .filter(Parser.name == name, Parser.cat == cat, Parser.subcat == subcat)
            .one_or_none()
        )

        if parser is None:
            parser = Parser(name=name, cat=cat, subcat=subcat)
            s.add(parser)
            s.commit()
            s.refresh(parser)

        # create the video parser if it doesn't exist
        video_parser = (
            s.query(VideoParser)
            .filter(
                VideoParser.video_id == video_id, VideoParser.parser_id == parser.id
            )
            .one_or_none()
        )
        if not video_parser:
            video_parser = VideoParser(video_id=video_id, parser_id=parser.id)
            s.add(video_parser)
            s.commit()

        # save the clips
        for clip in clips:
            clip.video_id = video_id
            clip.parser_id = parser.id

        s.bulk_save_objects(clips)
        s.commit()


def query_clips(videos: list[str | int], query: str) -> list[Clip]:
    query_data = parse_query(query)
    if query_data is None:
        return []

    results = []

    video_ids = [v for v in videos if isinstance(v, int)]
    video_paths = [v for v in videos if isinstance(v, str)]

    parsertypes = get_parser_types()

    def convert_to_sql(query_structure):
        if isinstance(query_structure, list):
            left = convert_to_sql(query_structure[0])
            operator = query_structure[1]
            right = convert_to_sql(query_structure[2])

            return f"({left} {operator} {right})"

        elif isinstance(query_structure, dict):
            table = query_structure["table"]
            table_id = parsertypes.get(table, -1)
            q = query_structure["q"]
            return f"(clips.parser_id={table_id} AND clips.content REGEXP '{q}')"

        else:
            return query_structure

    sql_query = convert_to_sql(query_data)

    with SessionLocal() as s:
        if len(video_paths) > 0:
            ids = (
                s.query(Video)
                .with_entities(Video.id)
                .filter(Video.path.in_(video_paths))
                .all()
            )
            video_ids += [i[0] for i in ids]
        stmt = s.query(Clip).where(text(sql_query))
        if len(video_ids) > 0:
            stmt = stmt.filter(Clip.video_id.in_(video_ids))
        stmt = stmt.options(joinedload(Clip.video))
        results = list(stmt.all())

    return results


def get_parser_types():
    with SessionLocal() as s:
        parser_types = s.query(Parser).all()
    out = {}
    for p in parser_types:
        out[p.name] = p.id
        out[p.cat] = p.id
        out[p.subcat] = p.id
    return out


def get_installed_parsers() -> dict:
    out = {}

    discovered_parsers = [
        importlib.import_module(name)
        for _, name, _ in pkgutil.iter_modules()
        if name.startswith("vidquery_parser_")
    ]

    default_parsers = [
        importlib.import_module(name) for _, name, _ in iter_namespace(parsers)
    ]

    all_parsers = default_parsers + discovered_parsers

    for p in all_parsers:
        if "PARSER_NAME" not in dir(p):
            continue
        if "process" not in dir(p):
            continue

        out[p.PARSER_NAME] = {
            "module": p,
            "name": p.PARSER_NAME,
            "long_name": p.PARSER_LONG_NAME,
            "description": p.PARSER_DESCRIPTION,
            "cat": p.PARSER_CAT,
            "subcats": p.PARSER_SUBCATS,
        }

    return out


def analyze(parser_name: str, videopaths: list[str]) -> None:
    for vidpath in videopaths:
        vid = get_or_make_video(vidpath)
        if vid:
            results = all_parsers[parser_name]["module"].process(vidpath)
            print(results)
            for name, cat, subcat, clips in results:
                save_clips(vid.id, name, cat, subcat, clips)


def search(query: str, videos=[]) -> list[Clip]:
    res = query_clips(videos, query)
    return res


all_parsers = get_installed_parsers()

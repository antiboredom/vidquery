from moviepy.editor import VideoFileClip

# from transformers import pipeline
from PIL import Image
from ..models import Clip
from ..vidquery import get_scenes

PARSER_NAME = "caption"
PARSER_LONG_NAME = "Image Captioning"
PARSER_CAT = "image-to-text"
PARSER_SUBCATS = ["blip_caption"]
PARSER_DESCRIPTION = "Creates captions for scenes."

PARSER_OPTIONS = [
    {
        "name": "device",
        "default": "cpu",
        "values": ["mps", "cpu", "gpu"],
        "type": "str",
    },
    {
        "name": "model",
        "default": "Salesforce/blip-image-captioning-base",
        "type": "str",
    },
]

captioner = None
pipeline = None


def make_config():
    config = {}
    for o in PARSER_OPTIONS:
        config[o["name"]] = o["default"]
    return config


def process(video, options={}):
    options = {**make_config(), **options}
    global captioner, pipeline

    if pipeline is None:
        from transformers import pipeline

    if captioner is None:
        captioner = pipeline(
            "image-to-text", model=options["model"], device=options["device"]
        )

    vidclip = VideoFileClip(video)

    scenes = get_scenes(video)

    out = []

    # go through every scene in the video
    for i, scene in enumerate(scenes):
        start_time = scene.start
        end_time = scene.end

        frame = vidclip.get_frame(start_time)
        img = Image.fromarray(frame)
        results = captioner(img)
        caption = results[0]["generated_text"]

        clip = Clip(content=caption, start=start_time, end=end_time)

        out.append(clip)

    return [(PARSER_NAME, PARSER_CAT, PARSER_SUBCATS[0], out)]

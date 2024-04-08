from moviepy.editor import VideoFileClip

PARSER_NAME = "face_recognition"
PARSER_LONG_NAME = "Face Recognition"
PARSER_CAT = "face-recognition"
PARSER_SUBCATS = ["face_recognition"]
PARSER_DESCRIPTION = "Recognizes faces in videos."

PARSER_OPTIONS = [
    {
        "name": "input_images",
        "default": "[]",
        "type": "list[tuple]",
    },
]


def f_to_s(f, fps):
    return f / fps


def make_config():
    config = {}
    for o in PARSER_OPTIONS:
        config[o["name"]] = o["default"]
    return config


# def process(video, options={}):
#     options = {**make_config(), **options}
#     input_images = options["input_images"]

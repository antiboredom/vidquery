from scenedetect import ContentDetector, detect
from ..models import Clip

PARSER_NAME = "scenedetect"
PARSER_LONG_NAME = "Shot Detection"
PARSER_DESCRIPTION = "Detects shots in a video using scenedetect."
PARSER_CAT = "shots"
PARSER_SUBCATS = ["shot_detection"]


def process(video, options={}):
    """returns a shot list and saves the list as a file"""

    shots = []

    scene_list = detect(video, ContentDetector())

    for i, shot in enumerate(scene_list):
        shots.append(
            Clip(
                start=shot[0].get_seconds(),
                end=shot[1].get_seconds(),
                content=f"shot {i+1}",
            )
        )

    return [(PARSER_NAME, PARSER_CAT, "shot_detection", shots)]

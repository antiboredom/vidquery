import os
from subprocess import run
import webview
from . import vidquery


class Api:
    def log(self, value):
        print(value)

    def listvideos(self):
        videos = vidquery.get_videos()
        return [{"path": v.path} for v in videos]

    def query(self, videos, q):
        results = vidquery.query_clips(videos, q)
        return [
            {"path": r.video.path, "start": r.start, "end": r.end, "content": r.content}
            for r in results
        ]

    def previewMPV(self, clips):
        lines = [f"{c['path']},{c['start']},{c['end']-c['start']}" for c in clips]
        edl = "edl://" + ";".join(lines)

        run(["mpv", edl])


def gui():
    webview.settings["ALLOW_FILE_URLS"] = True

    entry = "file://" + os.path.abspath("src/vidquery/html/index.html")

    webview.create_window(
        "Vidquery",
        url=entry,
        js_api=Api(),
    )

    webview.start(debug=True)

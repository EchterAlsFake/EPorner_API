import re
import json
from selectolax.lexbor import LexborHTMLParser


# ROOT URLs
ROOT_URL = "https://www.eporner.com/"
PORNSTAR = "https://www.eporner.com/pornstar/"

# API Calls
API_SEARCH = "api/v2/video/search/"
API_VIDEO_ID = "api/v2/video/id/"

headers = {
    "Referer": "https://www.eporner.com/"
}


def extractor(content: str) -> list[str]:
    video_urls = []
    lexbor = LexborHTMLParser(content)
    divs = lexbor.css("div.mb.hdy")
    for div in divs:
        a_tag = div.css_first("a")
        url = f"https://www.eporner.com{a_tag.attributes.get("href")}"
        video_urls.append(url)

    return video_urls


def extractor_json(content: str) -> list[str]:
    video_urls = []
    stuff = json.loads(content)

    for video_ in stuff.get("videos", []):  # Don't know why this works lmao
        video_urls.append(video_["url"])

    return video_urls

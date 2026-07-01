import re
from selectolax.lexbor import LexborHTMLParser


# ROOT URLs
ROOT_URL = "https://www.eporner.com/"
PORNSTAR = "https://www.eporner.com/pornstar/"

# API Calls
API_V2 = "api/v2/"
API_SEARCH = "api/v2/video/search/"
API_VIDEO_ID = "api/v2/video/id/"

# REGEXES
REGEX_ID = re.compile("https://www.eporner.com/video-(.*?)/")
REGEX_ID_ALTERNATE = re.compile("hd-porn/(.*?)/")

headers = {
    "Referer": "https://www.eporner.com/"
}


def extractor(content: str):
    video_urls = []
    lexbor = LexborHTMLParser(content)
    divs = lexbor.css("div.mb.hdy")
    for div in divs:
        a_tag = div.css_first("a")
        url = f"https://www.eporner.com{a_tag.attributes.get("href")}"
        video_urls.append(url)

    return video_urls

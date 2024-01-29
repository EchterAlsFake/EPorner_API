import re

# ROOT URLs
ROOT_URL = "https://eporner.com/"


# API Calls
API_V2 = "api/v2/"
API_SEARCH = "api/v2/video/search/"
API_VIDEO_ID = "api/v2/video/id/"

# REGEXES
REGEX_ID = re.compile("https://www.eporner.com/video-(.*?)/")
REGEX_HTML_JSON = re.compile(r'<script type="application/ld\+json">\s*(\{.*?})\s*</script>')
REGEX_VIDEO_UPLOADER = re.compile(r'title="Uploader">(.*?)</a>')
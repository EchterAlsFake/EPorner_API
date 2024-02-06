import re

# ROOT URLs
ROOT_URL = "https://eporner.com/"


# API Calls
API_V2 = "api/v2/"
API_SEARCH = "api/v2/video/search/"
API_VIDEO_ID = "api/v2/video/id/"

# REGEXES
REGEX_ID = re.compile("https://www.eporner.com/video-(.*?)/")
REGEX_ID_ALTERNATE = re.compile("hd-porn/(.*?)/")
REGEX_HTML_JSON = re.compile(r'<script type="application/ld\+json">\s*(\{.*?})\s*</script>')
REGEX_VIDEO_UPLOADER = re.compile(r'title="Uploader">(.*?)</a>')
REGEX_VIDEO_PORNSTAR = re.compile('<a href="/pornstar/(.*?)/">')
REGEX_VIDEO_LIKES = re.compile(r'<div class="likeup" onclick="EP\.video\.postVote\(\d+, [01], \'video\'\);"><i>\d+</i><small>(.*?)</small></div>')
REGEX_VIDEO_DISLIKES = re.compile(r'<div class="likedown" onclick="EP\.video\.postVote\(\d+, [01], \'video\'\);"><i>\d+</i><small>(\d+)</small></div>')

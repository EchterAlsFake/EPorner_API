import re

# ROOT URLs
ROOT_URL = "https://eporner.com/"
PORNSTAR = "https://eporner.com/pornstar/"

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
REGEX_VIDEO_THUMBNAILS = re.compile(r'poster="([^"]+\.jpg)"')
REGEX_SCRAPE_VIDEO_URLS = re.compile(r'class="mbcontent">[^<]*<a href="([^"]+)"')

REGEX_PORNSTAR_SUBSCRIBERS = re.compile(r'<small>(.*?)</small>')
REGEX_PORNSTAR_NAME = re.compile(r'<h1 >(.*?)</h1>')
REGEX_PORNSTAR_VIDEO_AMOUNT = re.compile(r'Videos<span>(.*?)</span></a>')
REGEX_PORNSTAR_PHOTOS_AMOUNT = re.compile(r'Photos<span>(.*?)</span></a>')
REGEX_PORNSTAR_RANK = re.compile(r'<div>Rank:<span>(.*?)</span></div>')
REGEX_PORNSTAR_PROFILE_VIEWS = re.compile(r'<div>Profile views:<span>(.*?)</span></div>')
REGEX_PORNSTAR_VIDEO_VIEWS = re.compile(r'<div>Video views:<span>(.*?)</span></div>')
REGEX_PORNSTAR_PHOTO_VIEWS = re.compile(r'<div>Photo views:<span>(.*?)</span></div>')
REGEX_PORNSTAR_COUNTRY = re.compile(r'<li><span>Country:</span><div class="cllnumber">(.*?)</div></li>')
REGEX_PORNSTAR_AGE = re.compile(r'<li><span>Age:</span><div class="cllnumber">(.*?)</div></li>')
REGEX_PORNSTAR_ETHNICITY = re.compile(r'<li><span>Ethnicity:</span><div class="cllnumber">(.*?)</div></li>')
REGEX_PORNSTAR_EYE_COLOR = re.compile(r'<li><span>Eye:</span><div class="cllnumber">(.*?)</div></li>')
REGEX_PORNSTAR_HAIR_COLOR = re.compile(r'<li><span>Hair:</span><div class="cllnumber">(.*?)</div></li>')
REGEX_PORNSTAR_HEIGHT = re.compile(r'<li><span>Height:</span><div class="cllnumber">(.*?)</div></li>')
REGEX_PORNSTAR_WEIGHT = re.compile(r'<li><span>Weight:</span><div class="cllnumber">(.*?)</div></li>')
REGEX_PORNSTAR_CUP = re.compile(r'<li><span>Cup:</span><div class="cllnumber">(.*?)</div></li>')
REGEX_PORNSTAR_MEASUREMENTS = re.compile(r'<li><span>Measurements:</span><div class="cllnumber">(.*?)</div></li>')
REGEX_PORNSTAR_ALIASES = re.compile(r'<ul class="psbioaliases">(.*?)</ul>')
REGEX_PORNSTAR_BIOGRAPHY = re.compile(r'<div class="psscrol"><p>(.*?)</p></div>')
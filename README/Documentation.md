# EPorner Documentation

> - Version 1.3
> - Author: Johannes Habel
> - Copryight (C) 2024
> - License: GPL 3
> - Dependencies: requests, lxml, bs4

# Important Notice
The ToS of Eporner.com clearly say, that using scrapers / bots isn't allowed.
<br>This API uses primarily the official Webmasters API which is in compliance to the ToS.

<br>However, there are more features, which can be enabled using the function parameters.
<br> The function parameter is called `enable_html_scraping`. This parameter is by default
<br> set to `False`. However, you can set it to `True` to enable all features.

If you are using this you may face legal actions, so it's at your own risk!

# Table of Contents

- [Importing the API](#importing-the-api)
- [The Video Object](#video-object)
    - [Video Information](#video-information)
    - [Download a Video](#downloading-a-video)
    - [Custom Callback](#custom-callback)
- [Searching for Videos](#searching-for-videos)
- [Locals](#locals)
    - [Quality](#quality)
    - [Encoding](#encoding)

- [Sorting](#sorting)
    - [Order](#order)
    - [Gay](#gay)
    - [Low Quality](#lowquality)

# Importing the API

```python
from eporner_api.eporner_api import Client, Quality
from eporner_api.modules.errors import *  # These are the exceptions
from eporner_api.modules.sorting import *  # These are sorting used for searching
```


## Video Object

The video object has the following attributes:

```python
from eporner_api.eporner_api import Client, Quality, Encoding

client = Client()
video = client.get_video("<video_url>", enable_html_scraping=False)
"""
Set Enable HTML Scraping to True, if you need more information.
Downloading Videos is only possible if you enabled HTML Scraping!
"""

# Now you access video attributes like

print(video.title)
print(video.length_seconds)

# etc...

# Downloading a Video (HTML Scraping needs to be enabled!)

video.download_video(quality=Quality.BEST,
                    output_path="./", mode=Encoding.mp4_h264)

```
## Video Information

> Webmasters
> - 
> - Video ID
> - Tags
> - Title
> - Views
> - Rate
> - Publish Date
> - Length (Seconds)
> - Length (Minutes)
> - Embed URL (to embed the video in a website)
> - Thumbnails
>
> HTML Content
> -
> - Bitrate
> - Source video URL (you probably never need this)
> - Rating
> - Rating Count

### Functions
- direct_download_link() # Returns the direct download URL
- download_video()

### Downloading a Video

> Please See [Locals](#locals)

You can download a video by using `video.downlod()`

> Arguments:
> 
> - quality : must be a [Quality](#quality) object
> - output_path : must be a string for an output location
> - mode : must be an [Encoding](#encoding) object

#### Custom Callback

If you want to use a custom callback function you can do so, by specifying your function
in the `callback` argument.

Your function needs to take the arguments `pos` and `total`

- pos: The current progress
- total: The total filesize


## Searching for Videos

You can search videos using 

```python
from eporner_api.eporner_api import Client

client = Client()
videos = client.search_videos(query, etc...)

for video in videos:
    print(video.title)
    # etc...
```

#### Arguments:

- query: The search Query (str)
- page: How many pages to iterate (int)
- per_page: How many videos per page (int)
- sorting_order: [Order](#order) Object
- sorting_gay: [Gay](#gay) Object
- sorting_low_quality: [Low Quality](#lowquality) Object
- enable_html_scraping : [Important Notice](#important-notice)

Returns a [Video](#video-object) Object (as a Generator)




# Locals

## Quality

The Quality object has three types:

- BEST 
- HALF
- WORST

(I think they explain themselves good enough :)

> You can also pass a string instead of the object.

- For Quality.BEST: `best`
- For Quality.HALF: `half`
- For Quality.WORST: `ẁorst`



```python
from eporner_api.modules.locals import Quality

quality = Quality.BEST
quality = Quality.HALF
quality = Quality.WORST 

# or 

quality = "best" # etc...
```


## Encoding

Videos on EPorner are available in AV1 and MP4 (H264) format.
<br>I recommend MP4 (H264)

```python
from eporner_api.modules.locals import Encoding

encoding = Encoding.mp4_h264 # Recommended!
encoding = Encoding.av1
```



# Sorting

The sorting objects are needed for searching.

## Order
- latest 
- longest
- shortest
- top_rated
- most_popular
- top_weekly
- top_monthly
```python
from eporner_api.modules.sorting import Order

order = Order.latest
# etc...
```

## Gay
- exclude_gay_content
- include_gay_content
- only_gay_content

```python
from eporner_api.modules.sorting import Gay

gay = Gay.exclude_gay_content
# etc...
```


## LowQuality
- exclude_low_quality_content
- include_low_quality_content
- only_low_quality_content

```python
from eporner_api.modules.sorting import LowQuality

quality_sorting = LowQuality.exclude_low_quality_content
# etc...
```
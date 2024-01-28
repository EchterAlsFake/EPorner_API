<h1 align="center">EPorner API</h1> 

<div align="center">
    <a href="https://pepy.tech/project/hqporner_api"><img src="https://static.pepy.tech/badge/hqporner_api" alt="Downloads"></a>
    <a href="https://github.com/EchterAlsFake/hqporner_api/workflows/"><img src="https://github.com/EchterAlsFake/hqporner_api/workflows/CodeQL/badge.svg" alt="CodeQL Analysis"/></a>
</div>

# Description

EPorner API is an API for EPorner, which allows you to fetch information from videos using the official V2 API.

# Disclaimer
> Some modules of this API are in violence to the ToS from Eporner.com
 
> See Documentation for details about this!

Copyright Information: I have no intention of stealing copyright protected content or slowing down
a website. Contact me at my E-Mail, and I'll take this Repository immediately offline.


# Quickstart

### Have a look at the [Documentation](https://github.com/EchterAlsFake/hqporner_api/blob/master/README/DOCUMENTATION.md) for more details

- Install the library with `pip install hqporner_api`

# Features
> Webmasters API
> - Information about videos
> - Search for videos
> - Search using filters



```python
from eporner_api.eporner_api import Client, Quality
# Initialize a Client object
client = Client()

# Fetch a video
video_object = client.get_video("<insert_url_here>")  # Can also be a Video ID

# Search for videos
videos = client.search_videos(query="Your query here", ..sortings..) # See Documentation!
for video in videos:
    print(video.title)

# SEE DOCUMENTATION FOR MORE
```

# Changelog
See [Changelog](https://github.com/EchterAlsFake/hqporner_api/blob/master/README/CHANGELOG.md) for more details.

# Contribution
Do you see any issues or having some feature requests? Simply open an Issue or talk
in the discussions.

Pull requests are also welcome, but please avoid bs4 and use regex :) 

# License
Licensed under the LGPLv3 License

Copyright (C) 2023–2024 Johannes Habel

# Support

Leave a star on the repository. That's enough :) 
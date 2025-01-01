<h1 align="center">EPorner API</h1> 

<div align="center">
    <a href="https://pepy.tech/project/Eporner-API"><img src="https://static.pepy.tech/badge/Eporner-API" alt="Downloads"></a>
    <a href="https://github.com/EchterAlsFake/EPorner_API/workflows/"><img src="https://github.com/EchterAlsFake/EPorner_API/workflows/CodeQL/badge.svg" alt="CodeQL Analysis"/></a>
    <a href="https://github.com/EchterAlsFake/EPorner_API/workflows/"><img src="https://github.com/EchterAlsFake/EPorner_API/actions/workflows/tests.yml/badge.svg" alt="API Tests"/></a>
</div>

# Description

EPorner API is an API for EPorner, which allows you to fetch information from videos using the official V2 API.

# Disclaimer
> Some modules of this API are in violation of the ToS of Eporner.com
 
> See Documentation for details about this!

> [!IMPORTANT]
> Copyright Information: I have no intention of stealing copyright protected content or slowing down
> a website. Contact me at my E-Mail, and I'll take this Repository immediately offline. (EchterAlsFake@proton.me)

# Features
> Webmasters API
> - 
> - Information about videos
> - Search for videos
> - Search using filters
> 
> HTML Content
> - 
> - Even more information about videos
> - Downloading videos

More will be coming in the next versions!


# Quickstart

### Have a look at the [Documentation](https://github.com/EchterAlsFake/EPorner_API/blob/master/README/Documentation.md) for more details

## Installation

- Install using `pip`: 
```shell
pip install --upgrade Eporner-API
```

- Or from this repo to get the latest fixes/features:
```shell
pip install --upgrade git+https://github.com/EchterAlsFake/EPorner_API.git
```


```python
from eporner_api import Client
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

> [!NOTE]
> EPorner API can also be used from the command line. Do: eporner_api -h to see the options

# Changelog
See [Changelog](https://github.com/EchterAlsFake/EPorner_API/blob/master/README/Changelog.md) for more details.

# Support (Donations)
I am developing all my projects entirely for free. I do that because I have fun and I don't want
to charge 30€ like other people do.

However, if you find my work useful, please consider donating something. A tiny amount such as 1€
means a lot to me.

Paypal: https://paypal.me/EchterAlsFake
<br>XMR (Monero): `46xL2reuanxZgFxXBBaoagiEJK9c7bL7aiwKNR15neyX2wUsX2QVzkeRMVG2Cro44qLUNYvsP1BQa12KPbNat2ML41nyEeq`

# Contribution
Do you see any issues or having some feature requests? Simply open an Issue or talk
in the discussions.

Pull requests are also welcome.

# License
Licensed under the LGPLv3 License
<br>Copyright (C) 2023–2025 Johannes Habel

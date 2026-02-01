<h1 align="center">EPorner API</h1> 

<div align="center">
    <a href="https://pepy.tech/project/Eporner-API"><img src="https://static.pepy.tech/badge/Eporner-API" alt="Downloads"></a>
    <a href="https://github.com/EchterAlsFake/EPorner_API/workflows/"><img src="https://github.com/EchterAlsFake/EPorner_API/workflows/CodeQL/badge.svg" alt="CodeQL Analysis"/></a>
    <a href="https://echteralsfake.me/ci/eporner_api/badge.svg"><img src="https://echteralsfake.me/ci/EPorner_API/badge.svg" alt="API Tests"/></a>
</div>

# Disclaimer
> [!IMPORTANT]
> This is an unofficial and unaffiliated project. Please read the full disclaimer before use:
> **[DISCLAIMER.md](https://github.com/EchterAlsFake/API_Docs/blob/master/Disclaimer.md)**
>
> By using this project you agree to comply with the target site’s rules, copyright/licensing requirements,
> and applicable laws. Do not use it to bypass access controls or scrape at disruptive rates.

# Features
- Fetch videos + metadata
- Download videos
- Fetch Pornstars
- Search for videos
- Fetch videos by category
- Built-in caching
- Easy interface
- Great type hinting
- Proxy support
- Very customizable

# Supported Platforms
This API has been tested and confirmed working on:

- Windows 11 (x64) 
- macOS Sequoia (x86_64)
- Linux (Arch) (x86_64)
- Android 16 (aarch64)

# Quickstart

### Have a look at the [Documentation](https://github.com/EchterAlsFake/API_Docs/blob/master/Porn_APIs/EPorner.md) for more details

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
<br>XMR (Monero): `42XwGZYbSxpMvhn9eeP4DwMwZV91tQgAm3UQr6Zwb2wzBf5HcuZCHrsVxa4aV2jhP4gLHsWWELxSoNjfnkt4rMfDDwXy9jR`

# Contribution
Do you see any issues or having some feature requests? Simply open an Issue or talk
in the discussions.

Pull requests are also welcome.

# License
Licensed under the LGPLv3 License
<br>Copyright (C) 2023–2026 Johannes Habel

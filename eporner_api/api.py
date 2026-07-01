from __future__ import annotations

import re
import os
import json
import logging
import asyncio
import argparse

from dataclasses import dataclass
from urllib.parse import urljoin
from typing import AsyncGenerator
from functools import cached_property
from curl_cffi import Response, AsyncSession
from selectolax.lexbor import LexborHTMLParser
from base_api.modules.config import RuntimeConfig
from base_api import BaseCore, setup_logger, Helper, DownloadConfigRAW
from base_api.modules.static_functions import normalize_quality_value, choose_quality_from_list, str_to_bool
from base_api.modules.errors import InvalidProxy, BotProtectionDetected, NetworkRequestError, UnknownError, VideoFetchError, PageFetchError, ResourceGone

from eporner_api.modules.errors import (InvalidURL, ProxyError, BotDetection, VideoDisabled, HTML_IS_DISABLED,
                                        NotAvailable, NotFound, NetworkError, UnknownNetworkError, InvalidVideo, DownloadFailed)

from eporner_api.modules.consts import (extractor, REGEX_ID, REGEX_ID_ALTERNATE, ROOT_URL, API_V2, API_SEARCH,
                                        API_VIDEO_ID)
from eporner_api.modules.locals import Encoding, Category
from eporner_api.modules.sorting import Order, LowQuality


async def on_error(url: str, error: Exception, attempt: int) -> bool:
    print(f"URL: {url}, ERROR: {error}, Attempt: {attempt}")

    if isinstance(error, ResourceGone):
        return False

    return True


async def get_html_content(core: BaseCore, url: str, get_json: bool = False) -> str | None | dict:
    # What should I do here?
    try:
        content = await core.fetch(url)
        if isinstance(content, str):
            if get_json:
                return json.loads(content)

            return content

        if isinstance(content, Response):
            if content.status_code == 404:
                raise NotFound(f"Server returned 404 for: {url}")

    except NetworkRequestError as e:
        raise NetworkError(str(e)) from e

    except InvalidProxy as e:
        raise ProxyError(str(e)) from e

    except BotProtectionDetected as e:
        raise BotDetection(str(e)) from e

    except UnknownError as e:
        raise UnknownNetworkError(str(e)) from e


@dataclass(slots=True)
class VideoMetadata:
    video_id: int
    tags: list
    title: str
    views: str
    rate: str
    publish_date: str
    length: str
    length_minutes: str
    embed_url: str
    thumbnail: str
    rating: str
    likes: str
    dislikes: str
    rating_count: str
    uploader: AsyncGenerator[Pornstar, None]
    parsed_urls: dict
    html_content: str # Optional HTML Content for downloading, usually not needed
    bitrate: str



class Video:
    __slots__ = ("metadata", "core")

    def __init__(self, metadata: VideoMetadata, core: BaseCore):
        self.metadata = metadata
        self.core = core


    @property
    def video_id(self) -> str:
        return self.metadata.video_id

    @property
    def tags(self) -> list:
        return self.metadata.tags

    @property
    def title(self) -> str:
        return self.metadata.title

    @property
    def views(self) -> str:
        return self.metadata.views

    @property
    def rate(self) -> str:
        return self.metadata.rate

    @property
    def publish_date(self) -> str:
        return self.metadata.publish_date

    @property
    def length(self) -> str:
        return self.metadata.length

    @property
    def length_minutes(self) -> str:
        return self.metadata.length_minutes

    @property
    def embed_url(self) -> str:
        return self.metadata.embed_url

    @property
    def thumbnail(self) -> str:
        return self.metadata.thumbnail

    @property
    def rating(self) -> str:
        return self.metadata.rating

    @property
    def likes(self) -> str:
        return self.metadata.likes

    @property
    def dislikes(self) -> str:
        return self.metadata.dislikes

    @property
    def rating_count(self) -> str:
        return self.metadata.rating_count

    @property
    def uploader(self) -> str:
        return self.metadata.uploader

    @property
    def parsed_urls(self) -> dict:
        return self.metadata.parsed_urls

    def get_available_qualities(self) -> list[str]:
        # I assume here that the available qualities aren't different per mdoe (hopefully)
        return [k for k, v in self.parsed_urls.items()]

    def get_url_by_quality(self, quality: str | int, mode: Encoding | str) -> str:
        available_qualities = self.get_available_qualities()
        qn = normalize_quality_value(quality)
        quality_to_choose = choose_quality_from_list(available=available_qualities, target=qn)

        for stuff, key in self.parsed_urls.items():
            stuff = stuff.lower().strip("p")
            if str(quality_to_choose) == stuff:
                return stuff.get(mode)

        raise ValueError("Couldn't find a URL to match, please report this!")

    async def download(self, configuration: DownloadConfigRAW, mode: Encoding | str, use_workaround: bool = True):
        quality = configuration.quality
        url = self.get_url_by_quality(quality=quality, mode=mode)

        if not configuration.no_title:
            configuration.path = os.path.join(configuration.path, f"{self.title}.mp4")

        if use_workaround:
            response_redirect_url = await self.core.fetch(self.get_url_by_quality(configuration.quality, mode),
                                            allow_redirects=True, get_response=True) # Sometimes the site trolls me

            url = response_redirect_url.redirect_url

        try:
            await self.core.legacy_download(url=url, configuration=configuration)
            return True

        except Exception as e:
            raise DownloadFailed(str(e))


class VideoBuilder:
    def __init__(self, url: str, core: BaseCore, allow_html: bool = True, html_content: str | None = None):
        self.url = url
        self.core = core
        self.allow_html = allow_html
        self.html_content = html_content
        self.lexbor: LexborHTMLParser | None = None
        self.json_data: dict = None

    def _extract_from_html(self):
        meta = VideoMetadata(
            title=self.title,
            video_id=self.video_id,
            embed_url=self.embed_url,
            thumbnail=self.thumbnail,


        )


    @cached_property
    def json_html(self) -> dict:
        if not self.html_content:
            raise ValueError("You have not allowed html content, please do allow_html = True")

        script = self.lexbor.css_first("script[type='application/ld+json']")
        return json.loads(script.text())

    async def init(self) -> Video:
        url = f"{ROOT_URL}{API_VIDEO_ID}?id={self.video_id}&thumbsize=medium&format=json"
        print(f"Requesting: {url}")
        core = BaseCore()
        content = await get_html_content(url=url, core=core)
        print(f"Content: {content}")
        assert isinstance(content, str)

        self.json_data = json.loads(content)
        print(self.json_data)
        print(await self.parse_video_urls())

        if self.allow_html:
            self.html_content = await get_html_content(core=self.core, url=self.url)
            self.lexbor = LexborHTMLParser(self.html_content)
            print(self.json_html)
        #return await asyncio.to_thread(self._extract_from_html)


    @cached_property
    def video_id(self) -> str:
        return re.search(r'video-([^/]+)', self.url).group(1)

    # The following functions are all related to the webmaster API!

    @cached_property
    def title(self) -> str:
        return self.json_data.get("title")

    @cached_property
    def keywords(self) -> list[str]:
        return self.json_data.get("keywords").split(",")

    @cached_property
    def views(self) -> str:
        return self.json_data.get("views")

    @cached_property
    def rate(self) -> str:
        return self.json_data.get("rate")

    @cached_property
    def publish_date(self) -> str:
        return self.json_data.get("added")

    @cached_property
    def length_seconds(self) -> str:
        return self.json_data.get("length_sec")

    @cached_property
    def length_minutes(self) -> str:
        return self.json_data.get("length_min")

    @cached_property
    def embed_url(self) -> str:
        return self.json_data.get("embed")

    @cached_property
    def thumbnail(self) -> str:
        return self.json_data.get("default_thumb".get("src"))

    @cached_property
    def thumbnails(self) -> list:
        return self.json_data.get("thumbs")

    # The following functions are related to the HTML Code
    @cached_property
    def content_url(self) -> str:
        return self.json_html.get("contentUrl")

    async def parse_video_urls(self) -> dict:
        # Initialize the Lexbor parser
        if not self.html_content:
            self.html_content = await get_html_content(url=self.url, core=self.core)

        assert isinstance(self.html_content, str)
        parser = LexborHTMLParser(self.html_content)

        # Temporary storage to hold raw integer qualities and their corresponding URLs
        raw_data = {}

        # 1. Parse AV1 URLs
        for node in parser.css('span.download-av1 a'):
            href = node.attributes.get('href')
            if href:
                # Extract the resolution number (e.g., '240' from '240p' or '/240/')
                match = re.search(r'(\d+)p', href)
                if match:
                    quality = int(match.group(1))
                    if quality not in raw_data:
                        raw_data[quality] = {}
                    raw_data[quality]['av1'] = f"https://www.eporner.com{href}"

        # 2. Parse H.264 URLs
        for node in parser.css('span.download-h264 a'):
            href = node.attributes.get('href')
            if href:
                match = re.search(r'(\d+)p', href)
                if match:
                    quality = int(match.group(1))
                    if quality not in raw_data:
                        raw_data[quality] = {}
                    raw_data[quality]['h264'] = f"https://www.eporner.com{href}"

        # 3. Sort by quality (worst to best / ascending order) and build the final dict
        sorted_qualities = sorted(raw_data.keys())

        sorted_dictionary = {}
        for q in sorted_qualities:
            sorted_dictionary[f"{q}p"] = {
                "av1": raw_data[q].get("av1"),
                "h264": raw_data[q].get("h264")
            }

        return sorted_dictionary

    @cached_property
    def encoding_format(self) -> str:
        return self.json_html.get("encodingFormat")

    @cached_property
    def is_family_friends(self) -> str:
        return self.json_html.get("isFamilyFriendly")

    @cached_property
    def description(self) -> str:
        return self.json_html.get("description")

    @cached_property
    def rating_value(self) -> str:
        return self.json_html.get("aggregateRating").get("ratingValue")

    @cached_property
    def rating_count(self) -> str:
        return self.json_html.get("aggregateRating").get("ratingCount")

    @cached_property
    def best_rating(self) -> str:
        return self.json_html.get("aggregateRating").get("bestRating")

    @cached_property
    def worst_rating(self) -> str:
        return self.json_html.get("aggregateRating").get("worstRating")

    async def get_authors(self) -> AsyncGenerator[Pornstar, None]:
        actors = self.json_html.get("actor")

        for actor in actors:
            url = actor.get("url")
            yield Pornstar(url=url, core=self.core)



class Pornstar(Helper):
    def __init__(self, url: str, core: BaseCore, enable_html_scraping: bool = False, html_content=None):
        super().__init__(core=core, video_constructor=Video)
        self.core = core
        self.url = url
        self.enable_html_scraping = enable_html_scraping
        self.logger = setup_logger(name="EPorner API - [Pornstar]", log_file=None, level=logging.CRITICAL)
        self.html_content = html_content
        
    async def init(self):
        if not self.html_content:
            self.html_content = await get_html_content(core=self.core, url=self.url)
            assert isinstance(self.html_content, str)

        return self

    def enable_logging(self, log_file: str, level, log_ip: str | None = None, log_port: int | None = None):
        self.logger = setup_logger(name="EPorner API - [Pornstar]", log_file=log_file, level=level, http_ip=log_ip, http_port=log_port)

    async def videos(self, pages: int = 0, videos_concurrency: int | None = None, pages_concurrency: int | None = None,
                     on_video_error: on_error_hint = on_error, on_page_error: on_error_hint = None) -> AsyncGenerator[Video, None]:
        if pages == 0:
            video_amount = str(self.video_amount).replace(",", "")
            pages = round(int(video_amount)) / 37 # One page contains 37 videos

        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
        assert videos_concurrency and pages_concurrency

        pages = round(pages) # Dont ask
        page_urls = [urljoin(f"{self.url}/", str(page)) for page in range(1, pages + 1)]
        async for video in self.iterator(target_page_urls=page_urls, video_link_extractor=extractor, max_page_concurrency=pages_concurrency,
                                 max_video_concurrency=videos_concurrency,
                                         on_video_error=on_video_error, on_page_error=on_page_error):
            if isinstance(video, (VideoFetchError, PageFetchError)):
                self.logger.error(f"Error during iteration: {video}")
                continue
            yield await video.init()

    @cached_property
    def name(self) -> str:
        """Returns the name of the Pornstar"""
        return REGEX_PORNSTAR_NAME.search(self.html_content).group(1)

    @cached_property
    def subscribers(self) -> str:
        """Returns the number of subscribers the pornstar has"""
        return REGEX_PORNSTAR_SUBSCRIBERS.search(self.html_content).group(1).replace("(", "").replace(")", "")

    @cached_property
    def picture(self) ->str:
        """Returns the URL of the pornstar picture"""
        regex_pornstar_picture = re.compile(fr'<img src="(.*?)" alt="{self.name}" >')
        return regex_pornstar_picture.search(self.html_content).group(1)

    @cached_property
    def photos_amount(self) -> str:
        """Returns the number of photos the pornstar has"""
        return REGEX_PORNSTAR_PHOTOS_AMOUNT.search(self.html_content).group(1)

    @cached_property
    def video_amount(self) -> str:
        """Returns the number of videos the pornstar has"""
        return REGEX_PORNSTAR_VIDEO_AMOUNT.search(self.html_content).group(1)

    @cached_property
    def pornstar_rank(self) -> str:
        """Returns the pornstar rank"""
        return REGEX_PORNSTAR_RANK.search(self.html_content).group(1)

    @cached_property
    def profile_views(self) -> str:
        """Returns the number of profile views"""
        return REGEX_PORNSTAR_PROFILE_VIEWS.search(self.html_content).group(1)

    @cached_property
    def video_views(self) -> str:
        """Returns the number of video views"""
        return REGEX_PORNSTAR_VIDEO_VIEWS.search(self.html_content).group(1)

    @cached_property
    def photo_views(self) -> str:
        """Returns the number of photo views"""
        return REGEX_PORNSTAR_PHOTO_VIEWS.search(self.html_content).group(1)

    @cached_property
    def country(self) -> str:
        """Returns the country of the pornstar"""
        return REGEX_PORNSTAR_COUNTRY.search(self.html_content).group(1)

    @cached_property
    def age(self) -> str:
        """Returns the age of the pornstar"""
        return REGEX_PORNSTAR_AGE.search(self.html_content).group(1)

    @cached_property
    def ethnicity(self) -> str:
        """Returns the ethnicity of the pornstar"""
        return REGEX_PORNSTAR_ETHNICITY.search(self.html_content).group(1)

    @cached_property
    def eye_color(self) -> str:
        """Returns the eye color of the pornstar"""
        return REGEX_PORNSTAR_EYE_COLOR.search(self.html_content).group(1)

    @cached_property
    def hair_color(self) -> str:
        """Returns the hair color of the pornstar"""
        return REGEX_PORNSTAR_HAIR_COLOR.search(self.html_content).group(1)

    @cached_property
    def height(self) -> str:
        """Returns the height of the pornstar"""
        return REGEX_PORNSTAR_HEIGHT.search(self.html_content).group(1)

    @cached_property
    def weight(self) -> str:
        """Returns the weight of the pornstar"""
        return REGEX_PORNSTAR_WEIGHT.search(self.html_content).group(1)

    @cached_property
    def cup(self) -> str:
        """Returns the cup size of the pornstar"""
        return REGEX_PORNSTAR_CUP.search(self.html_content).group(1)

    @cached_property
    def measurements(self) -> str:
        """Returns the measurements of the pornstar"""
        return REGEX_PORNSTAR_MEASUREMENTS.search(self.html_content).group(1)

    @cached_property
    def aliases(self) -> list:
        """Returns the aliases of the pornstar"""
        aliases = REGEX_PORNSTAR_ALIASES.search(self.html_content).group(1)
        aliases_filtered = re.findall("<li>(.*?)</li>", aliases)
        return aliases_filtered

    @cached_property
    def biography(self) -> str:
        """Returns the biography of the pornstar"""
        return REGEX_PORNSTAR_BIOGRAPHY.search(self.html_content).group(1)

    def parse_video_urls(html_snippet: str) -> dict:
        # Initialize the Lexbor parser
        parser = LexborHTMLParser(html_snippet)

        # Temporary storage to hold raw integer qualities and their corresponding URLs
        raw_data = {}

        # 1. Parse AV1 URLs
        for node in parser.css('span.download-av1 a'):
            href = node.attributes.get('href')
            if href:
                # Extract the resolution number (e.g., '240' from '240p' or '/240/')
                match = re.search(r'(\d+)p', href)
                if match:
                    quality = int(match.group(1))
                    if quality not in raw_data:
                        raw_data[quality] = {}
                    raw_data[quality]['av1'] = href

        # 2. Parse H.264 URLs
        for node in parser.css('span.download-h264 a'):
            href = node.attributes.get('href')
            if href:
                match = re.search(r'(\d+)p', href)
                if match:
                    quality = int(match.group(1))
                    if quality not in raw_data:
                        raw_data[quality] = {}
                    raw_data[quality]['h264'] = href

        # 3. Sort by quality (worst to best / ascending order) and build the final dict
        sorted_qualities = sorted(raw_data.keys())

        sorted_dictionary = {}
        for q in sorted_qualities:
            sorted_dictionary[f"{q}p"] = {
                "av1": raw_data[q].get("av1"),
                "h264": raw_data[q].get("h264")
            }

        return sorted_dictionary


class Client(Helper):
    def __init__(self, core: BaseCore = BaseCore(RuntimeConfig())):
        super().__init__(core, video_constructor=Video)
        self.core = core
        self.core.initialize_session()
        assert isinstance(self.core.session, AsyncSession)
        self.core.session.headers.update(headers)
        self.logger = setup_logger(name="EPorner API - [Client]", log_file=None, level=logging.CRITICAL)

    def enable_logging(self, log_file: str, level, log_ip: str | None = None, log_port: int | None = None):
        self.logger = setup_logger(name="EPorner API - [Client]", log_file=log_file, level=level, http_ip=log_ip, http_port=log_port)

    async def get_video(self, url: str, enable_html_scraping: bool = True) -> Video:
        """Returns the Video object for a given URL"""
        self.logger.info(f"Returning video object for: {url} HTML Scraping -> {enable_html_scraping}")
        video = Video(url, enable_html_scraping=enable_html_scraping, core=self.core)
        return await video.init()

    async def search_videos(self, query: str, sorting_gay: str | Gay, sorting_order: str | Order,
                      sorting_low_quality: str | LowQuality,
                      page: int, per_page: int, enable_html_scraping: bool = True) -> AsyncGenerator[Video, None]:

        url = f"{ROOT_URL}{API_SEARCH}?query={query}&per_page={per_page}&%page={page}&thumbsize=medium&order={sorting_order}&gay={sorting_gay}&lq={sorting_low_quality}&format=json"
        json_data = await get_html_content(core=self.core, url=url, get_json=True)
        assert isinstance(json_data, dict)

        for video_ in json_data.get("videos", []):  # Don't know why this works lmao
            id_ = video_["url"]
            video = Video(url=id_, core=self.core, enable_html_scraping=enable_html_scraping)
            yield await video.init()

    async def get_videos_by_category(self, category: str | Category,
                               videos_concurrency: int | None = None, pages_concurrency: int | None = None,
                                     on_video_error: on_error_hint = on_error, on_page_error: on_error_hint = None) -> AsyncGenerator[Video, None]:

        page_urls = [f"{ROOT_URL}cat/{category}/{page}" for page in range(1, 100)]

        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
        assert videos_concurrency and pages_concurrency
        async for video in self.iterator(target_page_urls=page_urls, max_video_concurrency=videos_concurrency,
                                 max_page_concurrency=pages_concurrency, video_link_extractor=extractor,
                                         on_video_error=on_video_error, on_page_error=on_page_error):
            if isinstance(video, (VideoFetchError, PageFetchError)):
                self.logger.error(f"Error during iteration: {video}")
                continue
            yield await video.init()


    async def get_pornstar(self, url: str, enable_html_scraping: bool = True) -> Pornstar:
        self.logger.info(f"Returning Pornstar object for: {url} HTML Scraping -> {enable_html_scraping}")
        pornstar = Pornstar(url=url, enable_html_scraping=enable_html_scraping, core=self.core)
        return await pornstar.init()


async def run_main():
    parser = argparse.ArgumentParser(description="API Command Line Interface")
    parser.add_argument("--download", metavar="URL (str)", type=str, help="URL to download from")
    parser.add_argument("--quality", metavar="best,half,worst", type=str, help="The video quality (best,half,worst)",
                        required=True)
    parser.add_argument("--file", metavar="Source to .txt file", type=str,
                        help="(Optional) Specify a file with URLs (separated with new lines)")
    parser.add_argument("--output", metavar="Output directory", type=str, help="The output path (with filename)",
                        required=True)
    parser.add_argument("--no-title", metavar="True,False", type=str,
                        help="Whether to apply video title automatically to output path or not", required=True)

    args = parser.parse_args()
    no_title = str_to_bool(args.no_title)

    if args.download:
        client = Client()
        video = await client.get_video(args.download, enable_html_scraping=True)
        await video.download(quality=args.quality, path=args.output, no_title=no_title)

    if args.file:
        videos = []
        client = Client()

        with open(args.file, "r") as file:
            content = file.read().splitlines()

        for url in content:
            videos.append(await client.get_video(url, enable_html_scraping=True))

        for video in videos:
            await video.download(quality=args.quality, path=args.output, no_title=no_title)

async def test():
    core = BaseCore()
    video = await VideoBuilder(url="https://www.eporner.com/video-dJjeWjEE8cJ/mih-ninfetinha-public-dap/", core=core, allow_html=True).init()
    print(video.json_html)



def main():
    asyncio.run(test())

if __name__ == "__main__":
    main()

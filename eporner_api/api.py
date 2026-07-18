from __future__ import annotations

import re
import os
import copy
import json
import logging
import asyncio
import argparse

from dataclasses import dataclass, fields
from urllib.parse import urljoin
from typing import AsyncGenerator
from curl_cffi import Response, AsyncSession
from selectolax.lexbor import LexborHTMLParser
from base_api.modules.config import RuntimeConfig
from base_api import BaseCore, BaseMedia, Helper, DownloadConfigRAW, ScrapeResult
from base_api.modules.static_functions import normalize_quality_value, choose_quality_from_list, str_to_bool
from base_api.modules.errors import InvalidProxy, BotProtectionDetected, NetworkRequestError, UnknownError, ResourceGone

from eporner_api.modules.errors import (ProxyError, BotDetection, NotFound, NetworkError, UnknownNetworkError,
                                        DownloadFailed)

from eporner_api.modules.consts import (extractor, ROOT_URL, API_SEARCH,
                                        API_VIDEO_ID, headers, extractor_json)
from eporner_api.modules.type_hints import on_error_hint
from eporner_api.modules.locals import Encoding, Category
from eporner_api.modules.sorting import Order, LowQuality, Gay

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


async def on_error(url: str, error: Exception, attempt: int) -> bool:
    logger.error(f"URL: {url}, ERROR: {error}, Attempt: {attempt}")

    if isinstance(error, ResourceGone):
        return False

    return True


async def get_html_content(core: BaseCore, url: str, get_json: bool = False) -> str | None | dict:
    # What should I do here?
    try:
        content = await core.fetch(url)
        if isinstance(content, str):
            if get_json:
                return json.loads(content, strict=False)

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


@dataclass(slots=True, kw_only=True)
class Video(BaseMedia):
    url: str
    core: BaseCore
    video_id: str | None = None
    keywords: list | None = None
    title: str | None = None
    views: int | None = None
    rate: str | None = None
    publish_date: str | None = None
    length_seconds: str | None = None
    length_minutes: str | None = None
    embed_url: str | None = None
    thumbnail: str | None = None
    rating_value: str | None = None
    rating_count: str | None = None
    parsed_urls: dict | None = None
    description: str | None = None
    encoding_format: str | None = None
    is_family_friendly: str | None = None
    thumbnails: list[str] | None = None
    content_url: str | None = None
    best_rating: str | None = None
    worst_rating: str | None = None
    authors_urls: list[str] | None = None

    async def _perform_load(self, api: bool, html: bool, anything_else: bool):
        self.video_id = None
        match = re.search(r'video-([^/]+)', self.url)
        if match:
            self.video_id = match.group(1)

        match_2 = re.search(r'hd-porn/(.*?)/', self.url)
        if match_2:
            self.video_id = match_2.group(1)

        setattr(self, "video_id", self.video_id)
        tasks = []
        keys = []

        if api:
            tasks.append(self._fetch_api())
            keys.append("api")

        if html:
            tasks.append(self._fetch_html())
            keys.append("html")

        results = {}
        if tasks:
            payloads = await asyncio.gather(*tasks)
            results = dict(zip(keys, payloads))

        combined_data = {}
        if "html" in results and results["html"]:
            combined_data.update(results["html"])

        if "api" in results and results["api"]:
            combined_data.update(results["api"])

        allowed_fields = {field.name for field in fields(self)}
        for key, value in combined_data.items():
            if key in allowed_fields:
                setattr(self, key, value)

    async def _fetch_api(self):
        url = f"{ROOT_URL}{API_VIDEO_ID}?id={self.video_id}&thumbsize=medium&format=json"
        json_content = await get_html_content(core=self.core, url=url)
        assert isinstance(json_content, str)
        return await asyncio.to_thread(self._extract_api, json_content)


    async def _fetch_html(self):
        html_content = await get_html_content(core=self.core, url=self.url)
        assert isinstance(html_content, str)
        return await asyncio.to_thread(self._extract_html, html_content)

    @staticmethod
    def _extract_api(json_content: str) -> dict:
        json_data = json.loads(json_content, strict=False)
        title = json_data.get("title", "")
        keywords = json_data.get("keywords", "").split(",")
        views = json_data.get("views", None)
        rate = json_data.get("rate", "")
        publish_date = json_data.get("added", "")
        length_seconds = json_data.get("length_sec", "")
        length_minutes = json_data.get("length_min", "")
        embed_url = json_data.get("embed", "")
        thumbnail = json_data.get("default_thumb", {}).get("src", "")
        thumbnails = json_data.get("thumbs", [])

        return {
            "title": title,
            "keywords": keywords,
            "views": views,
            "rate": rate,
            "publish_date": publish_date,
            "length_seconds": length_seconds,
            "length_minutes": length_minutes,
            "embed_url": embed_url,
            "thumbnail": thumbnail,
            "thumbnails": thumbnails
        }

    @staticmethod
    def _extract_html(html_content: str) -> dict:
        lexbor = LexborHTMLParser(html_content)

        script = lexbor.css_first("script[type='application/ld+json']")
        json_html = json.loads(script.text(), strict=False)

        encoding_format = json_html.get("encodingFormat", "")
        is_family_friendly = json_html.get("isFamilyFriendly", "")
        description = json_html.get("description", "")
        rating_value = json_html.get("aggregateRating", {}).get("ratingValue", "")
        rating_count = json_html.get("aggregateRating", {}).get("ratingCount", "")
        best_rating = json_html.get("aggregateRating", {}).get("bestRating", "")
        worst_rating = json_html.get("aggregateRating", {}).get("worstRating", "")
        content_url = json_html.get("contentUrl", "")

        authors_urls = []
        actors = json_html.get("actor", {})
        for actor in actors:
            authors_urls.append(actor.get("url"))

        # Temporary storage to hold raw integer qualities and their corresponding URLs
        raw_data = {}

        # 1. Parse AV1 URLs
        for node in lexbor.css('span.download-av1 a'):
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
        for node in lexbor.css('span.download-h264 a'):
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

        parsed_urls = {}
        for q in sorted_qualities:
            parsed_urls[f"{q}p"] = {
                "av1": raw_data[q].get("av1"),
                "h264": raw_data[q].get("h264")
            }

        return {
            "encoding_format": encoding_format,
            "is_family_friendly": is_family_friendly,
            "description": description,
            "rating_value": rating_value,
            "best_rating": best_rating,
            "worst_rating": worst_rating,
            "rating_count": rating_count,
            "content_url": content_url,
            "parsed_urls": parsed_urls,
            "authors_urls": authors_urls
        }

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
                return key.get(mode)

        raise ValueError("Couldn't find a URL to match, please report this!")

    async def download(self, configuration: DownloadConfigRAW, mode: Encoding | str, use_workaround: bool = True):
        config = copy.deepcopy(configuration)
        quality = config.quality
        url = self.get_url_by_quality(quality=quality, mode=mode)

        if not config.no_title:
            config.path = os.path.join(config.path, f"{self.title}.mp4")

        try:
            await self.core.legacy_download(url=url, configuration=config)
            return True

        except Exception as e:
            raise DownloadFailed(str(e))

    async def get_authors(self, load_html: bool = True) -> AsyncGenerator[Pornstar, None]:
        actors = self.authors_urls
        for url in actors:
            star = Pornstar(url=url, core=self.core)
            yield await star.load(html=load_html)


@dataclass(kw_only=True, slots=True)
class Pornstar(BaseMedia):
    url: str
    core: BaseCore
    subscribers: str | None = None
    picture: str | None = None
    name: str | None = None
    photos_amount: str | None = None
    video_amount: str | None = None
    pornstar_rank: str | None = None
    profile_views: str | None = None
    video_views: str | None = None
    photo_views: str | None = None
    country: str | None = None
    age: str | None = None
    ethnicity: str | None = None
    eye_color: str | None = None
    hair_color: str | None = None
    height: str | None = None
    weight: str | None = None
    cup: str | None = None
    measurements: str | None = None
    biography: str | None = None
    aliases: list | None = None

    async def _perform_load(self, api: bool, html: bool, anything_else: bool):
        if html:
            await asyncio.gather(self._fetch_html())

    async def _fetch_html(self):
        html_content = await get_html_content(url=self.url, core=self.core)
        assert isinstance(html_content, str)
        data: dict = await asyncio.to_thread(self._extract_html, html_content)
        allowed_fields = {field.name for field in fields(self)}
        for key, value in data.items():
            if key in allowed_fields:
                setattr(self, key, value)

    @staticmethod
    def _extract_html(html_content: str) -> dict:
        lexbor = LexborHTMLParser(html_content)

        name = lexbor.css_first("h1").text(strip=True)
        subscribers = lexbor.css_first("div#resppssubcnt").text(strip=True)
        picture = lexbor.css_first("div.psImgOuter").css_first("img").attributes.get("src")
        photos_amount = lexbor.css_first("div.ps1a").css_first("a").css_first("span").text(strip=True)
        video_amount = lexbor.css_first("div.ps1a").css("a")[1].css_first("span").text(strip=True)
        pornstar_rank = lexbor.css_first("div.psbio.ps3").css_first("div").css_first("span").text(strip=True)
        profile_views = lexbor.css_first("div.psbio.ps3 > div:nth-child(2) > span").text(strip=True)
        video_views = lexbor.css_first("div.psbio.ps3").css("div")[2].css_first("span").text(strip=True)
        photo_views = lexbor.css_first("div.psbio.ps3").css("div")[3].css_first("span").text(strip=True)
        country = lexbor.css_first("div.psbio.ps2").css_first("div.cllnumber").text(strip=True)
        age = lexbor.css_first("div.psbio.ps2").css("div.cllnumber")[1].text(strip=True)
        ethnicity = lexbor.css_first("div.psbio.ps2").css("div.cllnumber")[2].text(strip=True)
        eye_color = lexbor.css_first("div.psbio.ps2").css("div.cllnumber")[3].text(strip=True)
        hair_color = lexbor.css_first("div.psbio.ps2").css("div.cllnumber")[4].text(strip=True)
        height = lexbor.css_first("div.psbio.ps2").css("div.cllnumber")[5].text(strip=True)
        weight = lexbor.css_first("div.psbio.ps2").css("div.cllnumber")[6].text(strip=True)
        cup = lexbor.css_first("div.psbio.ps2").css("div.cllnumber")[7].text(strip=True)
        measurements = lexbor.css_first("div.psbio.ps2").css("div.cllnumber")[8].text(strip=True)

        biography = lexbor.css_first("div.psscrol > p").text(strip=True)
        stuff = lexbor.css_first("div.psbio.ps4")
        aliases = [tag.text(strip=True) for tag in stuff.css("li")]

        return {
            "name": name,
            "subscribers": subscribers,
            "picture": picture,
            "photos_amount": photos_amount,
            "video_amount": video_amount,
            "pornstar_rank": pornstar_rank,
            "profile_views": profile_views,
            "video_views": video_views,
            "photo_views": photo_views,
            "country": country,
            "age": age,
            "ethnicity": ethnicity,
            "eye_color": eye_color,
            "hair_color": hair_color,
            "height": height,
            "weight": weight,
            "cup": cup,
            "measurements": measurements,
            "biography": biography,
            "aliases": aliases,
        }

    async def videos(self, pages: int = 0, videos_concurrency: int | None = None, pages_concurrency: int | None = None,
                         on_video_error: on_error_hint = on_error, on_page_error: on_error_hint = None,
                     keep_original_order: bool = False, load_html: bool = False, load_api: bool = False) -> AsyncGenerator[ScrapeResult, None]:
            if pages == 0:
                video_amount = str(self.video_amount).replace(",", "")
                pages = round(int(video_amount)) / 37 # One page contains 37 videos

            videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
            pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
            assert videos_concurrency and pages_concurrency
            helper = Helper(core=self.core, constructor=Video)
            pages = round(pages) # Dont ask
            url = self.url
            page_urls = [urljoin(f"{url}/", str(page)) for page in range(1, pages + 1)]
            async for scrape_result in helper.iterator(target_page_urls=page_urls, video_link_extractor=extractor, max_page_concurrency=pages_concurrency,
                                     max_video_concurrency=videos_concurrency, keep_original_order=keep_original_order,
                                     fetch_api=load_api, fetch_html=load_html,
                                     on_video_error=on_video_error, on_page_error=on_page_error):
                yield scrape_result


class Client:
    def __init__(self, core: BaseCore = BaseCore(RuntimeConfig())):
        self.core = core
        self.core.initialize_session()
        assert isinstance(self.core.session, AsyncSession)
        self.core.session.headers.update(headers)

    async def get_video(self, url: str, load_html: bool = False, load_api: bool = True) -> Video:
        """Returns the Video object for a given URL"""
        logger.info(f"Returning video object for: {url} HTML Scraping -> {load_html}")
        video = Video(url=url, core=self.core)
        return await video.load(html=load_html, api=load_api)

    async def search_videos(self, query: str, sorting_gay: str | Gay, sorting_order: str | Order,
                        sorting_low_quality: str | LowQuality, per_page: int, load_html: bool = True, pages: int = 2,
                        max_video_concurrency: int = 20,
                        max_page_concurrency: int = 2,
                        on_page_error: on_error_hint = None,
                        on_video_error: on_error_hint = on_error,
                        keep_original_order: bool = False, load_api: bool = False,
                        ) -> AsyncGenerator[ScrapeResult, None]:
        helper = Helper(core=self.core, constructor=Video)
        max_video_concurrency = max_video_concurrency or self.core.configuration.pages_concurrency
        max_page_concurrency = max_page_concurrency or self.core.configuration.pages_concurrency
        assert max_video_concurrency and max_video_concurrency

        page_urls = [f"{ROOT_URL}{API_SEARCH}?query={query}&per_page={per_page}&%page={page}&thumbsize=medium&order={sorting_order}&gay={sorting_gay}&lq={sorting_low_quality}&format=json" for page in range(pages)]
        async for scrape_result in helper.iterator(target_page_urls=page_urls, max_page_concurrency=max_page_concurrency,
                                         max_video_concurrency=max_video_concurrency, on_video_error=on_video_error,
                                         on_page_error=on_page_error, keep_original_order=keep_original_order,
                                         video_link_extractor=extractor_json, fetch_html=load_html, fetch_api=load_api):
            yield scrape_result


    async def get_videos_by_category(self, category: str | Category,
                               videos_concurrency: int | None = None, pages_concurrency: int | None = None,
                                     on_video_error: on_error_hint = on_error, on_page_error: on_error_hint = None,
                                     load_html: bool = False, load_api: bool = False,
                                     keep_original_order: bool = False) -> AsyncGenerator[ScrapeResult, None]:

        page_urls = [f"{ROOT_URL}cat/{category}/{page}" for page in range(1, 100)]

        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
        assert videos_concurrency and pages_concurrency
        helper = Helper(core=self.core, constructor=Video)
        async for scrape_result in helper.iterator(target_page_urls=page_urls, max_video_concurrency=videos_concurrency,
                                 max_page_concurrency=pages_concurrency, video_link_extractor=extractor,
                                 on_video_error=on_video_error, on_page_error=on_page_error,
                                 keep_original_order=keep_original_order, fetch_html=load_html, fetch_api=load_api):
            yield scrape_result


    async def get_pornstar(self, url: str, load_html: bool = True) -> Pornstar:
        logger.info(f"Returning Pornstar object for: {url} HTML Scraping -> {load_html}")
        pornstar = Pornstar(url=url, core=self.core)
        return await pornstar.load(html=load_html)


async def run_main():
    from rich.console import Console
    from rich.panel import Panel
    from rich_argparse import RichHelpFormatter
    
    console = Console()
    console.print(Panel.fit("[bold magenta]EPorner API CLI[/bold magenta]", border_style="cyan"))

    parser = argparse.ArgumentParser(
        description="API Command Line Interface",
        formatter_class=RichHelpFormatter
    )
    parser.add_argument("--download", metavar="URL", type=str, help="URL to download from")
    parser.add_argument("--quality", metavar="best|half|worst", type=str, help="The video quality (best, half, worst)",
                        required=True)
    parser.add_argument("--file", metavar="FILE", type=str,
                        help="(Optional) Specify a file with URLs (separated with new lines)")
    parser.add_argument("--output", metavar="DIR", type=str, help="The output path (with filename)",
                        required=True)
    parser.add_argument("--no-title", metavar="True|False", type=str,
                        help="Whether to apply video title automatically to output path or not", required=True)

    args = parser.parse_args()
    no_title = str_to_bool(args.no_title)
    config = DownloadConfigRAW(quality=args.quality, path=args.output, no_title=no_title)

    if args.download:
        client = Client()
        console.print(f"[cyan]Fetching video information for:[/cyan] [yellow]{args.download}[/yellow]")
        video = await client.get_video(args.download, load_html=True)
        console.print(f"[green]Starting download for:[/green] [bold]{video.title}[/bold]")
        await video.download(config, mode=Encoding.mp4_h264)
        console.print("[bold green]Download complete![/bold green]")

    if args.file:
        client = Client()

        with open(args.file, "r") as file:
            content = [line.strip() for line in file.readlines() if line.strip()]

        console.print(f"[cyan]Fetching information for {len(content)} videos concurrently...[/cyan]")
        
        fetch_tasks = [client.get_video(url, load_html=True) for url in content]
        videos = await asyncio.gather(*fetch_tasks)

        console.print(f"[cyan]Downloading {len(videos)} videos concurrently...[/cyan]")
        
        download_tasks = [video.download(config, mode=Encoding.mp4_h264) for video in videos]
        await asyncio.gather(*download_tasks)
        
        console.print("[bold green]All downloads complete![/bold green]")

def main():
    asyncio.run(run_main())

if __name__ == "__main__":
    main()
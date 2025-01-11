import asyncio
import json
import logging
import argparse
import os.path
import traceback

try:
    from .modules.consts import *
    from .modules.locals import *
    from .modules.errors import *
    from .modules.sorting import *
    from .modules.progressbar import *

except (ModuleNotFoundError, ImportError):
    from modules.consts import *
    from modules.locals import *
    from modules.errors import *
    from modules.sorting import *
    from modules.progressbar import *

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from base_api.base import BaseCore
from typing import Union, List
from functools import cached_property

"""
Copyright (c) 2024 Johannes Habel

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
DISCLAIMER:

Some modules of this project are in violence to the terms of services of EPorner.com
You can read them here: https://www.eporner.com/terms/

You (the user) are responsible for using this API. I am not liable for your actions!

All methods which use the Webmasters API are in compliance with the ToS. Those methods are used by default.
If you still need additional functionalities and information from videos / Eporner.com you can enable the use of 
HTML Content. See the Documentation for more details.
"""

core = BaseCore()
logging.basicConfig(format='%(name)s %(levelname)s %(asctime)s %(message)s', datefmt='%I:%M:%S %p')
logger = logging.getLogger("EPORNER API")
logger.setLevel(logging.DEBUG)

def disable_logging():
    logger.setLevel(logging.CRITICAL)


def extract_json_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    script_tags = soup.find_all('script', {'type': 'application/ld+json'})

    combined_data = {}

    for script in script_tags:
        json_text = script.string.strip()
        try:
            data = json.loads(json_text)

        except json.decoder.JSONDecodeError:
            raise InvalidVideo("""
JSONDecodeError: I need your help to fix this error. Please report the URL you've used on GitHub. Thanks :)""")

        combined_data.update(data)

    cleaned_dictionary =flatten_json(combined_data)
    return cleaned_dictionary


def flatten_json(nested_json, parent_key='', sep='_'):
    """
    Flatten a nested JSON dictionary. Duplicate keys will be overridden.

    :param nested_json: The nested JSON dictionary to be flattened.
    :param parent_key: The base key to use for the flattened keys.
    :param sep: The separator between nested keys.
    :return: A flattened dictionary.
    """
    items = []
    for k, v in nested_json.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class Video:
    def __init__(self, url: str, enable_html_scraping: bool = False, content: str = None, json_data: dict = None,
                html_json_data: dict = None) -> None:
        self.url = url
        self.enable_html = enable_html_scraping
        self.html_content = content
        self.html_json_data = html_json_data
        self.json_data = json_data

    @classmethod
    async def create(cls, url: str, enable_html_scraping: bool = False):
        if enable_html_scraping:
            html_content = await core.fetch(url)
            is_removed = REGEX_VIDEO_DISABLED.findall(html_content)
            for _ in is_removed:
                if _ == "deletedfile":
                    raise VideoDisabled("Video has been removed because of a Copyright claim")

            if str(url).startswith("https://"):
                video_id = REGEX_ID.search(url)
                if video_id:
                    id = video_id.group(1)

                else:
                    video_id = REGEX_ID_ALTERNATE.search(url)
                    id = video_id.group(1)

            data = await core.fetch(f"{ROOT_URL}{API_VIDEO_ID}?id={id}&thumbsize=medium&format=json")
            json_data = json.loads(data)
            html_json_data = extract_json_from_html(html_content)

        else:
            html_content = None
            data = await core.fetch(f"{ROOT_URL}{API_VIDEO_ID}?id={id}&thumbsize=medium&format=json")
            json_data = json.loads(data)
            html_json_data = None

        return cls(url, enable_html_scraping, html_content, json_data, html_json_data)

    @cached_property
    def video_id(self) -> str:
        """
        Extracts the video ID from the video URL
        :return: ID (string)
        """
        if str(self.url).startswith("https://"):
            video_id = REGEX_ID.search(self.url)
            if video_id:
                return video_id.group(1)

            else:
                try:
                    video_id = REGEX_ID_ALTERNATE.search(self.url)
                    return video_id.group(1)

                except Exception:
                    raise InvalidURL("The URL is not valid. Couldn't extract ID!")

        else:
            return self.url  # Assuming this is a video ID (hopefully)

    @cached_property
    def tags(self) -> list:
        tags = []
        tags_data = self.json_data["keywords"]
        tags_data_split = tags_data.split(",")
        for tag in tags_data_split:
            tag = str(tag).replace(" ", "")
            tags.append(tag)

        return tags

    @cached_property
    def title(self) -> str:
        title = self.json_data["title"]
        return title

    @cached_property
    def views(self) -> str:
        views = self.json_data["views"]
        return views

    @cached_property
    def rate(self) -> str:
        rate = self.json_data["rate"]
        return rate

    @cached_property
    def publish_date(self) -> str:
        added = self.json_data["added"]
        return added

    @cached_property
    def length(self) -> str:
        length_sec = self.json_data["length_sec"]
        return length_sec

    @cached_property
    def length_minutes(self) -> str:
        length_min = self.json_data["length_min"]
        return length_min

    @cached_property
    def embed_url(self) -> str:
        embed = self.json_data["embed"]
        return embed

    @cached_property
    def thumbnail(self):
        if self.enable_html:
            return REGEX_VIDEO_THUMBNAILS.search(self.html_content).group(1)

        else:
            return None

    """
    The following methods are using HTML scraping. This is against the ToS from EPorner.com!
    """

    @cached_property
    def bitrate(self) -> str:
        """Return the bitrate of the video? (I don't know)"""
        return self.html_json_data["bitrate"] if self.enable_html else None


    @cached_property
    def source_video_url(self) -> str:
        """
        Returns the .mp4 video location URL

        :return: str
        """
        return self.html_json_data["contentUrl"] if self.enable_html else None


    @cached_property
    def rating(self) -> str:
        """
        Returns the rating value. Highest (best) is 100, least is zero (worst)
        :return: str
        """
        if self.enable_html:
            try:
                return self.html_json_data["aggregateRating_ratingValue"]

            except KeyError:
                raise NotAvailable("No rating available. This isn't an error!")

    @cached_property
    def likes(self) -> str:
        """
        Returns the video likes
        :return: str
        """
        return REGEX_VIDEO_LIKES.search(self.html_content).group(1) if self.enable_html else None

    @cached_property
    def dislikes(self) -> str:
        """
        Returns the video dislikes
        :return:
        """
        return REGEX_VIDEO_DISLIKES.search(self.html_content).group(1) if self.enable_html else None

    @cached_property
    def rating_count(self) -> str:
        """
        Returns how many people have rated the video
        :return: str
        """
        return self.html_json_data["aggregateRating_ratingCount"] if self.enable_html else None

    @cached_property
    def author(self) -> str:
        """
        Returns the Uploader of the Video
        :return: str
        """
        if self.enable_html:
            match = REGEX_VIDEO_UPLOADER.search(self.html_content)
            if match:
                if match.group(1) is None or match.group(1) == "":
                    match = REGEX_VIDEO_PORNSTAR.search(self.html_content)
                    return match.group(1)

                else:
                    return match.group(1)

    def direct_download_link(self, quality, mode) -> str:
        """
        Returns the direct download URL for a given quality
        :param quality: 'best', 'half', 'worst', or a specific resolution like '720p'
        :param mode: The mode to filter links by (e.g., 'video')
        :return: str
        """
        if not self.enable_html:
            raise HTML_IS_DISABLED("HTML content is disabled! See Documentation for more details")

        soup = BeautifulSoup(self.html_content, 'html.parser')
        available_links = []

        # Define the quality preferences in descending order
        quality_preferences = ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p']

        # Search for all <a> tags and collect links for the specified mode
        for a_tag in soup.find_all('a', href=True):
            link_text = a_tag.text.lower()
            href = a_tag['href']
            # Filter links by mode
            if str(mode.lower()) in link_text:
                for preference in quality_preferences:
                    if preference in link_text:
                        available_links.append((preference, href))
                        break

        reversed_links = list(reversed(available_links))

        if quality == "best":
            quality, url = reversed_links[0]

        elif quality == "half":
            index_to_use = round(len(available_links) / 2)
            quality, url = reversed_links[index_to_use]

        elif quality == "worst":
            quality, url = reversed_links[-1]

        else:
            raise "No URLs available? Please report that"

        return urljoin("https://eporner.com", str(url))

    async def download(self, quality, path, callback=None, mode=Encoding.mp4_h264, no_title=False):
        if not self.enable_html:
            raise HTML_IS_DISABLED("HTML content is disabled! See Documentation for more details")

        response_redirect_url = await core.fetch(self.direct_download_link(quality, mode),
                                            allow_redirects=True, get_response=True)

        if no_title is False:
            path = os.path.join(path, f"{self.title}.mp4")

        try:
            await core.legacy_download(url=str(response_redirect_url.url), callback=callback, path=path)
            return True

        except Exception:
            error = traceback.format_exc()
            logger.error(error)
            return False



class Pornstar:
    def __init__(self, url: str, enable_html_scraping: bool = False, content: str = None):
        self.url = url
        self.enable_html_scraping = enable_html_scraping
        self.html_content = content

    @classmethod
    async def create(cls, url, enable_html_scraping=False):
        return cls(url, enable_html_scraping=enable_html_scraping, content = await core.fetch(url))

    async def videos(self, pages: int = 0) -> List[Video]:
        if pages == 0:
            pages = int(self.video_amount) / 37 # One page contains 37 videos

        urls = []
        for page in range(1, pages):
            response = await core.fetch(urljoin(self.url + "/", str(page)))
            extraction = REGEX_SCRAPE_VIDEO_URLS.findall(response)
            for url in extraction:
                url = f"https://www.eporner.com{url}"
                url = url.replace("EPTHBN/", "")
                urls.append(url)

        video_tasks = [asyncio.create_task(Client.get_video(url, enable_html_scraping=self.enable_html_scraping)) for url in urls]
        video_results = await asyncio.gather(*video_tasks)
        return video_results

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


class Client:

    @classmethod
    async def get_video(cls, url: str, enable_html_scraping: bool = False) -> Video:
        """Returns the Video object for a given URL"""
        return await Video.create(url, enable_html_scraping=enable_html_scraping)

    @classmethod
    async def search_videos(cls, query: str, sorting_gay: Union[str, Gay], sorting_order: Union[str, Order],
                      sorting_low_quality: Union[str, LowQuality],
                      page: int, per_page: int, enable_html_scraping: bool = False) -> List[Video]:

        response = await core.fetch(f"{ROOT_URL}{API_SEARCH}?query={query}&per_page={per_page}&%page={page}"
                                f"&thumbsize=medium&order={sorting_order}&gay={sorting_gay}&lq="
                                f"{sorting_low_quality}&format=json")

        json_data = json.loads(response)
        video_urls = []

        for video_ in json_data.get("videos", []):  # Don't know why this works lmao
            video_urls.append(video_["url"])

        video_tasks = [asyncio.create_task(Client.get_video(url=url, enable_html_scraping=enable_html_scraping)) for url
                       in video_urls]
        video_results = await asyncio.gather(*video_tasks)
        return video_results


    @classmethod
    async def get_videos_by_category(cls, category: Union[str, Category], enable_html_scraping: bool = False,
                               pages: int = 1) -> List[Video]:

        video_urls = []

        for page in range(pages):
            response = await core.fetch(f"{ROOT_URL}cat/{category}/{page}")
            extraction = REGEX_SCRAPE_VIDEO_URLS.findall(response)
            for url in extraction:
                url = f"https://www.eporner.com{url}"
                url = url.replace("EPTHBN/", "")
                video_urls.append(url)

        video_tasks = [asyncio.create_task(Client.get_video(url=url, enable_html_scraping=enable_html_scraping)) for url in video_urls]
        video_results = await asyncio.gather(*video_tasks)
        return video_results


    @classmethod
    async def get_pornstar(cls, url: str, enable_html_scraping: bool = True) -> Pornstar:
        return await Pornstar.create(url, enable_html_scraping)


async def main():
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
    no_title = BaseCore().str_to_bool(args.no_title)

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


if __name__ == "__main__":
    asyncio.run(main())
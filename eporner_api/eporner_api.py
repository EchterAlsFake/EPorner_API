import re

import requests
import json
import os

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

from functools import cached_property
from bs4 import BeautifulSoup
from typing import Generator

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


class Video:
    def __init__(self, url, enable_html_scraping=False):
        self.url = url
        self.enable_html = enable_html_scraping
        self.html_content = None
        self.json_data = self.raw_json_data()
        if self.enable_html:
            self.request_html_content()
            self.html_json_data = self.extract_json_from_html()

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

    def raw_json_data(self):
        """
        Uses the V2 API to retrieve information from a video
        :return:
        """

        data = (requests.get(f"{ROOT_URL}{API_VIDEO_ID}?id={self.video_id}&thumbsize=medium&format=json")
                .content.decode("utf-8"))
        parsed_data = json.loads(data)
        return parsed_data

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

    def request_html_content(self):
        if not self.enable_html:
            raise HTML_IS_DISABLED("HTML content is disabled! See Documentation for more details")

        self.html_content = requests.get(self.url).content.decode("utf-8")

    def extract_json_from_html(self):
        if not self.enable_html:
            raise HTML_IS_DISABLED("HTML content is disabled! See Documentation for more details")

        soup = BeautifulSoup(self.html_content, 'lxml')
        script_tags = soup.find_all('script', {'type': 'application/ld+json'})

        combined_data = {}

        for script in script_tags:
                json_text = script.string.strip()
                data = json.loads(json_text)
                combined_data.update(data)
        cleaned_dictionary = self.flatten_json(combined_data)
        return cleaned_dictionary

    def flatten_json(self, nested_json, parent_key='', sep='_'):
        """
        Flatten a nested json dictionary. Duplicate keys will be overridden.

        :param nested_json: The nested JSON dictionary to be flattened.
        :param parent_key: The base key to use for the flattened keys.
        :param sep: The separator between nested keys.
        :return: A flattened dictionary.
        """
        items = []
        for k, v in nested_json.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_json(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    @cached_property
    def bitrate(self):
        if self.enable_html:
            return self.html_json_data["bitrate"]

        else:
            return None

    @cached_property
    def source_video_url(self):
        """
        Returns the .mp4 video location URL

        :return: str
        """
        if self.enable_html:
            return self.html_json_data["contentUrl"]

        else:
            return None

    @cached_property
    def rating(self):
        """
        Returns the rating value. Highest (best) is 100, least is 0 (worst)
        :return: str
        """
        if self.enable_html:
            try:
                return self.html_json_data["aggregateRating_ratingValue"]

            except KeyError:
                raise NotAvailable("No rating available. This isn't an error!")

    @cached_property
    def likes(self):
        """
        Returns the video likes
        :return: str
        """
        if self.enable_html:
            return REGEX_VIDEO_LIKES.search(self.html_content).group(1)

    @cached_property
    def dislikes(self):
        """
        Returns the video dislikes
        :return:
        """
        if self.enable_html:
            return REGEX_VIDEO_DISLIKES.search(self.html_content).group(1)

    @cached_property
    def rating_count(self):
        """
        Returns how many people have rated the video
        :return: str
        """
        if self.enable_html:
            return self.html_json_data["aggregateRating_ratingCount"]

        else:
            return None

    @cached_property
    def author(self):
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
        :param quality:
        :param mode:
        :return: str
        """
        if not self.enable_html:
            raise HTML_IS_DISABLED("HTML content is disabled! See Documentation for more details")

        quality = self.fix_quality(quality)
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
                        break  # Stop once the first matching preference is found for this link

        # Sort available links by quality preferences
        available_links.sort(key=lambda x: quality_preferences.index(x[0]))

        start_index = 0
        if quality == Quality.HALF:
            start_index = len(quality_preferences) // 3  # Adjust based on preference
        elif quality == Quality.WORST:
            start_index = 2 * len(quality_preferences) // 3  # Adjust based on preference

        # Filter links based on quality preference and availability
        for preference in quality_preferences[start_index:]:
            for resolution, link in available_links:
                if resolution == preference:
                    return f"https://eporner.com{link}"

        # If no specific match is found, return None or the lowest available quality
        if len(available_links) <= 0:
            raise NotAvailable("No available links for given quality / mode found. Not all videos support AV1")

        return "https://eporner.com" + available_links[-1][1] if available_links else None

    @classmethod
    def fix_quality(cls, quality):

        if isinstance(quality, Quality):
            return quality

        else:
            if str(quality) == "best":
                return Quality.BEST

            elif str(quality) == "half":
                return Quality.HALF

            elif str(quality) == "worst":
                return Quality.WORST

    def download_video(self, quality, output_path, callback=None, mode=Encoding.mp4_h264):
        if not self.enable_html:
            raise HTML_IS_DISABLED("HTML content is disabled! See Documentation for more details")

        quality = self.fix_quality(quality)

        session = requests.Session()
        response_redirect_url = session.get(self.direct_download_link(quality, mode),
                                            allow_redirects=False)

        if 'Location' in response_redirect_url.headers:
            redirected_url = response_redirect_url.headers['Location']
            response_download = session.get(redirected_url, stream=True)
            file_size = int(response_download.headers.get('content-length', 0))

            final_path = output_path
            if callback is None:
                progress_bar = Callback()

            downloaded_so_far = 0

            if not os.path.exists(final_path):
                with open(final_path, 'wb') as file:
                    for chunk in response_download.iter_content(chunk_size=1024):
                        file.write(chunk)
                        downloaded_so_far += len(chunk)

                        if callback:
                            callback(downloaded_so_far, file_size)

                        else:
                            progress_bar.text_progress_bar(downloaded=downloaded_so_far, total=file_size)

                if not callback:
                    del progress_bar


class Pornstar:
    def __init__(self, url, enable_html_scraping=False):
        self.url = url
        self.enable_html_scraping = enable_html_scraping
        self.html_content = requests.get(self.url).text

    def videos(self, pages: int = 2) -> Generator:
        urls = []
        for page in range(pages):
            response = requests.get(self.url).content.decode("utf-8")
            extraction = REGEX_SCRAPE_VIDEO_URLS.findall(response)
            for url in extraction:
                url = f"https://www.eporner.com{url}"
                url = url.replace("EPTHBN/", "")
                urls.append(url)

        for url in urls:
            yield Video(url, enable_html_scraping=self.enable_html_scraping)

    @cached_property
    def name(self):
        return REGEX_PORNSTAR_NAME.search(self.html_content).group(1)

    @cached_property
    def subscribers(self):
        return REGEX_PORNSTAR_SUBSCRIBERS.search(self.html_content).group(1).replace("(", "").replace(")", "")

    @cached_property
    def picture(self):
        REGEX_PORNSTAR_PICTURE = re.compile(fr'<img src="(.*?)" alt="{self.name}" >')
        return REGEX_PORNSTAR_PICTURE.search(self.html_content).group(1)

    @cached_property
    def photos_amount(self):
        return REGEX_PORNSTAR_PHOTOS_AMOUNT.search(self.html_content).group(1)

    @cached_property
    def video_amount(self):
        return REGEX_PORNSTAR_VIDEO_AMOUNT.search(self.html_content).group(1)

    @cached_property
    def pornstar_rank(self):
        return REGEX_PORNSTAR_RANK.search(self.html_content).group(1)

    @cached_property
    def profile_views(self):
        return REGEX_PORNSTAR_PROFILE_VIEWS.search(self.html_content).group(1)

    @cached_property
    def video_views(self):
        return REGEX_PORNSTAR_VIDEO_VIEWS.search(self.html_content).group(1)

    @cached_property
    def photo_views(self):
        return REGEX_PORNSTAR_PHOTO_VIEWS.search(self.html_content).group(1)

    @cached_property
    def country(self):
        return REGEX_PORNSTAR_COUNTRY.search(self.html_content).group(1)

    @cached_property
    def age(self):
        return REGEX_PORNSTAR_AGE.search(self.html_content).group(1)

    @cached_property
    def ethnicity(self):
        return REGEX_PORNSTAR_ETHNICITY.search(self.html_content).group(1)

    @cached_property
    def eye_color(self):
        return REGEX_PORNSTAR_EYE_COLOR.search(self.html_content).group(1)

    @cached_property
    def hair_color(self):
        return REGEX_PORNSTAR_HAIR_COLOR.search(self.html_content).group(1)

    @cached_property
    def height(self):
        return REGEX_PORNSTAR_HEIGHT.search(self.html_content).group(1)

    @cached_property
    def weight(self):
        return REGEX_PORNSTAR_WEIGHT.search(self.html_content).group(1)

    @cached_property
    def cup(self):
        return REGEX_PORNSTAR_CUP.search(self.html_content).group(1)

    @cached_property
    def measurements(self):
        return REGEX_PORNSTAR_MEASUREMENTS.search(self.html_content).group(1)

    @cached_property
    def aliases(self):
        aliases = REGEX_PORNSTAR_ALIASES.search(self.html_content).group(1)
        aliases_filtered = re.findall("<li>(.*?)</li>", aliases)
        return aliases_filtered

    @cached_property
    def biography(self):
        return REGEX_PORNSTAR_BIOGRAPHY.search(self.html_content).group(1)


class Client:

    @classmethod
    def get_video(cls, url, enable_html_scraping=False):
        return Video(url, enable_html_scraping=enable_html_scraping)

    @classmethod
    def search_videos(cls, query: str, sorting_gay: Gay, sorting_order: Order, sorting_low_quality: LowQuality,
                      page: int, per_page: int, enable_html_scraping=False):

        response = requests.get(f"{ROOT_URL}{API_SEARCH}?query={query}&per_page={per_page}&%page={page}"
                                f"&thumbsize=medium&order={sorting_order}&gay={sorting_gay}&lq="
                                f"{sorting_low_quality}&format=json")

        content = response.content.decode("utf-8")
        json_data = json.loads(content)
        for video_ in json_data.get("videos", []):  # Don't know why this works lmao
            id_ = video_["url"]
            yield Video(id_, enable_html_scraping)

    @classmethod
    def get_videos_by_category(cls, category: Category, pages: int = 2, enable_html_scraping=False):
        urls = []

        for page in range(pages):
            response = requests.get(f"{ROOT_URL}cat/{category}/{page}").content.decode("utf-8")
            extraction = REGEX_SCRAPE_VIDEO_URLS.findall(response)
            for url in extraction:
                url = f"https://www.eporner.com{url}"
                url = url.replace("EPTHBN/", "")
                urls.append(url)

        for url in urls:
            yield Video(url, enable_html_scraping=enable_html_scraping)

    @classmethod
    def get_pornstar(cls, url, enable_html_scraping=True):
        return Pornstar(url, enable_html_scraping)

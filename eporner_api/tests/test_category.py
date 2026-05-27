import pytest
from ..eporner_api import Client, Category
from base_api import BaseCore

@pytest.mark.asyncio
async def test_category():
    core = BaseCore()
    core.config.pages_concurrency = 1
    core.config.videos_concurrency = 1
    
    videos_1 = Client(core).get_videos_by_category(category=Category.JAPANESE)
    videos_2 = Client(core).get_videos_by_category(category=Category.HD)
    videos_3 = Client(core).get_videos_by_category(category=Category.BLONDE)

    idx = 0
    async for video in videos_1:
        if idx == 3:
            break
        assert isinstance(video.title, str) and len(video.title) > 0
        idx += 1

    idx = 0
    async for video in videos_2:
        if idx == 3:
            break
        assert isinstance(video.title, str) and len(video.title) > 0
        idx += 1

    idx = 0
    async for video in videos_3:
        if idx == 3:
            break
        assert isinstance(video.title, str) and len(video.title) > 0
        idx += 1

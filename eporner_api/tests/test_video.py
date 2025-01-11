import pytest
from ..eporner_api import Client, Encoding, NotAvailable

url = "https://www.eporner.com/video-0t0CdQ8Fhaf/hypnotic-big-tits-therapy-video-5-cock-hero/"

@pytest.mark.asyncio
async def test_video_all():
    video = await Client().get_video(url, enable_html_scraping=True)
    assert isinstance(video.title, str) and len(video.title) > 0
    assert isinstance(video.video_id, str) and len(video.video_id) > 0
    assert isinstance(video.tags, list) and len(video.tags) > 0
    assert isinstance(video.views, int) and video.views > 0
    assert isinstance(video.rate, str) and len(video.rate) > 0
    assert isinstance(video.publish_date, str) and len(video.publish_date) > 0
    assert isinstance(video.length, int) > 0
    assert isinstance(video.length_minutes, str) and len(video.length_minutes) > 0
    assert isinstance(video.embed_url, str) and len(video.embed_url) > 0
    assert isinstance(video.thumbnail, str) and len(video.thumbnail) > 0
    assert isinstance(video.bitrate, str) and len(video.bitrate) > 0
    assert isinstance(video.source_video_url, str) and len(video.source_video_url) > 0
    assert isinstance(video.rating, str) and len(video.rating) > 0
    assert isinstance(video.rating_count, str) and len(video.rating_count) > 0
    assert isinstance(video.author, str) and len(video.author) > 0
    assert isinstance(video.direct_download_link(quality="best", mode=Encoding.mp4_h264), str)
    assert isinstance(video.direct_download_link(quality="half", mode=Encoding.mp4_h264), str)
    assert isinstance(video.direct_download_link(quality="worst", mode=Encoding.mp4_h264), str)

    try:
        assert isinstance(video.direct_download_link(quality="best", mode=Encoding.av1), str)
        assert isinstance(video.direct_download_link(quality="half", mode=Encoding.av1), str)
        assert isinstance(video.direct_download_link(quality="worst", mode=Encoding.av1), str)

    except NotAvailable:
        pass

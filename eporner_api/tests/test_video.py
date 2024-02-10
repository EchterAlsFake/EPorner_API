from ..eporner_api import Client, Quality, Encoding, NotAvailable

url = "https://www.eporner.com/hd-porn/f8MuayGnGiS/Exciting-Moments-With-Lacey-Duvalle/"
video = Client.get_video(url, enable_html_scraping=True)


def test_title():
    assert isinstance(video.title, str) and len(video.title) > 0


def test_video_id():
    assert isinstance(video.video_id, str) and len(video.video_id) > 0


def test_tags():
    assert isinstance(video.tags, list) and len(video.tags) > 0


def test_views():
    assert isinstance(video.views, int) and video.views > 0


def test_rate():
    assert isinstance(video.rate, str) and len(video.rate) > 0


def test_publish_date():
    assert isinstance(video.publish_date, str) and len(video.publish_date) > 0


def test_length_seconds():
    assert isinstance(video.length, int) > 0


def test_length_minutes():
    assert isinstance(video.length_minutes, str) and len(video.length_minutes) > 0


def test_embed_url():
    assert isinstance(video.embed_url, str) and len(video.embed_url) > 0


def test_thumbnails():
    assert isinstance(video.thumbnail, str) and len(video.thumbnail) > 0


def test_bitrate():
    assert isinstance(video.bitrate, str) and len(video.bitrate) > 0


def test_source_video_url():
    assert isinstance(video.source_video_url, str) and len(video.source_video_url) > 0


def test_rating():
    assert isinstance(video.rating, str) and len(video.rating) > 0


def test_rating_count():
    assert isinstance(video.rating_count, str) and len(video.rating_count) > 0


def test_author():
    assert isinstance(video.author, str) and len(video.author) > 0


def test_direct_download_url():
    assert isinstance(video.direct_download_link(quality=Quality.BEST, mode=Encoding.mp4_h264), str)
    assert isinstance(video.direct_download_link(quality=Quality.HALF, mode=Encoding.mp4_h264), str)
    assert isinstance(video.direct_download_link(quality=Quality.WORST, mode=Encoding.mp4_h264), str)
    try:
        assert isinstance(video.direct_download_link(quality=Quality.BEST, mode=Encoding.av1), str)
        assert isinstance(video.direct_download_link(quality=Quality.HALF, mode=Encoding.av1), str)
        assert isinstance(video.direct_download_link(quality=Quality.WORST, mode=Encoding.av1), str)

    except NotAvailable:
        pass

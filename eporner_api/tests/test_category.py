import time

from ..eporner_api import Client, Category


def test_category():
    videos_1 = Client().get_videos_by_category(category=Category.JAPANESE)
    videos_2 = Client().get_videos_by_category(category=Category.HD)
    videos_3 = Client().get_videos_by_category(category=Category.BLONDE)

    for idx, video in enumerate(videos_1):
        time.sleep(5) # Lmao
        if idx == 3:
            break

        assert isinstance(video.title, str) and len(video.title) > 0

    for idx, video in enumerate(videos_2):
        time.sleep(5)
        if idx == 3:
            break

        assert isinstance(video.title, str) and len(video.title) > 0

    for idx, video in enumerate(videos_3):
        time.sleep(5)
        if idx == 3:
            break

        assert isinstance(video.title, str) and len(video.title) > 0

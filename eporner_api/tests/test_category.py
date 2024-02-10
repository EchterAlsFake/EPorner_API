from ..eporner_api import Client, Category


def test_category():
    pages = 1

    videos_1 = Client().get_videos_by_category(category=Category.JAPANESE, pages=pages)
    videos_2 = Client().get_videos_by_category(category=Category.HD, pages=pages)
    videos_3 = Client().get_videos_by_category(category=Category.BLONDE, pages=pages)

    for idx, video in enumerate(videos_1):
        if idx == 3:
            break

        assert isinstance(video.title, str) and len(video.title) > 0

    for idx, video in enumerate(videos_2):
        if idx == 3:
            break

        assert isinstance(video.title, str) and len(video.title) > 0

    for idx, video in enumerate(videos_3):
        if idx == 3:
            break

        assert isinstance(video.title, str) and len(video.title) > 0

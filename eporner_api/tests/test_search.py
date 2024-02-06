from ..eporner_api import Client, Gay, Order, LowQuality

client = Client()
query = "Mia Khalifa"
pages = 2
per_page = 10


def test_search_1():
    videos = client.search_videos(query, page=pages, per_page=per_page, sorting_gay=Gay.exclude_gay_content, sorting_order=Order.top_rated, sorting_low_quality=LowQuality.exclude_low_quality_content)
    for video in videos:
        assert len(video.title) > 0


def test_search_2():
    videos = client.search_videos(query, page=pages, per_page=per_page, sorting_gay=Gay.only_gay_content, sorting_order=Order.latest, sorting_low_quality=LowQuality.only_low_quality_content)
    for video in videos:
        assert len(video.title) > 0


def test_search_3():
    videos = client.search_videos(query, page=pages, per_page=per_page, sorting_gay=Gay.include_gay_content, sorting_order=Order.longest, sorting_low_quality=LowQuality.include_low_quality_content)
    for video in videos:
        assert len(video.title) > 0


def test_search_4():
    videos = client.search_videos(query, page=pages, per_page=pages, sorting_gay=Gay.exclude_gay_content, sorting_order=Order.shortest, sorting_low_quality=LowQuality.include_low_quality_content)
    for video in videos:
        assert len(video.title) > 0


def test_search_5():
    videos = client.search_videos(query, page=pages, per_page=per_page, sorting_order=Gay.include_gay_content, sorting_gay=Order.top_weekly, sorting_low_quality=LowQuality.include_low_quality_content)
    for video in videos:
        assert len(video.title) > 0


def test_search_6():
    videos = client.search_videos(query, page=pages, per_page=per_page, sorting_order=Order.most_popular, sorting_low_quality=LowQuality.include_low_quality_content, sorting_gay=Gay.only_gay_content)
    for video in videos:
        assert len(video.title) > 0


def test_search_7():
    videos = client.search_videos(query, page=pages, per_page=per_page, sorting_gay=Gay.include_gay_content, sorting_order=Order.top_monthly, sorting_low_quality=LowQuality.include_low_quality_content)
    for video in videos:
        assert len(video.title) > 0

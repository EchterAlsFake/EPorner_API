import pytest
from ..eporner_api import Client, Gay, Order, LowQuality

client = Client()
query = "Mia Khalifa"
pages = 2
per_page = 10

@pytest.mark.asyncio
async def test_search_all():
    videos = await client.search_videos(query, page=pages, per_page=per_page, sorting_gay=Gay.exclude_gay_content, sorting_order=Order.top_rated, sorting_low_quality=LowQuality.exclude_low_quality_content, enable_html_scraping=True)
    for video in videos:
        assert len(video.title) > 0

    videos = await client.search_videos(query, page=pages, per_page=per_page, sorting_gay=Gay.only_gay_content, sorting_order=Order.latest, sorting_low_quality=LowQuality.only_low_quality_content, enable_html_scraping=True)
    for video in videos:
        assert len(video.title) > 0

    videos = await client.search_videos(query, page=pages, per_page=per_page, sorting_gay=Gay.include_gay_content, sorting_order=Order.longest, sorting_low_quality=LowQuality.include_low_quality_content, enable_html_scraping=True)
    for video in videos:
        assert len(video.title) > 0

    videos = await client.search_videos(query, page=pages, per_page=pages, sorting_gay=Gay.exclude_gay_content, sorting_order=Order.shortest, sorting_low_quality=LowQuality.include_low_quality_content, enable_html_scraping=True)
    for video in videos:
        assert len(video.title) > 0

    videos = await client.search_videos(query, page=pages, per_page=per_page, sorting_order=Gay.include_gay_content, sorting_gay=Order.top_weekly, sorting_low_quality=LowQuality.include_low_quality_content, enable_html_scraping=True)
    for video in videos:
        assert len(video.title) > 0

    videos = await client.search_videos(query, page=pages, per_page=per_page, sorting_order=Order.most_popular, sorting_low_quality=LowQuality.include_low_quality_content, sorting_gay=Gay.only_gay_content, enable_html_scraping=True)
    for video in videos:
        assert len(video.title) > 0

    videos = await client.search_videos(query, page=pages, per_page=per_page, sorting_gay=Gay.include_gay_content, sorting_order=Order.top_monthly, sorting_low_quality=LowQuality.include_low_quality_content, enable_html_scraping=True)
    for video in videos:
        assert len(video.title) > 0

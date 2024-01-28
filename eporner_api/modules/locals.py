from enum import Enum


class Sort:
    # Quality

    exclude_low_quality_content = "0"
    include_low_quality_content = "1"
    only_low_quality_content = "2"

    """
    You can also specify the format either XML or Json. We only use JSON in the API!
    format = json
    """


class Size:
    # Thumbnail Sizes
    small = "small"    # 190x152
    medium = "medium"  # 427x240
    big = "big"        # 640x360


class Quality(Enum):
    BEST = 'BEST'
    HALF = 'HALF'
    WORST = 'WORST'


class Encoding:
    mp4_h264 = "h264"  # Same quality, more file size
    av1 = "AV1"  # Same quality, less file size

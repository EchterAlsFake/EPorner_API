from enum import Enum


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

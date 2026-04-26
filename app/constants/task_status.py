from enum import StrEnum


class TaskStatus(StrEnum):
    # finish
    DETECT_CAT_FINISHED = "detect_cat:finished"
    TRIM_CAT_FINISHED = "trim_cat:finished"

    # failed
    READ_IMAGE_FAILED = "read_image:failed"
    DETECT_CAT_FAILED = "detect_cat:failed"
    TRIM_CAT_FAILED = "trim_cat:failed"

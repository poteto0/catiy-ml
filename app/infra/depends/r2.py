from collections.abc import Generator

from mypy_boto3_s3 import S3Client

from app.infra.r2.client import r2Client


def get_r2() -> Generator[S3Client]:
    yield r2Client

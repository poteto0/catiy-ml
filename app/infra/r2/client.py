import boto3

from app.config.setting import setting

endpoint_url = (
    "http://localhost:4566"
    if setting.env == "TEST"
    else f"https://{setting.r2AccountID}.r2.cloudflarestorage.com"
)

r2Client = boto3.client(
    "s3",
    endpoint_url=endpoint_url,
    aws_access_key_id=setting.r2AccessKeyID,
    aws_secret_access_key=setting.r2AccessSecretKey,
    region_name="auto",
)

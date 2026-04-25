import boto3

from app.config.setting import setting

r2Client = boto3.client(
    "s3",
    endpoint_url=f"https://{setting.r2AccountID}.r2.cloudflarestorage.com",
    aws_access_key_id=setting.r2AccessKeyID,
    aws_secret_access_key=setting.r2AccessSecretKey,
    region_name="auto",
)

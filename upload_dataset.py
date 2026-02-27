import boto3
from botocore.config import Config
from boto3.s3.transfer import TransferConfig
from tqdm import tqdm
import os
import sys
import argparse

# ===== CONFIGURATION =====
# you can override these on the command line or via environment variables
BUCKET_NAME = os.environ.get("TACOPS_BUCKET", "tacops-map-images")
REGION = os.environ.get("AWS_DEFAULT_REGION", "eu-central-1")
EXPIRATION = 604800  # 7 days in seconds
# S3_KEY is the *object key* (name within the bucket); not AWS credentials
# FILE_PATH and S3_KEY will be supplied by the user at runtime (via args)
# ==========================


def upload_with_progress(file_path, bucket, key, progress_callback=None):
    """Upload a file to S3. If *progress_callback* is provided it will be called
    with the number of bytes transferred on each chunk; otherwise a tqdm progress
    bar is shown (CLI behaviour).
    """
    file_size = os.path.getsize(file_path)

    use_tqdm = progress_callback is None
    if use_tqdm:
        progress = tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            desc="Uploading"
        )

        def _cb(bytes_transferred):
            progress.update(bytes_transferred)
    else:
        _cb = progress_callback

    config = TransferConfig(
        multipart_threshold=1024 * 25,
        multipart_chunksize=1024 * 25,
        use_threads=True
    )

    s3 = boto3.client(
        "s3",
        region_name=REGION,
        config=Config(signature_version="s3v4")
    )

    s3.upload_file(
        file_path,
        bucket,
        key,
        Callback=_cb,
        Config=config,
        ExtraArgs={
            "ContentType": "application/zip",
            "ContentDisposition": "attachment"
        }
    )

    if use_tqdm:
        progress.close()
    return s3


def generate_presigned_url(s3_client, bucket, key, expiration):
    url = s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": bucket,
            "Key": key,
            "ResponseContentDisposition": "attachment"
        },
        ExpiresIn=expiration
    )
    return url


def ensure_credentials():
    """Ensure AWS credentials are available, optionally prompting and writing them."""
    session = boto3.Session()
    creds = session.get_credentials()
    if creds is None or not creds.access_key:
        print("AWS credentials not found. You can run 'aws configure' or enter them now.")
        if input("Would you like to enter credentials now? [y/N]: ").strip().lower() == 'y':
            access_key = input("AWS Access Key ID: ").strip()
            secret_key = input("AWS Secret Access Key: ").strip()
            region = input(f"AWS Region [{REGION}]: ").strip() or REGION
            import configparser
            cred_path = os.path.expanduser("~/.aws/credentials")
            cfg = configparser.ConfigParser()
            cfg['default'] = {
                'aws_access_key_id': access_key,
                'aws_secret_access_key': secret_key
            }
            os.makedirs(os.path.dirname(cred_path), exist_ok=True)
            with open(cred_path, 'w') as f:
                cfg.write(f)
            conf_path = os.path.expanduser("~/.aws/config")
            cfg2 = configparser.ConfigParser()
            cfg2['default'] = {'region': region}
            with open(conf_path, 'w') as f:
                cfg2.write(f)
            print(f"Credentials written to {cred_path}")
        else:
            sys.exit("Credentials are required to upload to S3.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a file to S3 with progress and generate a presigned URL.")
    parser.add_argument('--file', '-f', dest='file_path', required=True,
                        help='Path to the local file to upload')
    parser.add_argument('--key', '-k', dest='s3_key', required=True,
                        help='S3 object key (name in the bucket)')
    parser.add_argument('--bucket', '-b', dest='bucket', default=BUCKET_NAME,
                        help='S3 bucket name (env TACOPS_BUCKET or default)')
    parser.add_argument('--region', '-r', dest='region', default=REGION,
                        help='AWS region (env AWS_DEFAULT_REGION or default)')
    parser.add_argument('--expiry', '-e', dest='expiry', type=int, default=EXPIRATION,
                        help='Presigned URL expiration in seconds')
    args = parser.parse_args()

    FILE_PATH = args.file_path
    S3_KEY = args.s3_key
    BUCKET_NAME = args.bucket
    REGION = args.region
    EXPIRATION = args.expiry

    if not os.path.exists(FILE_PATH):
        print("File not found.")
        sys.exit(1)

    ensure_credentials()

    print("Starting upload...\n")
    try:
        s3_client = upload_with_progress(FILE_PATH, BUCKET_NAME, S3_KEY)
    except Exception as e:
        print(f"Upload failed: {e}")
        sys.exit(1)

    print(f"\nGenerating {EXPIRATION}-second pre-signed URL...\n")
    url = generate_presigned_url(
        s3_client,
        BUCKET_NAME,
        S3_KEY,
        EXPIRATION
    )

    print(f"Download URL (valid {EXPIRATION} seconds):\n")
    print(url)
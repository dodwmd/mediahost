from minio import Minio
from minio.error import S3Error
import os
from dotenv import load_dotenv
from datetime import timedelta
import io

load_dotenv()

minio_client = Minio(
    os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
    access_key=os.getenv('MINIO_ACCESS_KEY'),
    secret_key=os.getenv('MINIO_SECRET_KEY'),
    secure=os.getenv('MINIO_SECURE', 'False').lower() == 'true'
)

def upload_file(file_data, file_name, bucket_name="videos"):
    try:
        # Make sure the bucket exists
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)

        # Convert bytes to file-like object if necessary
        if isinstance(file_data, bytes):
            file_data = io.BytesIO(file_data)

        # Get the file size
        file_data.seek(0, os.SEEK_END)
        file_size = file_data.tell()
        file_data.seek(0)

        # Upload the file
        minio_client.put_object(
            bucket_name, file_name, file_data, length=file_size, part_size=10*1024*1024
        )
        return f"{bucket_name}/{file_name}"
    except S3Error as e:
        print(f"Error uploading file to MinIO: {e}")
        return None

def get_secure_file_url(file_path, bucket_name="videos", expires=timedelta(minutes=30)):
    try:
        return minio_client.presigned_get_object(bucket_name, file_path, expires=expires)
    except S3Error as e:
        print(f"Error getting presigned URL: {e}")
        return None

def get_file_url(file_path, bucket_name="videos", expires=3600):
    return get_secure_file_url(file_path, bucket_name, expires=timedelta(seconds=expires))

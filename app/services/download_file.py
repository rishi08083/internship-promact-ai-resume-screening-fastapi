import boto3
import io
from dotenv import load_dotenv
import os
from botocore.exceptions import ClientError

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('aws_access_key_id')
AWS_SECRET_ACCESS_KEY=os.getenv('aws_secret_access_key')
REGION=os.getenv('region')
bucket_name = os.getenv('aws_bucket_name')


s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=REGION )

def download_from_s3_to_buffer(file_key):
    file_buffer = io.BytesIO()
    try:
        s3_client.download_fileobj(bucket_name, file_key, file_buffer)
        
        file_buffer.seek(0)
        
        file_content = file_buffer.read()
                
        return file_content

    except ClientError as e:
        print(f"Failed to download from S3: {e}")
        raise ValueError(f"Failed to download from S3: {e}")
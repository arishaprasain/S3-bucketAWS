#!/usr/bin/env python3
"""
Simple S3 Deployment Script for Café Website

This script provides a straightforward way to deploy the café website
to AWS S3 without using Google Colab or Jupyter notebooks.

Usage:
    python deploy_to_s3.py

Requirements:
    pip install boto3
"""

import os
import sys
import json
import mimetypes
from pathlib import Path

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print("Error: boto3 is not installed.")
    print("Please install it using: pip install boto3")
    sys.exit(1)


def get_aws_credentials():
    """Get AWS credentials from user input."""
    print("\n" + "="*60)
    print("AWS Credentials Configuration")
    print("="*60)
    
    # Check if credentials are already in environment
    if os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
        print("✓ AWS credentials found in environment variables")
        region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        return region
    
    # Get credentials from user
    import getpass
    aws_access_key_id = getpass.getpass('Enter AWS Access Key ID: ')
    aws_secret_access_key = getpass.getpass('Enter AWS Secret Access Key: ')
    aws_region = input('Enter AWS Region (default: us-east-1): ') or 'us-east-1'
    
    # Set environment variables
    os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key_id
    os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_access_key
    os.environ['AWS_DEFAULT_REGION'] = aws_region
    
    print(f"✓ AWS credentials configured for region: {aws_region}")
    return aws_region


def verify_aws_credentials():
    """Verify that AWS credentials are working."""
    try:
        s3_client = boto3.client('s3')
        response = s3_client.list_buckets()
        print("\n✓ AWS credentials verified successfully!")
        print(f"\nYou have access to {len(response['Buckets'])} S3 bucket(s)")
        return s3_client
    except NoCredentialsError:
        print("\n✗ No AWS credentials found. Please configure them.")
        return None
    except ClientError as e:
        print(f"\n✗ Error verifying credentials: {e}")
        return None


def upload_directory_to_s3(local_directory, bucket_name, s3_client, s3_prefix=''):
    """Upload a directory to S3 bucket with proper content types."""
    uploaded_files = []
    failed_files = []
    
    print(f"\nUploading files from {local_directory} to s3://{bucket_name}/")
    print("-" * 60)
    
    for root, dirs, files in os.walk(local_directory):
        # Skip .github directory
        if '.github' in root:
            continue
            
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_directory)
            s3_path = os.path.join(s3_prefix, relative_path).replace("\\", "/")
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(local_path)
            if content_type is None:
                content_type = 'binary/octet-stream'
            
            try:
                extra_args = {'ContentType': content_type}
                s3_client.upload_file(local_path, bucket_name, s3_path, ExtraArgs=extra_args)
                uploaded_files.append(s3_path)
                print(f"✓ {s3_path}")
            except ClientError as e:
                failed_files.append((s3_path, str(e)))
                print(f"✗ {s3_path}: {e}")
    
    return uploaded_files, failed_files


def configure_static_website(bucket_name, s3_client):
    """Configure the S3 bucket for static website hosting."""
    website_configuration = {
        'ErrorDocument': {'Key': 'error.html'},
        'IndexDocument': {'Suffix': 'index.html'},
    }
    
    try:
        s3_client.put_bucket_website(
            Bucket=bucket_name,
            WebsiteConfiguration=website_configuration
        )
        print("✓ Static website hosting configured")
        return True
    except ClientError as e:
        print(f"✗ Error configuring website: {e}")
        return False


def set_bucket_policy(bucket_name, s3_client):
    """Set bucket policy for public read access."""
    # First, try to disable block public access settings
    try:
        s3_client.delete_public_access_block(Bucket=bucket_name)
        print("✓ Public access block removed")
    except ClientError as e:
        print(f"Note: Could not remove public access block: {e}")
    
    # Define bucket policy for public read access
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        ]
    }
    
    # Apply the bucket policy
    try:
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        print("✓ Bucket policy applied for public access")
        return True
    except ClientError as e:
        print(f"✗ Error setting bucket policy: {e}")
        return False


def get_website_url(bucket_name, region):
    """Get the website URL for the bucket."""
    if region == 'us-east-1':
        return f"http://{bucket_name}.s3-website-us-east-1.amazonaws.com"
    else:
        return f"http://{bucket_name}.s3-website-{region}.amazonaws.com"


def main():
    """Main deployment function."""
    print("\n" + "="*60)
    print("Café Website S3 Deployment Script")
    print("="*60)
    
    # Get AWS credentials
    region = get_aws_credentials()
    
    # Verify credentials
    s3_client = verify_aws_credentials()
    if not s3_client:
        sys.exit(1)
    
    # Get bucket name
    print("\n" + "="*60)
    bucket_name = input('Enter your S3 bucket name: ').strip()
    if not bucket_name:
        print("✗ Bucket name cannot be empty")
        sys.exit(1)
    
    # Check if public directory exists
    public_dir = './public'
    if not os.path.exists(public_dir):
        print(f"✗ Error: {public_dir} directory not found")
        print("Please run this script from the repository root directory")
        sys.exit(1)
    
    # Upload files
    print("\n" + "="*60)
    print("Step 1: Uploading Files")
    print("="*60)
    uploaded, failed = upload_directory_to_s3(public_dir, bucket_name, s3_client)
    
    if failed:
        print(f"\n⚠ Warning: {len(failed)} file(s) failed to upload")
    
    print(f"\n✓ Successfully uploaded {len(uploaded)} file(s)")
    
    # Configure static website hosting
    print("\n" + "="*60)
    print("Step 2: Configuring Static Website Hosting")
    print("="*60)
    configure_static_website(bucket_name, s3_client)
    
    # Set bucket policy
    print("\n" + "="*60)
    print("Step 3: Setting Bucket Policy for Public Access")
    print("="*60)
    set_bucket_policy(bucket_name, s3_client)
    
    # Display website URL
    website_url = get_website_url(bucket_name, region)
    
    print("\n" + "="*60)
    print("🎉 Deployment Complete!")
    print("="*60)
    print(f"\nYour website is now live at:\n{website_url}")
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)

# S3 Bucket AWS - Café Website

This repository contains a static website for a café that is deployed to AWS S3. The website showcases the café's offerings, including pastries, coffees, and other treats.

## Repository Structure

- `public/` - Contains all website files
  - `index.html` - Main website page
  - `css/` - Stylesheets
  - `images/` - Website images
  - `.github/workflows/main.yml` - GitHub Actions workflow for automated deployment

## Deployment

The website is automatically deployed to AWS S3 using GitHub Actions whenever changes are pushed to the main branch.

### S3 Bucket
- Bucket name: `cafebucketchallengearisha`
- Region: `us-east-1`

## Using This Repository in Google Colab

For detailed instructions on how to use this repository in Google Colab, including uploading files to S3 and managing your bucket, please refer to:

**[colab_s3_deployment.ipynb](./colab_s3_deployment.ipynb)**

The notebook provides:
- Step-by-step instructions for AWS S3 deployment
- Python code examples using boto3
- AWS CLI commands for bucket management
- Configuration for static website hosting
- Troubleshooting tips

## Quick Start with Colab

1. Open the [colab_s3_deployment.ipynb](./colab_s3_deployment.ipynb) notebook
2. Click "Open in Colab" badge (or upload to Google Colab)
3. Follow the instructions in the notebook
4. Configure your AWS credentials
5. Run the cells to deploy your website to S3

## Prerequisites

- AWS Account
- AWS Access Key ID and Secret Access Key
- S3 bucket (can be created through the notebook)

## License

© 2020, Amazon Web Services, Inc. or its Affiliates. All rights reserved.

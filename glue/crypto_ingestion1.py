import json
import logging
import sys
from datetime import datetime, timezone

import boto3
import requests
from awsglue.utils import getResolvedOptions

#########################################################
# Configuration
#########################################################

S3_PREFIX = "bronze/coingecko"

URL = "https://api.coingecko.com/api/v3/coins/markets"

PER_PAGE = 250

#########################################################
# Logger
#########################################################

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)

#########################################################
# Glue Job Arguments
#########################################################

def get_job_arguments():

    return getResolvedOptions(
        sys.argv,
        [
            "BUCKET_NAME",
            "API_KEY"
        ]
    )

#########################################################
# AWS Client
#########################################################

def get_s3_client():

    return boto3.client("s3")

#########################################################
# Download data
#########################################################

def get_data(api_key):

    logger.info("Starting CoinGecko download...")

    all_records = []

    page = 1

    while True:

        logger.info(f"Downloading page {page}")

        response = requests.get(
            URL,
            params={
                "vs_currency": "usd",
                "per_page": PER_PAGE,
                "page": page
            },
            headers={
                "x-cg-demo-api-key": api_key
            },
            timeout=30
        )

        response.raise_for_status()

        records = response.json()

        if not records:
            logger.info("No more pages.")
            break

        logger.info(
            f"Downloaded {len(records)} records from page {page}"
        )

        all_records.extend(records)

        page += 1

    logger.info(
        f"Total downloaded records: {len(all_records)}"
    )

    return all_records

#########################################################
# Validation
#########################################################

def validate(data):

    logger.info("Validating data...")

    if not isinstance(data, list):
        raise ValueError("API did not return a list.")

    if len(data) == 0:
        raise ValueError("API returned an empty dataset.")

    logger.info("Validation successful.")

#########################################################
# Upload
#########################################################

def upload(data, bucket_name):

    logger.info("Preparing upload...")

    timestamp = datetime.now(timezone.utc)

    key = (
        f"{S3_PREFIX}/"
        f"{timestamp:%Y/%m/%d/%H%M%S}.json"
    )

    json_data = json.dumps(
        data,
        ensure_ascii=False,
        indent=2
    )

    s3 = get_s3_client()

    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=json_data,
        ContentType="application/json"
    )

    logger.info(
        f"Uploaded file to s3://{bucket_name}/{key}"
    )

#########################################################
# Main
#########################################################

def main():

    logger.info("Glue Job started.")

    args = get_job_arguments()

    bucket_name = args["BUCKET_NAME"]
    api_key = args["API_KEY"]

    data = get_data(api_key)

    validate(data)

    upload(
        data=data,
        bucket_name=bucket_name
    )

    logger.info("Glue Job finished successfully.")

#########################################################
# Entry Point
#########################################################

if __name__ == "__main__":

    try:

        main()

    except Exception as e:

        logger.exception(f"Glue Job failed: {e}")

        raise
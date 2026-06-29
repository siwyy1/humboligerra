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

S3_PREFIX = "bronze/coingecko/coin_details"

URL = "https://api.coingecko.com/api/v3/coins"

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
            "API_KEY",
            "COINS"
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

def get_data(api_key, coins):

    logger.info("Starting CoinGecko Coin Details download...")

    all_records = []

    for coin in coins:

        logger.info(f"Downloading {coin}")

        response = requests.get(
            f"{URL}/{coin}",
            headers={
                "x-cg-demo-api-key": api_key
            },
            timeout=30
        )

        response.raise_for_status()

        all_records.append(
            response.json()
        )

    logger.info(
        f"Downloaded {len(all_records)} coins."
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

    logger.info("Uploading data to S3...")

    s3 = get_s3_client()

    timestamp = datetime.now(timezone.utc)

    for coin in data:

        coin_id = coin["id"]

        key = (
            f"{S3_PREFIX}/"
            f"{timestamp:%Y-%m-%d}/"
            f"{coin_id}.json"
        )

        json_data = json.dumps(
            coin,
            ensure_ascii=False,
            indent=2
        )

        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json_data,
            ContentType="application/json"
        )

        logger.info(
            f"Uploaded {coin_id} to s3://{bucket_name}/{key}"
        )

#########################################################
# Main
#########################################################

def main():

    logger.info("Glue Job started.")

    args = get_job_arguments()

    bucket_name = args["BUCKET_NAME"]
    api_key = args["API_KEY"]

    coins = [
        coin.strip()
        for coin in args["COINS"].split(",")
    ]

    data = get_data(
        api_key=api_key,
        coins=coins
    )

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
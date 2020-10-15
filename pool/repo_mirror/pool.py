from typing import List
from pathlib import Path
from boto3.s3 import transfer
import boto3
import logging


_logger = logging.getLogger(__name__)


def upload_files(aws_bucket: str,
                 monthly_directory: str,
                 all_tarballs: List[Path]):
    upload_config = transfer.TransferConfig(
        max_concurrency=10,
        use_threads=True
    )
    s3 = boto3.client('s3')
    for tar in all_tarballs:
        name = tar.parts[-1]
        s3.upload_file(
            tar.absolute().as_posix(),
            aws_bucket,
            f'{monthly_directory}/{name}',
            ExtraArgs={'ACL': 'public-read'},
            Config=upload_config
        )
        _logger.info(f'uploaded {tar} to {aws_bucket}')


import logging


def define_logging_facility():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
        handlers=[
            logging.FileHandler(
                f'/opt/anaconda/accord.log',
                mode='a',
                encoding='utf-8',
                delay=1
            ),
            logging.StreamHandler()
        ]
    )
    logging.getLogger('sh').setLevel(logging.ERROR)
    return logging.getLogger()

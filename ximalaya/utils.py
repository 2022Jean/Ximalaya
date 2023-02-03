import logging


logging.basicConfig(level=logging.INFO,
                    filename='ximalaya.log',
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')


def log_print(message, *args, **kwargs) -> None:

    logging.info(message, *args, **kwargs)
    print(message)

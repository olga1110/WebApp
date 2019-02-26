import sys
import logging
from logging.handlers import TimedRotatingFileHandler

def create_log(path):

    logger = logging.getLogger("comment_log")
    logger.setLevel(logging.DEBUG)
    _format = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
    f_handler = logging.handlers.TimedRotatingFileHandler(path, when='D',
                                               interval=1, backupCount=31)
    f_handler.setFormatter(_format)
    f_handler.setLevel(logging.DEBUG)
    logger.addHandler(f_handler)

    s_handler = logging.StreamHandler(sys.stdout)
    s_handler.setLevel(logging.DEBUG)
    s_handler.setFormatter(_format)
    logger.addHandler(s_handler)
    return logger


# if __name__ == "__main__":
#     logger = create_log('comment_log.log')








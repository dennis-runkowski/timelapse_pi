""" Base Class for the Timelaspe. """

import logging
import redis


class Base:
    """Base class for timelapse."""

    def __init__(self, storage_path, redis_status=False, camera_rotate=0,
                 res=(3280, 2464), log_level="INFO"):
        """Instantiate the base class.

        Args:
            storage_path (str): Path to storage pictures
            redis_status (bool): Track the progress in redis
            camera_rotate (int): Int to rotate the camera
            res (tuple): Tuples containing the resolution, default is 4k
            log_level (str): logging level, default is info
        """
        self.log = self._setup_logging(__name__, log_level)
        self.resolution = res
        self.storage_path = storage_path
        self.redis_conn = None
        self.camera_rotate = camera_rotate
        if redis_status:
            self._connect_redis()

    def _connect_redis(self):
        """Method to connect to redis."""
        self.redis_conn = redis.StrictRedis(
            host='localhost',
            port=6379,
            db=0,
            charset="utf-8",
            decode_responses=True
        )

    def _setup_logging(self, name, level):
        """Method to setup logger.

        Args:
            name (str): Name of the logger
            level (str): log level
        Returns:
            obj logger
        """
        log = logging.getLogger(name)
        log.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )
        ch = logging.StreamHandler()
        ch.setLevel(level=level)
        ch.setFormatter(formatter)

        log.addHandler(ch)
        return log

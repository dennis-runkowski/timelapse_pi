"""Automate taking pictures on your raspberry pi"""

import os
import logging
import glob
import shutil
import datetime
import uuid
import json
from time import sleep
from timelapse.base import Base
try:
    import picamera
except:
    #TODO
    pass


class PiCameraWrapper(Base):
    """Class to capture pictures on raspberry pi."""

    def __init__(self, storage_path, redis_status=False, camera_rotate=0,
                 res=(3280, 2464), log_level="INFO"):
        super().__init__(
            storage_path,
            redis_status,
            camera_rotate,
            res=(3280, 2464),
            log_level="INFO"
        )
        self._connect_camera()

    def take_pictures(self, job_name, frequency, length):
        """Take pictures with your raspberry pi camera.

        The progress and stats are stored in redis.

        Args:
            job_name (str): Name of the job, this is used as the redis key
            frequency (int): How often to take pictures in seconds
            length (int): Duration to take pictures in minutes
        Returns:
            dict
        """
        if not isinstance(frequency, int):
            self.log.error("frequency must be an int")
            raise TypeError("Please use an integer for the frequency")
        if not isinstance(length, int):
            self.log.error("length must be an int")
            raise TypeError("Please use an integer for the length")

        # convert minutes to seconds
        length_secs = int(length * 60)
        picture_count = int(length_secs / frequency)

        # Check that there is enough storage
        free_space = self.check_pi_storage(self.storage_path)
        estimated_space = round(self.file_size_est * picture_count, 2)

        self.log.info("Estimated job size {}".format(estimated_space))

        if self.redis_conn:
            redis_name = "timelapse_job_{}".format(job_name)
            job_config = {
                "name": job_name,
                "status": "Running",
                "percent_done": 0.0,
                "frequency": frequency,
                "length": length,
                "resolution": str(self.resolution),
                "storage_path": self.storage_path,
                "estimated_size": estimated_space,
                "picture_count": 0
            }
        if estimated_space > free_space:
            self.log.warn("There is not enough storage to complete this job!")
            message = "Not enough storage, this job will take about {}".format(
                estimated_space
            )
            if self.redis_conn:
                job_config["status"] = "Cancelled"
                self.redis_conn.set(
                    redis_name,
                    json.dumps(job_config)
                )
            return {
                "status": "error",
                "message": message
            }
        self.log.info("Starting to take {} pictures".format(picture_count))
        try:
            for i in range(0, picture_count):
                self.log.info("Status {}/{} done".format(i, picture_count))

                if self.redis_conn:
                    job_config["percent_done"] = round(
                        float(i/picture_count) * 100.00, 2
                    )
                    job_config["picture_count"] = i
                    if self.redis_conn.get("stop_job") == job_name:
                        job_config["status"] = "Cancelled"
                        self.redis_conn.set(
                            redis_name,
                            json.dumps(job_config)
                        )
                        self.redis_conn.set("stop_job", "no")
                        self.redis_conn.set("jobs_running", "no")
                        return {"status": "done", "message": "cancelled"}

                    self.redis_conn.set(redis_name, json.dumps(job_config))

                file_name = "{}/{}_{}.jpg".format(
                    self.storage_path,
                    job_name,
                    i
                )

                self.camera.capture(file_name)
                sleep(frequency)
        except Exception as e:
            self.log.error("Error taking pictures %r", e)
            if self.redis_conn:
                job_config["status"] = "Error"
                self.redis_conn.set(
                    redis_name,
                    json.dumps(job_config)
                )
                self.redis_conn.set("stop_job", "no")
                self.redis_conn.set("jobs_running", "no")
            return {"status": "error", "message": "error"}
        self.log.info("Completed taking pictures")
        if self.redis_conn:
            job_config["percent_done"] = 100
            job_config["status"] = "Completed"
            job_config["picture_count"] = picture_count
            self.redis_conn.set(redis_name, json.dumps(job_config))
            self.redis_conn.set("jobs_running", "no")

        self._disconnect_camera()

        return {"status": "done", "message": "completed"}

    @staticmethod
    def check_pi_storage(storage_path):
        """Static Method Check the amount of free storage left on the pi.

        This will check the storage directory.

        Args:
            storage_path(str): Path to storage files
        Returns:
            int: free gb
        """
        stats = shutil.disk_usage(storage_path)
        free_space = round(stats.free / 1000000000, 2)
        return free_space

    @staticmethod
    def clean_storage(job_name, storage_path):
        """Static Method to remove all the images and mp4.

        Only removes the files in the storage directory that contain the job
        name.

        Args:
            job_name (str): Name of the job
            storage_path(str): Path to storage files
        """
        try:
            safe_name = "{}_".format(job_name)
            for f in os.listdir(storage_path):
                if safe_name in f:
                    if '.jpg' in f or '.mp4' in f:
                        path = "{}/{}".format(
                            storage_path,
                            f
                        )
                    os.remove(path)
        except Exception as e:
            raise e

    def test_picture(self):
        """Take test picture."""
        test_file = "{}/test.jpg".format(self.storage_path)
        self.camera.capture(test_file)

    def _connect_camera(self):
        """Connect to the pi camera."""
        try:
            self.log.info("Connecting to Pi Camera!")
            self.camera = picamera.PiCamera()
            self.camera.resolution = (3280, 2464)
            if self.camera_rotate:
                self.camera.rotation = self.camera_rotate
            self.camera.vflip = True
            self.camera.hflip = True
            test_file = "{}/test.jpg".format(self.storage_path)
            self.camera.capture(test_file)
            self.file_size_est = os.path.getsize(test_file) / 1000000000  # GB
            os.remove(test_file)
        except Exception as e:
            self.log.error("Error connecting to camera %r", e)
            raise e

    def _disconnect_camera(self):
        """Disconnect the pi camera."""
        try:
            if self.camera:
                self.log.info("Disconnecting from the pi camera.")
                self.camera.close()
        except Exception as e:
            self.log.error("Could not disconnect the pi camera - %r", e)
            raise e

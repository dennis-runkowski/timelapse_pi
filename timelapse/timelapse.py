""" Create a timelapse."""

import os
import logging
import glob
import datetime
from time import sleep
import cv2
from timelapse.base import Base


class TimeLapse(Base):
    """Class create a timelapse."""

    def __init__(self, storage_path, res=(3280, 2464), log_level="INFO"):
        super().__init__(storage_path, res=(3280, 2464), log_level="INFO")

    def create_timelapse(self, job_name, fps, save_path):
        """Create timelapse video from pictures.

        Args:
            job_name(str): Name of the job
            fps (int): Frames per second
            save_path (str): Path to save the video
        """
        try:
            self.log.info(
                "Creating timelapse - {} frames per second".format(
                    fps
                )
            )
            save_path = "{}/{}_timelapse.mp4".format(
                self.storage_path,
                job_name
            )
            video_type = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(
                save_path,
                video_type,
                fps,
                self.resolution
            )
            image_list = glob.glob(f"{self.storage_path}/*.jpg")
            sorted_images = sorted(image_list, key=os.path.getmtime)
            for file in sorted_images:
                image_frame = cv2.imread(file)
                writer.write(image_frame)
            self.log.info("Done creating timelapse video")
        except Exception as e:
            self.log.error("Error creating timelapse video")
            raise e

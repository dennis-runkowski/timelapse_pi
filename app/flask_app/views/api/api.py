"""Blueprint for the api."""
import os
import json
import glob
import logging
from flask import Blueprint, jsonify, render_template, url_for, request
from flask import current_app as app
from threading import Thread
import redis
from timelapse import PiCameraWrapper
from timelapse import TimeLapse


# Blue print for the api
api_blueprint = Blueprint(
    "api",
    __name__,
    template_folder="templates",
    static_folder="static"
)


def redis_connection():
    """Connect to redis.

    Returns:
        obj connection to redis
    """
    try:
        redis_conn = redis.StrictRedis(
            host="localhost",
            port=6379,
            db=0,
            charset="utf-8",
            decode_responses=True
        )
    except Exception as e:
        # TODO create a logger
        logging.error(e)
        return None

    return redis_conn


def run_timelapse_job(job_name, storage_path, job_resolution):
    """Method to create timelapse job.

    Args:
        job_name (str): Job name
        storage_path (str): Path to store pictures on pi
        job_resolution (tuple): Tuple with the resolution
    """
    try:
        timelapse_job = TimeLapse(storage_path, job_resolution)
        timelapse_job.create_timelapse(job_name, 5, storage_path)
    except Exception as e:
        logging.error("Error creating timelapse video %r", e)


def run_job(job_name, storage_path, camera_rotate,
            job_resolution, job_frequency, job_length):
    """Method to run job to take pictures on pi.

    Args:
        job_name (str): Job name
        storage_path (str): Path to store pictures on pi
        camera_rotate (int): Int to rotate the pi
        job_resolution (tuple): Tuple with the resolution
        job_frequency (int): Frequency to take pictures (sec)
        job_lenght (int): Length to take pictures (min)
    """
    details = {
        "name": job_name,
        "status": "Running",
        "percent_done": 0.0,
        "frequency": job_frequency,
        "length": job_length,
        "resolution": str(job_resolution),
        "storage_path": storage_path,
        "camera_rotate": camera_rotate,
        "estimated_size": "N/A",
        "picture_count": "N/A"
    }
    try:
        redis_conn = redis_connection()
        redis_conn.set("jobs_running", "yes")
        redis_name = "timelapse_job_{}".format(job_name)
        redis_conn.set(redis_name, json.dumps(details))
        camera_job = PiCameraWrapper(
            storage_path=storage_path,
            redis_status=True,
            camera_rotate=camera_rotate,
            res=job_resolution
        )
        camera_job.take_pictures(
            job_name,
            job_frequency,
            job_length
        )
    except Exception as e:
        logging.error("Error starting camera job %r", e)
        redis_conn.set("jobs_running", "no")
        details = json.loads(redis_conn.get(redis_name))
        details["error_details"] = e
        details["status"] = "Cancelled"
        redis_conn.set(redis_name, json.dumps(details))


@api_blueprint.route("/get_jobs", methods=["GET"])
def get_jobs():
    """Get all the jobs on the pi."""
    data = []
    status = "success"
    try:
        redis_conn = redis_connection()
        for job in redis_conn.scan_iter("timelapse_job_*"):
            data.append(
                json.loads(redis_conn.get(job))
            )
    except Exception as e:
        app.logger.error(e)
        status = "error"
    data = sorted(data, key=lambda i: i.get("status", ""), reverse=True)
    res = {
        "status": status,
        "data": data
    }
    return jsonify(res)


@api_blueprint.route("/get_job/<job_name>", methods=["GET"])
def get_job(job_name):
    """Get job on the pi.

    Args
        job_name (str): Name of the job
    Returns
        dict containg job details
    """
    data = {}
    # pictures = []
    status = "success"
    try:
        redis_conn = redis_connection()
        redis_name = "timelapse_job_{}".format(job_name)
        data = json.loads(redis_conn.get(redis_name))
        data["resolution"] = data.get("resolution")
        # static_dir = "{}/static/img/timelapse/{}/".format(
        #     app.root_path,
        #     job_name
        # )
        base_path = "/static/img/timelapse/{}/{}_".format(job_name, job_name)
        last_img_number = data.get("picture_count", 0)
        if last_img_number:
            last_img_number -= 1

        latest_img = "{}{}.jpg".format(base_path, last_img_number)
        # image_list = glob.glob("{}/{}_*.jpg".format(static_dir, job_name))
        # pictures = sorted(image_list, key=os.path.getmtime, reverse=True)
        # pictures = [i.replace(app.root_path, '') for i in pictures]
    except Exception as e:
        app.logger.error(e)
        status = "error"
    res = {
        "status": status,
        "data": data,
        "img_pagination": {
            "base_path": base_path,
            "last_back": last_img_number,
            "latest_picture": latest_img
        }
    }
    return jsonify(res)


@api_blueprint.route("/stop_job/<job_name>", methods=["POST"])
def stop_job(job_name):
    """
    Stop job

    Args:
        job_name (str): Name of the job to delete
    """
    redis_conn = redis_connection()
    redis_conn.set("stop_job", job_name)
    return jsonify({"status": "success", "message": "Stopping job."})


@api_blueprint.route("/delete_job/<job_name>", methods=["POST"])
def delete_job(job_name):
    """
    Delete job and all the data

    Args:
        job_name (str): Name of the job to delete
    """
    redis_conn = redis_connection()
    redis_name = "timelapse_job_{}".format(job_name)
    job_data = json.loads(redis_conn.get(redis_name))
    if job_data.get("status") == "Running":
        return jsonify({
            "status": "error",
            "message": "Please stop the job before deleting."
            })
    # Delete files
    try:
        PiCameraWrapper.clean_storage(job_name, job_data["storage_path"])
    except Exception as e:
        app.logger.error(e)
        return jsonify({
            "status": "error",
            "message": "Could not delete storage."
        })
    static_dir = "{}/static/img/timelapse/{}".format(
        app.root_path,
        job_name
    )
    try:
        os.unlink(static_dir)
    except Exception as e:
        app.logger.error("could not remove symlink - %r", e)
    redis_conn.delete(redis_name)
    return jsonify({"status": "success", "message": "Deleted!"})


@api_blueprint.route("/create_job", methods=["POST"])
def create_job():
    """Create timelapse job on pi."""
    data = request.form
    job_name = data.get("job_name", None)
    storage_dir = data.get("storage_dir", None)
    job_resolution = data.get("job_resolution", None)
    job_frequency = data.get("job_frequency", None)
    job_length = data.get("job_length", None)
    camera_rotate = data.get("camera_rotate", None)
    redis_conn = redis_connection()
    redis_name = "timelapse_job_{}".format(job_name)

    # Validate form
    errors = {}
    status = 0
    if not job_name:
        status = 1
        errors["#job_name_error"] = "Please enter a job name!"

    # remove spaces from job name
    job_name = job_name.replace(" ", "_")

    duplicate_check = redis_conn.get(redis_name)
    if duplicate_check:
        status = 1
        errors["#job_name_error"] = "A job with this name already exists!"

    if not storage_dir:
        status = 1
        errors["#storage_dir_error"] = "Please enter a storage path!"

    # Test if the storage_dir exists
    if not os.path.isdir(storage_dir):
        status = 1
        errors["#storage_dir_error"] = "This storage path does not exist!"

    # TODO check if there is enough space

    if not job_resolution:
        status = 1
        errors["#job_resolution_error"] = "Please enter a job resolution!"

    # Job resolution has to be a tuple
    try:
        job_resolution = tuple(job_resolution)
    except Exception as e:
        app.logger.warn("Job resolution bad format - {}".format(e))

    if not isinstance(job_resolution, tuple):
        status = 1
        error_message_res = "Job resolution must be a tuple (3280, 2464)!"
        errors["#job_resolution_error"] = error_message_res

    if not job_frequency:
        status = 1
        errors["#job_frequency_error"] = "Please enter a job frequency!"
    try:
        job_frequency = int(job_frequency)
    except Exception as e:
        app.logger.warn("Job frequency bad format- {}".format(e))

    # Job frequency has to be a int
    if not isinstance(job_frequency, int):
        status = 1
        errors["#job_frequency_error"] = "Job resolution must be type int!"

    if not job_length:
        status = 1
        errors["#job_length_error"] = "Please enter a job length!"
    try:
        job_length = int(job_length)
    except Exception as e:
        app.logger.warn("Job length bad format- {}".format(e))

    # Camera Rotation has to be a int
    try:
        camera_rotate = int(camera_rotate)
    except Exception as e:
        app.logger.warn("camera_rotate bad format- {}".format(e))

    if not isinstance(camera_rotate, int):
        status = 1
        errors["#job_camera_rotate_error"] = "Camera Rotate must be type int!"

    if camera_rotate not in [0, 90, 180, 270, 360]:
        status = 1
        errors["#job_camera_rotate_error"] = "Rotate Camera must be 0, 90," \
            " 180, 270 or 360"

    # Job length has to be a int
    if not isinstance(job_length, int):
        status = 1
        errors["#job_length_error"] = "Job length must be type int!"

    # Check if there is a job running
    running_job = redis_conn.get("jobs_running")
    if running_job == "yes":
        status = 1
        error_run = "There is a job running please wait to start a new job!"
        errors["#job_name_error"] = error_run

    if status == 1:
        return jsonify({"status": "error", "message": errors})

    # Create symlink storage path to the static folder
    try:
        static_dir = "{}/static/img/timelapse/{}".format(
            app.root_path,
            job_name
        )
        os.symlink(storage_dir, static_dir)
    except Exception as e:
        status = 1
        app.logger.error("Could not create symlink - %r", e)
        error_sym = "Could not create symlink, check the server logs."
        errors["#storage_dir_error"] = error_sym

    if status == 1:
        return jsonify({"status": "error", "message": errors})

    # Start Thread with job
    try:
        job_thread = Thread(target=run_job, args=(
            job_name,
            storage_dir,
            camera_rotate,
            job_resolution,
            job_frequency,
            job_length
        ))
        job_thread.name = job_name
        job_thread.setDaemon(True)
        job_thread.start()
    except Exception as e:
        app.logger.error("Error starting job- %r", e)
        error_connection = "Could not make pi camera connection."
        errors["#job_name_error"] = error_connection
        return jsonify({"status": "error", "message": error_connection})
    return jsonify({"status": "success", "message": ""})


@api_blueprint.route("/create_timelapse/<job_name>", methods=["GET"])
def create_timelapse(job_name):
    """
    Create timelapse video

    Args:
        job_name (str): Name of the job to delete
    """
    redis_conn = redis_connection()
    redis_name = "timelapse_job_{}".format(job_name)
    job_data = json.loads(redis_conn.get(redis_name))
    storage_dir = job_data.get("storage_path", None)
    job_resolution = tuple(job_data.get("resolution", (3280, 2464)))

    if job_data.get("status", "") != "Completed":
        return jsonify({
            "status": "error",
            "message": "This Job is still running!"
        })

    # Start Thread with job
    job_thread = Thread(target=run_timelapse_job, args=(
        job_name,
        storage_dir,
        job_resolution
    ))
    job_thread.name = "timelapse_job"
    job_thread.setDaemon(True)
    job_thread.start()
    return jsonify({
        "status": "success",
        "message": "Creating your timelapse!"
    })

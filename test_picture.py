from timelapse import PiCameraWrapper

camera_job = PiCameraWrapper(
    storage_path='./',
    res=(3280, 2464)
)
camera_job.test_picture()

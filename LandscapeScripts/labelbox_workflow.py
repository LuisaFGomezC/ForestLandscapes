
import os
from labelbox import Client
import labelbox
from matplotlib import pyplot as plt
from IPython.display import clear_output
import numpy as np
import json
import ndjson
import requests
import cv2
from typing import Dict, Any

API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJjbHRoYjZ4d2cwNXA3MDcxMGMzeTk1bTZjIiwib3JnYW5pemF0aW9uSWQiOiJjanF6bGVoNHcweGhxMDc3N2dqNDF0cHNrIiwiYXBpS2V5SWQiOiJjbHVyNWM2cHYwM3E3MDd6YjFtYzJoMDQ1Iiwic2VjcmV0IjoiMzhiNDM0ODNhN2JmMjg1ZjM1NjA5MzdiNTU5M2VlODAiLCJpYXQiOjE3MTI1OTI0NjksImV4cCI6MjM0Mzc0NDQ2OX0.SMSSj5PU2Xm-dmuMeyPWQ-GUf26vwEGOwqSMdJdjnEU"

client = labelbox.Client(api_key=API_KEY)
params = {
	"data_row_details": True,
	"metadata_fields": True,
	"attachments": True,
	"project_details": True,
	"performance_details": True,
	"label_details": True,
	"interpolated_frames": True
}

project = client.get_project('cltj2i26q09vj07yn62gd5q3b')
export_task = project.export_v2(params=params)

export_task.wait_till_done()
if export_task.errors:
	print(export_task.errors)
export_json = export_task.result

if not os.path.exists('timeseries_videos'):
    os.makedirs('timeseries_videos')

for i in range(len(export_json)):
    export_url = export_json[i]["data_row"]["row_data"]
    video_name = export_json[i]["data_row"]["external_id"]

    # Download the video
    with open("video.mp4", "wb") as f:
        f.write(requests.get(export_url).content)

    vidcap=cv2.VideoCapture("video.mp4")
    success, image = vidcap.read()

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    out = cv2.VideoWriter(f'timeseries_videos/{video_name}.mp4', fourcc, 1, (image.shape[1], image.shape[0]))

    if image is not None:
        image= image[:,:, ::-1]
    count=1
    while success and count<90:
        if image is not None:
            plt.figure(1)
            plt.imshow(image)
            plt.pause(0.1)
            plt.clf()
            # Write the frame into the file 'output.mp4'
            out.write(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        success, image = vidcap.read()
        if image is not None:
            image= image[:,:, ::-1]
        count += 1
        if success and count<10:
            clear_output(wait=True)

    # Release everything after the job is finished
    out.release()
    vidcap.release()
    cv2.destroyAllWindows()

    # Delete the temporary video file
    os.remove("video.mp4")
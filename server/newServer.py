from fastapi import FastAPI
# from pydantic import BaseModel
# from typing import List, Dict, Any
# import uvicorn
from scraperMain import imageScraper
# from fastapi import Query
# import shutil
# import threading
# import time
# import os 

#Import functions from processor.py
from newProcessor import (
   resize_image, color_convert, gaussian_blur, rotate_image,
   adjust_brightness, adjust_contrast, adjust_saturation, flip_image, coreProcessor )
# def delete(path):
#     try:
#         time.sleep(300)  # wait for 5 minutes (300 seconds)

#         if os.path.isfile(path):
#             os.remove(path)
#             print(f"Deleted file: {path}")
#         elif os.path.isdir(path):
#             shutil.rmtree(path)
#             print(f"Deleted folder: {path}")
#         else:
#             print(f"Path does not exist: {path}")

#     except Exception as e:
#         print(f"Error deleting {path}: {e}")

# app = FastAPI()
# TEMP_FOLDER = "./temp_files"

# # Create a folder for temp files if it doesn't exist
# if not os.path.exists(TEMP_FOLDER):
#     os.makedirs(TEMP_FOLDER)

# # Function to zip a folder
# def create_zip_from_folder(folder_path, zip_filename):
#     with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
#         for root, dirs, files in os.walk(folder_path):
#             for file in files:
#                 zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_path))

# global latest_input_folder 
# global latest_output_folder

# # Define request body structure
# class ProcessRequest(BaseModel):
#     query: str
#     num_images: int
#     selected_steps: List[str]
#     params: Dict[str, Any]
# # Map step numbers to function names and functions
# step_map = {
#     "1": ("resize", resize_image),
#     "2": ("colorconvert", color_convert),
#     "3": ("gaussianblur", gaussian_blur),
#     "4": ("rotate", rotate_image),
#     "5": ("brightness", adjust_brightness),
#     "6": ("contrast", adjust_contrast),
#     "7": ("saturation", adjust_saturation),
#     "8": ("flip", flip_image),
# }

# @app.post("/process")
# async def process_images(request: ProcessRequest):
#     query = request.query
#     num_images = request.num_images
#     selected_steps = request.selected_steps
#     params = request.params

#     print(query)
#     print(num_images)
#     print(selected_steps)


#     #scrape
#     folder = imageScraper(query, num_images)
#    # latest_input_folder = folder

#     # preprocess
#     op_folder = coreProcessor(folder, selected_steps, step_map, params)
#     #latest_output_folder = op_folder

#     print(op_folder)
#     # Zip
#     zip_path = f"{op_folder}.zip"
#     shutil.make_archive(op_folder, 'zip', op_folder)

#     # Schedule deletion after 5 minutes
#     threading.Thread(target=delete, args=(folder,), daemon=True).start()
#     threading.Thread(target=delete, args=(op_folder,), daemon=True).start()
#     threading.Thread(target=delete, args=(zip_path,), daemon=True).start()


#     download_link = f"http://localhost:8000/download?file={os.path.basename(zip_path)}"
#     return {"message": "Processing done!", "download_link": download_link}



# @app.get("/")
# async def say():
#     print("a request to the server received")
#     return {
#         "message":"Welcome to the scraper"
#     }


# if __name__ == "__main__":
#     import multiprocessing
   
#     multiprocessing.freeze_support()
#     uvicorn.run("newServer:app", host="0.0.0.0", port=8000, reload=True)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify frontend URL e.g., ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods: GET, POST, OPTIONS, etc.
    allow_headers=["*"],  # Allow all headers
)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
from scraperMain import imageScraper
import shutil
import threading
import time
import os
import zipfile
from fastapi.responses import FileResponse

# Function to delete files/folders after a delay
def delete(path):
    try:
        time.sleep(30)  # wait for 5 minutes (300 seconds)

        if os.path.isfile(path):
            os.remove(path)
            print(f"Deleted file: {path}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"Deleted folder: {path}")
        else:
            print(f"Path does not exist: {path}")

    except Exception as e:
        print(f"Error deleting {path}: {e}")

app = FastAPI()


# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify frontend URL e.g., ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods: GET, POST, OPTIONS, etc.
    allow_headers=["*"],  # Allow all headers
)

TEMP_FOLDER = "./temp_files"

# Create a folder for temp files if it doesn't exist
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

# Function to zip a folder
def create_zip_from_folder(folder_path, zip_filename):
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_path))

# Define request body structure
class ProcessRequest(BaseModel):
    query: str
    num_images: int
    selected_steps: List[str]
    params: Dict[str, Any]

# Map step numbers to function names and functions
step_map = {
    "1": ("resize", resize_image),
    "2": ("colorconvert", color_convert),
    "3": ("gaussianblur", gaussian_blur),
    "4": ("rotate", rotate_image),
    "5": ("brightness", adjust_brightness),
    "6": ("contrast", adjust_contrast),
    "7": ("saturation", adjust_saturation),
    "8": ("flip", flip_image),
}

@app.post("/process")
async def process_images(request: ProcessRequest):
    query = request.query
    num_images = request.num_images
    selected_steps = request.selected_steps
    params = request.params
    print(selected_steps)
    print(params)
    # Scrape images
    folder = imageScraper(query, num_images)

    # Preprocess images
    op_folder = coreProcessor(folder, selected_steps, step_map, params)

    # Zip the output folder
    zip_filename = f"{TEMP_FOLDER}/{os.path.basename(op_folder)}.zip"
    create_zip_from_folder(op_folder, zip_filename)

    # Schedule deletion after 5 minutes
    threading.Thread(target=delete, args=(folder,), daemon=True).start()
    threading.Thread(target=delete, args=(op_folder,), daemon=True).start()
    threading.Thread(target=delete, args=(zip_filename,), daemon=True).start()

    # Generate the download link
    download_link = f"http://localhost:8000/download/{os.path.basename(zip_filename)}"
    return {"message": "Processing done!", "download_link": download_link}

@app.get("/download/{filename}")
async def download_zip(filename: str):
    zip_path = os.path.join(TEMP_FOLDER, filename)

    # Ensure the file exists
    if os.path.exists(zip_path):
        return FileResponse(zip_path, media_type='application/zip', filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/")
async def say():
    return {"message": "Welcome to the scraper"}

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    uvicorn.run("newServer:app", host="127.0.0.1", port=8000, reload=True)

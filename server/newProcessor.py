import os
import cv2
import numpy as np
from tqdm import tqdm
import shutil 
import time # For copying original images

# ====== Define processing functions ======

def resize_image(img, width, height):
    print("resizing")
    return cv2.resize(img, (width, height))

def color_convert(img, code):
    return cv2.cvtColor(img, code)

def gaussian_blur(img, kernel_size):
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

def rotate_image(img, angle):
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(img, M, (w, h))

def adjust_brightness(img, factor):
    return cv2.convertScaleAbs(img, alpha=factor, beta=0)

def adjust_contrast(img, factor):
    return cv2.convertScaleAbs(img, alpha=factor, beta=0)

def adjust_saturation(img, factor):
    if len(img.shape) == 2 or img.shape[2] == 1:
            # Image is grayscale, skip saturation
        return img
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] *= factor
    hsv[..., 1] = np.clip(hsv[..., 1], 0, 255)
    hsv = hsv.astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def flip_image(img, flip_code):
    return cv2.flip(img, flip_code)


# ====== Process images ======
def coreProcessor(input_folder,selected_steps,step_map,params):
    output_folder = "./processedimg"
    os.makedirs(output_folder, exist_ok=True)
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    print(f"\n🔄 Processing {len(image_files)} images...")

    for img_file in tqdm(image_files):
        img_path = os.path.join(input_folder, img_file)
        img = cv2.imread(img_path)

        if img is None:
            print(f"❌ Failed to read {img_file}")
            continue

        filename_no_ext = os.path.splitext(img_file)[0]

        # ✅ Copy the original image to output folder
        shutil.copy(img_path, os.path.join(output_folder, f"{filename_no_ext}_original.jpg"))

        suffix_list = []
        processed_img = img

        for step_num in selected_steps:
            print("We are in a for loop")
            time.sleep(1)
            print(step_num)
            #step_num = step_num.strip()
            if step_num not in step_map:
                print("Step number checking is not in step map = is true we're skipping",step_num)
                continue
            step_name, func = step_map[step_num]
            step_name = step_name.strip().lower()
            suffix_list.append(step_name)

            print(step_name)
            # Apply step with relevant parameters
            if step_name == "resize":
                print("resizze was found true")
                processed_img = func(processed_img, params['resize'][0], params['resize'][1])
            elif step_name == "colorconvert":
                processed_img = func(processed_img, params['colorconvert'])
            elif step_name == "gaussianblur":
                processed_img = func(processed_img, params['gaussianblur'])
            elif step_name == "rotate":
                processed_img = func(processed_img, params['rotate'])
            elif step_name == "brightness":
                processed_img = func(processed_img, params['brightness'])
            elif step_name == "contrast":
                processed_img = func(processed_img, params['contrast'])
            elif step_name == "saturation":
                processed_img = func(processed_img, params['saturation'])
            elif step_name == "flip":
                processed_img = func(processed_img, params['flip'])

            # Save intermediate step image
            step_suffix = "_".join(suffix_list)
            step_filename = f"{filename_no_ext}_{step_suffix}.jpg"
            step_save_path = os.path.join(output_folder, step_filename)
            cv2.imwrite(step_save_path, processed_img)

    print(f"\n✅ Done! All processed images (including originals) are saved in: {output_folder}")
    return output_folder
   

import os
import cv2
import numpy as np
from tqdm import tqdm
import shutil  # For copying original images

# ====== Define processing functions ======

def resize_image(img, width, height):
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
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[...,1] *= factor
    hsv[...,1] = np.clip(hsv[...,1], 0, 255)
    hsv = hsv.astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def flip_image(img, flip_code):
    return cv2.flip(img, flip_code)

# ====== Ask user for folders ======
input_folder = input("📂 Enter path to folder with downloaded images: ").strip()
output_folder = input("💾 Enter path to save processed dataset: ").strip()
os.makedirs(output_folder, exist_ok=True)

# ====== Show processing options ======
print("\nSelect preprocessing steps by entering their numbers in order (comma separated):")
print("1. resize")
print("2. colorconvert")
print("3. gaussianblur")
print("4. rotate")
print("5. brightness")
print("6. contrast")
print("7. saturation")
print("8. flip")

selected_steps = input("\nEnter step numbers in sequence (e.g., 1,2,5,8): ").strip().split(",")

# ====== Get parameters for each selected step ======
params = {}

if "1" in selected_steps:
    width = int(input("Enter width for resizing: "))
    height = int(input("Enter height for resizing: "))
    params['resize'] = (width, height)

if "2" in selected_steps:
    print("Color Convert Options:")
    print("1: BGR2GRAY")
    print("2: BGR2HSV")
    color_code_input = input("Enter color code option (1 or 2): ")
    color_code = cv2.COLOR_BGR2GRAY if color_code_input == "1" else cv2.COLOR_BGR2HSV
    params['colorconvert'] = color_code

if "3" in selected_steps:
    kernel_size = int(input("Enter kernel size for Gaussian blur (odd number like 3,5,7): "))
    if kernel_size % 2 == 0:
        print("⚠️ Kernel size should be odd. Adding 1 to make it odd.")
        kernel_size += 1
    params['gaussianblur'] = kernel_size

if "4" in selected_steps:
    angle = int(input("Enter angle for rotation (e.g., 90, 180): "))
    params['rotate'] = angle

if "5" in selected_steps:
    brightness_factor = float(input("Enter brightness factor (e.g., 1.2 for brighter, 0.8 for darker): "))
    params['brightness'] = brightness_factor

if "6" in selected_steps:
    contrast_factor = float(input("Enter contrast factor (e.g., 1.5 for more contrast, 0.7 for less): "))
    params['contrast'] = contrast_factor

if "7" in selected_steps:
    saturation_factor = float(input("Enter saturation factor (e.g., 1.5 for more, 0.7 for less): "))
    params['saturation'] = saturation_factor

if "8" in selected_steps:
    print("Flip options:")
    print("0: Vertical Flip")
    print("1: Horizontal Flip")
    print("-1: Both axes Flip")
    flip_code = int(input("Enter flip code (0, 1, -1): "))
    params['flip'] = flip_code

# ====== Map step numbers to names and functions ======
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

# ====== Process images ======
#def coreProcessor(input_folder):
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
        step_num = step_num.strip()
        if step_num not in step_map:
            continue
        step_name, func = step_map[step_num]
        suffix_list.append(step_name)

        # Apply step with relevant parameters
        if step_name == "resize":
            processed_img = func(processed_img, *params['resize'])
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

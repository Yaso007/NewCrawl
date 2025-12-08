import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from urllib.parse import quote

# ========== USER INPUT ==========
query = input("🔍 Enter image search term: ")
num_images = int(input("🖼️ Enter number of images to download: "))

# ========== SETUP ==========
output_dir = f"images_{query.replace(' ', '_')}"
os.makedirs(output_dir, exist_ok=True)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

driver = webdriver.Chrome(options=chrome_options)
search_url = f"https://commons.wikimedia.org/w/index.php?search={quote(query)}&title=Special:MediaSearch&type=image"
driver.get(search_url)

image_urls = set()
scroll_pause = 3
max_scrolls = 30  # increase scroll attempts

print("📜 Scrolling and collecting image URLs...")

for _ in range(max_scrolls):
    # Scroll down
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause)

    # Collect image elements
    thumbnails = driver.find_elements(By.CLASS_NAME, "sd-image")
    for thumb in thumbnails:
        try:
            ##img = thumb.find_element(By.TAG_NAME, "img")
            src = thumb.get_attribute("src") or img.get_attribute("data-src")
            if src and src.startswith("http") and "upload.wikimedia.org" in src:
                image_urls.add(src)
                print(src)
        except:
            continue

    print(f"🔗 Collected {len(image_urls)} image links...")

    if len(image_urls) >= num_images:
        break

driver.quit()

# ========== DOWNLOAD ==========
download_count = min(num_images, len(image_urls))
print(f"\n📥 Downloading {download_count} images...\n")
print("Image URLs to download:", image_urls)
for i, url in enumerate(tqdm(list(image_urls)[:download_count], desc="Downloading")):
    try:
        print("Downloading URL:", url)
        response = requests.get(url, timeout=10)
        print("THE RESPONSE IS : ",response.content)
        with open(os.path.join(output_dir, f"{query.replace(' ', '_')}_{i+1}.jpg"), "wb") as f:
            f.write(response.content)
    except Exception as e:
        tqdm.write(f"[!] Failed to download {url[:50]}... Reason: {e}")

print(f"\n✅ Done! Saved {download_count} images to: {output_dir}")

import os
import time
import requests
from tqdm import tqdm
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Initialize Selenium driver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

# ===== Picjumbo Images =====
def scrape_picjumbo(query, total_images, dest_folder, start_num):
    driver = init_driver()
    base_url = f"https://picjumbo.com/search/{query.lower().replace(' ', '-')}/"
    image_urls = set()
    page_number = 1
    scroll_pause_time = 2

    print("\n🔎 Scraping Picjumbo Images...")
    while len(image_urls) < total_images:
        page_url = base_url if page_number == 1 else f"{base_url.rstrip('/')}/page/{page_number}/"
        print(f"🌐 Visiting: {page_url}")
        driver.get(page_url)
        time.sleep(scroll_pause_time)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        picture_tags = soup.find_all("picture")

        new_images_found = 0
        for picture in picture_tags:
            img = picture.find("img")
            if img and img.get("class") == ["image"]:
                src = img.get("src")
                if src:
                    if src.startswith("//"):
                        src = "https:" + src
                    elif src.startswith("/"):
                        src = urljoin("https://picjumbo.com", src)
                    if src not in image_urls:
                        image_urls.add(src)
                        new_images_found += 1

            if len(image_urls) >= total_images:
                break

        if new_images_found == 0:
            print("⚠️ No new images found on this page. Stopping further scraping.")
            break

        page_number += 1

    driver.quit()

    download_count = min(total_images, len(image_urls))
    print(f"\n📥 Downloading {download_count} Picjumbo images...\n")

    for i, url in enumerate(tqdm(list(image_urls)[:download_count], desc="Downloading Picjumbo")):
        download_image(url, dest_folder, start_num + i)

    return download_count

# ===== Wikimedia Images =====
def scrape_wikimedia(query, total_images, dest_folder, start_num):
    driver = init_driver()
    search_url = f"https://commons.wikimedia.org/w/index.php?search={quote(query)}&title=Special:MediaSearch&type=image"
    driver.get(search_url)

    image_urls = set()
    scroll_pause = 3
    max_scrolls = 50

    print("\n🔎 Scraping Wikimedia Images...")
    for _ in range(max_scrolls):
        print(len(image_urls))
        if len(image_urls) >= total_images:
            print(f"✅ Reached target of {total_images} images. Stopping scroll.")
            break  # ✅ Stop scrolling once enough images are collected

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)

        try:
            load_more_button = driver.find_element(By.CLASS_NAME, "sdms-load-more")
            if load_more_button.is_displayed():
                driver.execute_script("arguments[0].click();", load_more_button)
                print(f"🔘 Clicked 'Load more' button (Scroll {scroll_num+1}).")
                time.sleep(scroll_pause)
        except Exception as e:
            print("ℹ️ No 'Load more' button found this round.")

        thumbnails = driver.find_elements(By.CLASS_NAME, "sd-image")
        for thumb in thumbnails:
            if len(image_urls) >= total_images:
                break  # ✅ Stop collecting further if target met
            try:
                src = thumb.get_attribute("src")
                if src and src.startswith("http") and "upload.wikimedia.org" in src:
                    image_urls.add(src)
            except:
                continue

        print(f"🔗 Wikimedia collected {len(image_urls)} image links...")

    driver.quit()

    download_count = min(total_images, len(image_urls))
    print(f"\n📥 Downloading {download_count} Wikimedia images...\n")

    for i, url in enumerate(tqdm(list(image_urls)[:download_count], desc="Downloading Wikimedia")):
        download_image(url, dest_folder, start_num + i)

    return download_count

# ===== Yahoo Images =====
def scrape_yahoo(query, total_images, dest_folder, start_num):
    driver = init_driver()
    search_url = f"https://images.search.yahoo.com/search/images?p={quote(query)}"
    driver.get(search_url)

    image_urls = set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_pause = 2
    retry_limit = 3
    retry_count = 0

    print("\n🔎 Scraping Yahoo Images...")
    while len(image_urls) < total_images and retry_count < retry_limit:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)

        try:
            show_more_button = driver.find_element(By.CLASS_NAME, "more-res")
            if show_more_button.is_displayed():
                driver.execute_script("arguments[0].click();", show_more_button)
                print("🔘 Clicked 'Show more images' button.")
                time.sleep(2)
        except:
            pass

        thumbnails = driver.find_elements(By.CLASS_NAME, "round-img")
        for thumb in thumbnails:
            try:
                img = thumb.find_element(By.TAG_NAME, "img")
                src = img.get_attribute("src")
                if src and src.startswith("http"):
                    image_urls.add(src)
            except:
                continue

        print(f"🔗 Yahoo collected {len(image_urls)} image links...")

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            retry_count += 1
        else:
            retry_count = 0
        last_height = new_height

    driver.quit()

    download_count = min(total_images, len(image_urls))
    print(f"\n📥 Downloading {download_count} Yahoo images...\n")

    for i, url in enumerate(tqdm(list(image_urls)[:download_count], desc="Downloading Yahoo")):
        download_image(url, dest_folder, start_num + i)

    return download_count

# ===== Download Helper =====
def download_image(img_url, dest_folder, img_num):
    try:
        response = requests.get(img_url, stream=True, timeout=10)
        if response.status_code == 200:
            file_ext = os.path.splitext(img_url)[1].split('?')[0]
            if not file_ext or len(file_ext) > 5:
                file_ext = ".jpg"
            filename = f"{img_num}.jpg"
            file_path = os.path.join(dest_folder, filename)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
    except Exception as e:
        tqdm.write(f"[!] Failed to download {img_url[:50]}... Reason: {e}")

# ===== Main Controller =====
def imageScraper(queryOfImage, numberOfImages):
    query = queryOfImage
    total_images = numberOfImages

    dest_folder = f"./images_{query.replace(' ', '_')}"
    os.makedirs(dest_folder, exist_ok=True)

    downloaded_so_far = 0

    # Step 1: Picjumbo
    picjumbo_count = scrape_picjumbo(query, total_images, dest_folder, downloaded_so_far + 1)
    downloaded_so_far += picjumbo_count

    if downloaded_so_far < total_images:
        # Step 2: Wikimedia
        remaining = total_images - downloaded_so_far
        wikimedia_count = scrape_wikimedia(query, remaining, dest_folder, downloaded_so_far + 1)
        downloaded_so_far += wikimedia_count

    if downloaded_so_far < total_images:
        # Step 3: Yahoo
        remaining = total_images - downloaded_so_far
        yahoo_count = scrape_yahoo(query, remaining, dest_folder, downloaded_so_far + 1)
        downloaded_so_far += yahoo_count

    print(f"\n🎉 All done! Downloaded {downloaded_so_far} images into '{dest_folder}' folder.")
    return dest_folder
    pass

if __name__ == "__main__":
    # Only runs if you run scraperMain.py directly
    imageScraper("cats", 10)




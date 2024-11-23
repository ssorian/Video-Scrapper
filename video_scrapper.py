import os
import time
import requests
import argparse
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from requests.exceptions import ConnectTimeout, MissingSchema


load_dotenv()
USER_PHONE_NUM = os.getenv("FB_PHONE_NUM")
USER_PASSWD = os.getenv("FB_PASSWD")

def init_driver():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
   
    opts.set_preference("browser.cache.disk.enable", False)  # Deshabilita cache en disco
    opts.set_preference("browser.cache.memory.enable", False)  # Deshabilita cache en memoria
    opts.set_preference("browser.cache.offline.enable", False)  # Deshabilita cache offline
    opts.set_preference("network.http.use-cache", False)  # Evita el uso de cache HTTP

    # Bloqueo de contenido innecesario
    opts.set_preference("permissions.default.image", 2)  # Bloquea imágenes
    opts.set_preference("media.autoplay.default", 1)  # Bloquea reproducción automática
    opts.set_preference("media.autoplay.blocking_policy", 2)  # Bloqueo estricto de autoplay
    opts.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", "false")  # Desactiva Flash

    # Deshabilita prefetching y precarga de DNS (reduce solicitudes innecesarias)
    opts.set_preference("network.dns.disablePrefetch", True)  # Desactiva prefetch de DNS
    opts.set_preference("network.prefetch-next", False)  # Desactiva prefetch de contenido
    opts.set_preference("network.predictor.enabled", False)  # Desactiva predictor de red
    opts.set_preference("network.http.speculative-parallel-limit", 0)  # Desactiva conexiones especulativas

    # Limita el uso de recursos adicionales
    opts.set_preference("dom.webdriver.enabled", False)  # Reduce detección de Selenium
    opts.set_preference("dom.webnotifications.enabled", False)  # Desactiva notificaciones web
    opts.set_preference("dom.push.enabled", False)  # Desactiva notificaciones push

    return webdriver.Firefox(options=opts,)


def login(driver, email, passwd):
    driver.get("https://www.facebook.com")

    username = driver.find_element(By.NAME, "email")
    password = driver.find_element(By.NAME, "pass")
    username.send_keys(email)
    password.send_keys(passwd)

    password.send_keys(Keys.RETURN)


def scroll_page(driver, times):
    for _ in range(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)


def dowload_video(url, count, max_size=30):
    try:
        response = requests.head(url)
        if 'Content-Lenght' in response.headers:
            file_size = int(response.headers['Content-Length']) / (1024 * 1024)
            if file_size > max_size:
                print(f"[i] Skipped video - too large ({file_size:.2f} MB).")
                return

        response = requests.get(url, stream=True)
        os.makedirs("videos", exist_ok=True)
        with open(f"videos/video_{count}.mp4", "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

        print(f"[i] Video number {count} downloaded...")

    except (ConnectTimeout, MissingSchema) as e:
        print(f"[!] Failed to download {url}: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Script input")
    parser.add_argument("url", type=str, help="Url to scrape")
    parser.add_argument("-t", "--times", type=int, help="Videos quantity", required=True)
    args = parser.parse_args()

    driver = init_driver()
    try:
        login(driver, USER_PHONE_NUM, USER_PASSWD)
        time.sleep(6)

        driver.get(args.url)
        scroll_page(driver, args.times)

        count = 1
        for i in range(1, args.times + 1):
            try:
                video_url = str(driver.find_element(By.XPATH,
                    f"//div[@role='feed']/div[{i}]//div[@data-ad-preview='message']//a[@role='link']").text)

                if ".mp4" in video_url:
                    dowload_video(video_url, count)
                    count += 1
                else:
                    print(f"[!] Skipped non .mp4 video: {video_url}")
            except (TimeoutException, NoSuchElementException):
                continue

    finally:
        driver.quit()


if __name__ == "__main__":
    main()

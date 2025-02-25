import io
import os
from time import sleep

import streamlit as st
from PIL import Image
from google.genai import Client, types
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

if "cache" not in st.session_state:
    st.session_state["cache"] = {}

api_key = os.environ["GEMINI_API_KEY"]
client = Client(api_key=api_key)


def take_screenshot(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type="chromium").install()), options=options)
    driver.get(url)

    sleep(3)  # Wait for the page to render

    total_height = driver.execute_script("return document.body.scrollHeight")
    driver.set_window_size(1280, total_height)
    screenshot_png = driver.get_screenshot_as_png()
    driver.quit()
    image = Image.open(io.BytesIO(screenshot_png))
    image = image.convert("RGB")
    return image


def sanitize_url(url):
    url = url.lower()
    if url.startswith("http://"):
        url = "https://" + url[7:]
    if not url.startswith("https://"):
        url = "https://" + url
    if url.endswith("/"):
        url = url[:-1]
    return url


def stream_from_cache(url):
    for text in st.session_state["cache"][url].split(" "):
        yield text + " "
        sleep(.02)


def roast(url):
    url = sanitize_url(url)
    if url in st.session_state["cache"]:
        yield from stream_from_cache(url)
        return

    try:
        image = take_screenshot(url)
    except:
        st.error("Invalid URL.")
        return

    prompt = "Roast this website."
    response = client.models.generate_content_stream(
        model="gemini-2.0-flash", contents=[prompt, image], config=types.GenerateContentConfig(temperature=1)
    )

    full_text = ""
    for chunk in response:
        text = chunk.text
        full_text += text
        yield text
    st.session_state["cache"][url] = full_text


st.set_page_config(page_title="Roast This Website 🔥", page_icon="🔥")
st.title("🔥 Roast This Website 🔥")
st.write("Enter a webpage URL and let the AI roast it.")
with st.form("form"):
    col1, col2 = st.columns([5, 1])
    with col1:
        url = st.text_input(label="Website URL", placeholder="https://huggingface.co", label_visibility="collapsed")
    with col2:
        go = st.form_submit_button("Roast it!")

if go:
    if not url:
        url = "https://huggingface.co"
    with st.spinner("Cooking up the roast"):
        try:
            result = roast(url)
            st.write_stream(result)
        except Exception as e:
            st.error(f"Error: {str(e)}")

st.write("❤️ Made by [@tschillaciML](https://x.com/tschillaciML).")

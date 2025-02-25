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

api_key = os.environ["GEMINI_API_KEY"]
client = Client(api_key=api_key)


def roast(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    sleep(3)

    total_height = driver.execute_script("return document.body.scrollHeight")
    driver.set_window_size(1280, total_height)

    screenshot_png = driver.get_screenshot_as_png()
    driver.quit()

    image = Image.open(io.BytesIO(screenshot_png))
    image = image.convert("RGB")

    prompt = "Roast this website."
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=[prompt, image], config=types.GenerateContentConfig(temperature=1)
    )

    return response


st.set_page_config(page_title="🔥 AI Roaster", page_icon="🔥")
st.title("🔥 AI Roaster 🔥")
st.write("Enter a webpage URL and let the AI roast it.")
url = st.text_input("Website URL", placeholder="https://huggingface.co")

if st.button("Roast it!"):
    if url:
        with st.spinner("Cooking up the roast... 🔥"):
            try:
                result = roast(url)
                st.success("Here's your roast:")
                st.write(result)
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a valid URL.")

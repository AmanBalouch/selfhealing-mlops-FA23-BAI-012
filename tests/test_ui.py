import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

APP_URL = os.environ.get("APP_URL", "http://localhost:5000")


def test_frontend_sentiment():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(APP_URL)

        wait = WebDriverWait(driver, 15)

        text_input = wait.until(
            EC.presence_of_element_located((By.ID, "text-input"))
        )
        text_input.send_keys("The food was absolutely delicious and the chef clearly has exceptional skill")

        submit_btn = driver.find_element(By.ID, "submit-btn")
        submit_btn.click()

        WebDriverWait(driver, 15).until(
            lambda d: d.find_element(By.ID, "result-output").text.strip() != ""
        )

        result_text = driver.find_element(By.ID, "result-output").text.strip()
        assert result_text != ""
        assert any(k in result_text for k in ["POSITIVE", "NEGATIVE", "Confidence"])

    finally:
        driver.quit()
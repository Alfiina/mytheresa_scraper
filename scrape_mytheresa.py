from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv

# Setup
service = Service('/usr/bin/chromedriver')  # Adjust path if needed
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=service, options=options)
driver.get("https://www.mytheresa.com/int_en/men/shoes.html")
print(driver.page_source[:2000])


# Wait until products are loaded
WebDriverWait(driver, 50).until(
    EC.presence_of_element_located((By.CLASS_NAME, "item"))
)

# Scroll to load all products
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height
# Parse with BeautifulSoup
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
products = soup.find_all("div", class_="item item--sale")
# Save to CSV
with open("mytheresa_products.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Brand", "Product Name", "Offer_Price", "Listing_price", "Discount", "Size", "Image URL"])


    for product in products:
        image_url = product.find("img", class_="item__images__image item__images__image--single")
        brand = product.find("div", class_="item__info__header__designer")
        product_name = product.find("div", class_="item__info__name")
        offer_price = product.select_one("span.pricing__prices__value--discount > span.pricing__prices__price")
        listing_price = product.select_one("span.pricing__prices__value--original > span.pricing__prices__price")
        discount = product.find("span", class_="pricing__info__percentage")
        sizes = product.find_all("span", class_="item__sizes__size")

        brand_text = brand.get_text(strip=True) if brand else "N/A"
        product_name_text = product_name.find("a").get_text(strip=True) if product_name and product_name.find("a") else "N/A"
        offer_price_text = offer_price.get_text(strip=True) if offer_price else "N/A"
        listing_price_text = listing_price.get_text(strip=True) if listing_price else "N/A"
        discount_text = discount.get_text(strip=True) if discount else "N/A"
        size_text = ", ".join([s.get_text(strip=True) for s in sizes]) if sizes else "N/A"
        image_url_text = img_url["src"] if img_url and img_url.has_attr("src") else "N/A"

        writer.writerow([brand_text, product_name_text, offer_price_text, listing_price_text, discount_text, size_text, image_url_text])
        print(f"{brand_text} | {product_name_text} | {offer_price_text} | {listing_price_text} | {discount_text} | {size_text} | {image_url_text}")

driver.quit()


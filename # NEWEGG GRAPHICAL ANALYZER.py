# NEWEGG GRAPHICAL ANALYZER 
# Author: Sreevastav Sreenivasan
# Search and Compare Product Data on NewEgg.com to Help Make the Custom PC Build Cost Efficient 


import time
import random
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import undetected_chromedriver as uc
from bs4 import BeautifulSoup


# Rotate through a few Chrome-like user agents to avoid blocking 
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36",
]
print("Welcome to the NewEgg Product Analyzer!")
search_term = input("What's the product? ").strip()

# Setup stealthy browser
options = uc.ChromeOptions()
options.add_argument(f"user-agent={random.choice(user_agents)}")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Don’t use headless mode to avoid blocking
# options.add_argument("--headless")

# Launch browser
driver = uc.Chrome(options=options)


# T
try:
    url = f"https://www.newegg.com/p/pl?d={search_term}"
    driver.get(url)
    time.sleep(random.uniform(5, 8))

    soup = BeautifulSoup(driver.page_source, "html.parser")
    page_num = soup.find("span", class_="list-tool-pagination-text")
    if page_num:
        total = page_num.find("strong")
        end_num = total.text.split("/")[1]
        # Change this value to change pages to scrape 
        page_total = min(int(end_num), 5)  # SAFETY: limit pages to scrape (Newegg.com workaround)
    else:
        page_total = 1

    print(f"📄 Scraping up to {page_total} pages for '{search_term}'")

    products_data = []

    for page in range(1, page_total + 1):
        print(f"\n🔍 Scraping page {page}")
        paginated_url = f"https://www.newegg.com/p/pl?d={search_term}&page={page}"
        driver.get(paginated_url)
        time.sleep(random.uniform(6, 10))

        page_soup = BeautifulSoup(driver.page_source, "html.parser")
        products = page_soup.find_all("div", class_="item-cell")
        print(f"🧾 Found {len(products)} products")

        for product in products:
            title_tag = product.find("a", class_="item-title")
            price = product.find("li", class_="price-current")
            if title_tag and price:
                dollar = price.find("strong")
                cents = price.find("sup")
                if dollar and cents:
                    title = title_tag.text.strip()
                    price_str = f"{dollar.text}{cents.text}"
                    try:
                        price_val = float(price_str.replace(',', '').replace('$', ''))
                        products_data.append({"title": title, "price": price_val})
                        print(f"💻 {title} — 💰 ${price_val}")
                    except ValueError:
                        # skip if price conversion fails
                        continue

    if products_data:
        df = pd.DataFrame(products_data)
        print(f"\nCollected {len(df)+1} products")
    else:
        df = pd.DataFrame()
        print("No valid product price data collected.")

except Exception as e:
    print("❌ Error:", e)
    df = pd.DataFrame()  # ensure df exists if error

finally:
    driver.quit()

# --- Data Analysis & Plotting ---

if not df.empty:
    # Basic stats
    print(f"\n📊 Dataset Statistics for '{search_term}':")
    print(df.describe().round(2).to_string())
    print(f"\n🧾 Total products analyzed: {len(df)}")


    # Basic Scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(df.index, df['price'])
    plt.title("Scatter Plot of Product Price")
    plt.xlabel("Product Index")
    plt.ylabel("Price ($)")
    plt.show()

    # Unsupervised Machine Learning Similar Products to Prices (titel v price)
    print(f"\n📊 Brand Statistics for '{search_term}': UNSUPERVISED")
    # Step 1: Vectorize titles into TF-IDF features
    vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
    X_title = vectorizer.fit_transform(df['title'])

    # Step 2: Cluster titles based on TF-IDF features
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(X_title)

    df['title_cluster'] = clusters

    # Step 3: Analyze price differences between clusters
    print(df.groupby('title_cluster')['price'].describe())

    # Step 4: Print sample product titles per cluster
    for cluster_num in sorted(df['title_cluster'].unique()):
        print(f"\nCluster {cluster_num} sample titles:")
        sample_titles = df[df['title_cluster'] == cluster_num]['title'].sample(5, random_state=42).values
        for title in sample_titles:
            print(f" - {title}")
    # Supervised Machine Learning Predicting Prices Relative to Actual Prices and MSRP of Product 
    # print(f"\n📊 MSRP Statistics for '{search_term}': SUPERVISED")


else:
    print("No product data collected.")

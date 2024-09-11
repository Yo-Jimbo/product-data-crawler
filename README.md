# Product Data Extraction Script

This Python script is a powerful tool designed to extract detailed data about products from a specific e-commerce (the website in the code has been redacted as "e-commerce.com", as such the code is for demonstration purposes only). The script utilizes the Scrapy library to crawl product pages and gather their data like the product name, categories and SKU. The extracted data is then structured and saved into a CSV file format, making it convenient for importing into Google Analytics 4 (GA4) for fixing potential tracking mistakes and improving the data quality.

## How to Use
1. **Setup:** Ensure you have Python 3.x installed on your system along with the required libraries: `pandas`, `datetime`, `scrapy`, `beautifulsoup4`.
2. **Data Preparation:** Make sure that the script is in the same directory as the historical product data CSV file named `ProductDataNew.csv`, or the script will stop. It is taken as a given that there is always historical data to update (at the first launch of the script, the .csv file may contain data for products not currently on the e-commerce).
3. **Execution:** Run the script in a Python environment to initiate the data extraction process.
4. **Output:** The script will generate a new CSV file named `ProductDataNew.csv` containing the updated product information.
5. **Import into GA4:** Utilize the extracted data for importing into GA4 for cleaning potential mistracked data and improving its quality.

## Key Features and Functionality
- **Data Extraction:** The script accesses the e-commerce and extracts product information such as product names, categories, SKUs, and URLs.
- **Data Processing:** The extracted data is cleaned, organized, and formatted to ensure consistency and accuracy for further analysis.
- **New Product Identification:** The script compares the newly extracted data with historical product data to identify and highlight any new products that have been added since the last extraction.
- **Data Storage and Backup:** The script automatically creates a backup of the historical product data and stores the updated data in a timestamped file within the `Storico-Dati-Prodotti` directory.
- **Timestamp Tracking:** The script records the start and end times of the data extraction process, providing insights into the duration of the crawling operation.

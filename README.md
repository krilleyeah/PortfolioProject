# PortfolioProject #1

# Apple App Store Data Analysis Dashboard

A professional data science project that analyzes over 1.2 million Apple App Store apps. This project demonstrates a full data pipeline: from handling large datasets with **Pandas** and **SQLite** to deploying an interactive web application via **Streamlit**.

## 🚀 Live Demo
Check out the interactive dashboard here: [https://portfolioproject-9xmtgcnlvqx3zcaqzzexx7.streamlit.app/]

## 📊 Features
*   **Large Scale Data Handling:** Processes a dataset of ~400MB using a memory-efficient SQL-based approach.
*   **Interactive Visualizations:** Explore app distributions, pricing strategies, and user ratings.
*   **Clean Data Pipeline:** Includes a Jupyter Notebook for data cleaning, transformation (CSV to SQL), and preprocessing.

## 🛠️ Tech Stack
*   **Language:** Python
*   **Data Processing:** Pandas, NumPy
*   **Database:** SQLite3
*   **Deployment:** Streamlit Cloud
*   **Storage:** Git LFS (Large File Storage) for the 195MB database.

## 📁 Project Structure
*   `app.py`: The main Streamlit application script.
*   `AppleInsights.ipynb`: Documentation of the ETL process and data preparation.
*   `apple_apps.db`: The processed SQLite database (managed via Git LFS).
*   `requirements.txt`: List of necessary Python libraries.

## ⚙️ How it Works
Instead of loading a massive CSV file into memory on every user request, this project uses a **pre-processed SQLite database**. This ensures:
1.  **Speed:** Instant queries even on limited server resources.
2.  **Stability:** Efficient memory management by only fetching required data.
3.  **Portability:** The database is stored directly in the repository via Git LFS.

Used kaggle data source (thank you!):
[https://www.kaggle.com/datasets/gauthamp10/apple-appstore-apps?resource=download]
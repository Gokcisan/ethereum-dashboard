import streamlit as st
import pandas as pd
import sqlite3

# Başlık
st.title("📰 Ethereum News & 📈 Price Dashboard")
st.write("Explore how Ethereum news headlines align with daily price changes.")

# Veritabanlarına bağlan
conn_news = sqlite3.connect("ethereum_news_with_date.db")
conn_price = sqlite3.connect("ethereum_price.db")

# Verileri oku
news_df = pd.read_sql_query("SELECT * FROM ethereum_articles", conn_news)
price_df = pd.read_sql_query("SELECT * FROM ethereum_prices", conn_price)

# Veritabanı bağlantılarını kapat
conn_news.close()
conn_price.close()

# Tarihleri dönüştür
news_df["date"] = pd.to_datetime(news_df["date"]).dt.date
price_df["date"] = pd.to_datetime(price_df["date"]).dt.date

# Sayısal dönüşüm (önemli!)
price_df["open"] = pd.to_numeric(price_df["open"], errors="coerce")
price_df["close"] = pd.to_numeric(price_df["close"], errors="coerce")

# Günlük ortalama fiyat (gerekliyse)
price_df = price_df.groupby("date", as_index=False).agg({"open": "mean", "close": "mean"})

# Haber ve fiyat verilerini birleştir
merged_df = pd.merge(news_df, price_df, how="left", on="date")

# Haber başlıklarını tıklanabilir HTML linke dönüştür
merged_df["link"] = merged_df.apply(
    lambda row: f'<a href="{row["url"]}" target="_blank">{row["title"]}</a>', axis=1
)

# Layout: Tabs ile göster
tab1, tab2 = st.tabs(["📚 News Only", "🔗 News + Price"])

with tab1:
    st.markdown("### 📚 Ethereum News")
    st.write("Latest scraped headlines from U.Today:")
    st.write(merged_df[["date", "link"]].to_html(escape=False, index=False), unsafe_allow_html=True)

with tab2:
    st.markdown("### 💹 Price + News Data")
    st.write("Each headline paired with Ethereum price info (open & close):")
    st.dataframe(merged_df)

    if st.checkbox("Show only rows with valid price data"):
        st.dataframe(merged_df[merged_df["open"].notna()])

    # Grafiksel analiz: fiyat değişimi
    st.markdown("### 📊 Price Change on News Days")
    merged_df["price_change"] = merged_df["close"] - merged_df["open"]
    st.bar_chart(merged_df.set_index("date")["price_change"])
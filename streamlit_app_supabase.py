# 📦 Gerekli kütüphaneleri içe aktar
import streamlit as st
import pandas as pd
import os
import psycopg
from dotenv import load_dotenv

# 🌱 .env dosyasındaki Supabase bağlantı bilgisini yükle
load_dotenv()
dbconn = os.getenv("DBCONN")

# 📊 Supabase'ten fiyat verisini çek
def get_price_data():
    with psycopg.connect(dbconn) as conn:
        df = pd.read_sql("SELECT * FROM api_data", conn)
    return df

# 📰 Supabase'ten haber başlıklarını çek
def get_news_data():
    with psycopg.connect(dbconn) as conn:
        df = pd.read_sql("SELECT * FROM ethereum_articles", conn)
    return df

# 🎯 Başlık ve açıklama
st.title("🛰️ Ethereum News & Price")
st.write("Real-time news and crypto prices.")

# 🔍 Verileri çek
price_df = get_price_data()
news_df = get_news_data()

# 🧹 Tarih formatlarını düzelt
price_df["date"] = pd.to_datetime(price_df["date"]).dt.date
news_df["date"] = pd.to_datetime(news_df["date"]).dt.date

# 🔢 Sayısal dönüşüm (önemli!)
price_df["open"] = pd.to_numeric(price_df["open"], errors="coerce")
price_df["close"] = pd.to_numeric(price_df["close"], errors="coerce")

# 🧮 Günlük ortalama fiyat
price_df = price_df.groupby("date", as_index=False).agg({
    "open": "mean",
    "close": "mean"
})

# 🧩 Haber ve fiyatı birleştir
merged_df = pd.merge(news_df, price_df, how="left", on="date")

# 🔗 Haber başlıklarını tıklanabilir hale getir
merged_df["link"] = merged_df.apply(
    lambda row: f'<a href="{row["url"]}" target="_blank">{row["title"]}</a>', axis=1
)

# 📊 Fiyat değişimini hesapla
merged_df["price_change"] = merged_df["close"] - merged_df["open"]

# 🧭 Sekmeler oluştur
tab1, tab2, tab3 = st.tabs(["📰 Headlines", "📈 News + Price", "💹 Full Price History"])

# 📰 Sekme 1: Sadece haber başlıkları
with tab1:
    st.markdown("### Latest Ethereum Headlines (from U.Today)")
    st.write(merged_df[["date", "link"]].to_html(escape=False, index=False), unsafe_allow_html=True)

# 📈 Sekme 2: Haber + Fiyat eşleşmeleri
with tab2:
    st.markdown("### Ethereum News + Daily Price Info")
    st.dataframe(merged_df)

    if st.checkbox("Show only rows with price data"):
        st.dataframe(merged_df[merged_df["open"].notna()])

    st.markdown("### Price Movement on News Days")
    st.bar_chart(merged_df.set_index("date")["price_change"])

    st.markdown("### 🧪 Merge edilen tarih aralığı")
    st.write(f"Min: {merged_df['date'].min()}, Max: {merged_df['date'].max()}")
    st.write("Grafikte gösterilen veri sayısı:", merged_df["price_change"].notna().sum())

# 💹 Sekme 3: Tüm fiyat verisi (haberlerden bağımsız)
with tab3:
    st.markdown("### 💹 Ethereum Prices")
    st.line_chart(price_df.set_index("date")[["open", "close"]])
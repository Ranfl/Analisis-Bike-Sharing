import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

sns.set(style='dark', palette='viridis')

main_data = pd.read_csv("D:\Kuliah\Dicoding DBS\ILT ML\submission\dashboard\main_data.csv")
main_data['dteday'] = pd.to_datetime(main_data['dteday'])

st.title('Dashboard Analysis Bike Sharing')

def make_circle(image_path):
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, w, h), fill=255)
    img.putalpha(mask)

    border_size = 8
    bordered_img = Image.new("RGBA", (w + border_size * 2, h + border_size * 2), (255, 255, 255, 0))
    draw = ImageDraw.Draw(bordered_img)
    draw.ellipse((0, 0, w + border_size * 2, h + border_size * 2), fill=(255, 255, 255, 255))
    bordered_img.paste(img, (border_size, border_size), img)

    return bordered_img

with st.sidebar:
    circle_image = make_circle("D:\Kuliah\Dicoding DBS\ILT ML\submission\dashboard\logosepeda.png")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(circle_image, use_container_width=True)

    st.header('Filter Data')
    season = st.selectbox('Select Season', ['All'] + list(main_data['season'].unique()))
    weather = st.selectbox('Select Weather', ['All'] + list(main_data['weathersit'].unique()))
    user_type = st.radio('User Type', ['All', 'casual', 'registered'])
    day_type = st.radio('Day Type', ['All', 'Working Day', 'Weekend'])

filtered_data = main_data.copy()
if season != 'All':
    filtered_data = filtered_data[filtered_data['season'] == season]
if weather != 'All':
    filtered_data = filtered_data[filtered_data['weathersit'] == weather]
if day_type != 'All':
    if day_type == 'Working Day':
        filtered_data = filtered_data[(filtered_data['workingday'] == 'yes') & (filtered_data['holiday'] == 0)]
    elif day_type == 'Weekend':
        filtered_data = filtered_data[(filtered_data['workingday'] == 'no') | (filtered_data['holiday'] == 1)]

st.subheader('Season Users')
col1, col2, col3 = st.columns(3)
total_casual = filtered_data['casual'].sum()
total_registered = filtered_data['registered'].sum()
total_users = total_casual + total_registered

with col1:
    st.metric("Total Casual User", value=f'{total_casual:,}')
with col2:
    st.metric("Total Registered User", value=f'{total_registered:,}')
with col3:
    st.metric("Total Users", value=f'{total_users:,}')

if user_type == 'casual':
    filtered_data['user'] = filtered_data['casual']
elif user_type == 'registered':
    filtered_data['user'] = filtered_data['registered']
else:
    filtered_data['user'] = filtered_data['casual'] + filtered_data['registered']

if not filtered_data.empty:
    st.subheader('Analisis Pengguna Berdasarkan Filter')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='season', y='user', data=filtered_data, ci=None, estimator=sum, order=['spring', 'summer', 'fall', 'winter'], palette='viridis')
    ax.set_title('Jumlah Pengguna berdasarkan Musim')
    st.pyplot(fig, clear_figure=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='weathersit', y='user', data=filtered_data, ci=None, estimator=sum, palette='viridis')
    ax.set_title('Jumlah Pengguna berdasarkan Kondisi Cuaca')
    st.pyplot(fig, clear_figure=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='workingday', y='user', data=filtered_data, ci=None, estimator=sum, palette='viridis')
    ax.set_title('Jumlah Pengguna berdasarkan Tipe Hari')
    st.pyplot(fig, clear_figure=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(x='hr', y='user', data=filtered_data, ci=None, estimator=sum, palette='viridis')
    ax.set_title('Jam Sibuk Penyewaan Sepeda')
    st.pyplot(fig, clear_figure=True)

    st.subheader('RFM Analysis Berdasarkan Kondisi Cuaca')
    rfm_weather = filtered_data.copy()
    rfm_weather['Recency'] = (rfm_weather['dteday'].max() - rfm_weather['dteday']).dt.days
    rfm_weather['Frequency'] = rfm_weather.groupby('weathersit')['cnt'].transform('count')
    rfm_weather['Monetary'] = rfm_weather.groupby('weathersit')['cnt'].transform('sum')

    fig, axs = plt.subplots(1, 3, figsize=(18, 6))
    sns.barplot(x='weathersit', y='Recency', data=rfm_weather, ci=None, palette='viridis', ax=axs[0])
    axs[0].set_title('Recency Berdasarkan Kondisi Cuaca')

    sns.barplot(x='weathersit', y='Frequency', data=rfm_weather, ci=None, palette='viridis', ax=axs[1])
    axs[1].set_title('Frequency Berdasarkan Kondisi Cuaca')

    sns.barplot(x='weathersit', y='Monetary', data=rfm_weather, ci=None, palette='viridis', ax=axs[2])
    axs[2].set_title('Monetary Berdasarkan Kondisi Cuaca')

    st.pyplot(fig, clear_figure=True)
else:
    st.warning('Data tidak ditemukan sesuai dengan filter yang dipilih.')

st.caption('Copyright © Rasyid Naufal 2025')

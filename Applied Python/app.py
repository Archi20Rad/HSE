import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

def load_data(file):
    df = pd.read_csv(file)
    # df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['rolling_mean'] = df.groupby('city')['temperature'].transform(lambda x: x.rolling(window=30).mean())
    seasonal_stats = df.groupby(['city', 'season']).agg(mean_temperature=('temperature', 'mean'), std_temperature=('temperature', 'std')).reset_index()
    df = df.merge(seasonal_stats, on=['city', 'season'])
    df['anomaly'] = (df['temperature'] < (df['mean_temperature'] - 2 * df['std_temperature'])) | (df['temperature'] > (df['mean_temperature'] + 2 * df['std_temperature']))
    df = df.sort_values(by='timestamp')
    return df

def get_current_temperature(city, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if response.status_code == 200:
        return data['main']['temp']
    elif data.get('cod') == 401:
        raise Exception("Invalid API key. Please see https://openweathermap.org/faq#error401 for more info.")
    else:
        raise Exception(f"Error: {data['message']}")

def is_temperature_anomal(city, current_temp, df):
    current_season = df[df['city'] == city].iloc[-1]['season']
    seasonal_data = df[(df['city'] == city) & (df['season'] == current_season)]
    mean_temp = seasonal_data['temperature'].mean()
    std_temp = seasonal_data['temperature'].std()
    if mean_temp - 2 * std_temp <= current_temp <= mean_temp + 2 * std_temp:
        return False
    else:
        return True

def display_statistics(df, city):
    city_data = df[df['city'] == city]
    st.write(f"### Описательная статистика для {city}")
    st.write(city_data.describe())

def display_time_series(df, city):
    city_data = df[df['city'] == city]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=city_data['timestamp'], y=city_data['temperature'], mode='markers', name='Температура (°C)'))
    fig.add_trace(go.Scatter(x=city_data[city_data['anomaly']]['timestamp'], y=city_data[city_data['anomaly']]['temperature'], mode='markers', name='Аномалии', marker=dict(color='red')))
    fig.update_layout(
        title={
            'text': f'Ежедневная температура в {city}',
            'x': 0.25,  
            'font': dict(size=24)  
        },
        xaxis_title='Дата',
        yaxis_title='Температура (°C)',
        font=dict(size=14)  
    )
    st.plotly_chart(fig)

def display_seasonal_profiles(df, city):
    seasons = df['season'].unique()
    fig = go.Figure()
    for season in seasons:
        season_data = df[(df['city'] == city) & (df['season'] == season)]
        mean_temp = season_data['temperature'].mean()
        std_temp = season_data['temperature'].std()
        fig.add_trace(go.Scatter(
            x=season_data['timestamp'],
            y=season_data['temperature'],
            mode='markers',
            name=f'{season} (mean: {mean_temp:.2f}, std: {std_temp:.2f})',
            hovertext=season_data['season'],
            hovertemplate='Дата: %{x}<br>Температура: %{y}°C<br>Сезон: %{hovertext}<extra></extra>'
        ))
        fig.update_layout(
            title={
                'text': f'Сезонные температурные профили для {city}',
                'x': 0.10,  
                'font': dict(size=24)  
            },
            xaxis_title='Дата',
            yaxis_title='Температура (°C)',
            font=dict(size=14)) 
    st.plotly_chart(fig)

st.title("Анализ температурных данных")

uploaded_file = st.file_uploader("Загрузите файл с историческими данными", type=["csv"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    cities = df['city'].unique()

    selected_city = st.selectbox("Выберите город", cities)
    api_key = st.text_input("Введите API-ключ OpenWeatherMap", type="password")

    if api_key:
        try:
            current_temp = get_current_temperature(selected_city, api_key)
            st.write(f"Текущая температура в {selected_city}: {current_temp}°C")
            st.write(f"Температура {'аномальна' if is_temperature_anomal(selected_city, current_temp, df) else 'нормальна'} для текущего сезона.")
        except Exception as e:
            st.error(str(e))

    display_statistics(df, selected_city)
    display_time_series(df, selected_city)
    display_seasonal_profiles(df, selected_city)
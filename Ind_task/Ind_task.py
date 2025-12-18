import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Налаштування сторінки
st.set_page_config(page_title="Supermarket Analytics", layout="wide")
st.title("📊 Аналіз популярності супермаркетів")


@st.cache_data
def generate_supermarket_data(n=200):
    np.random.seed(42)

    chains = ['ATB', 'Silpo', 'Novus', 'Auchan', 'Metro', 'Fora']
    cities = ['Kyiv', 'Kharkiv', 'Lviv', 'Odesa', 'Dnipro']

    data = {
        'Store_ID': range(1, n + 1),
        'Chain': np.random.choice(chains, size=n),
        'City': np.random.choice(cities, size=n),
        'Square_m': np.random.randint(100, 5000, size=n),       # Площа
        'Daily_Visitors': np.random.randint(200, 3000, size=n), # Базовий трафік
        'Avg_Check_UAH': np.random.uniform(150, 1500, size=n),  # Середній чек
        'Rating': np.round(np.random.uniform(2.5, 5.0, size=n), 1), # Рейтинг
        'Parking_Spaces': np.random.randint(0, 150, size=n),
    }

    df = pd.DataFrame(data)

    df['Daily_Revenue'] = df['Daily_Visitors'] * df['Avg_Check_UAH'] # Розрахунок виторгу

    return df

df = generate_supermarket_data()

st.header("Статичний огляд даних")

st.subheader("Перші 5 рядків згенерованого датасету")
st.dataframe(df.head())

col1, col2 = st.columns(2) # Дві колонки для статичних графіків

with col1:
    st.subheader("Розподіл середнього чеку")
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.histplot(data=df, x='Avg_Check_UAH', hue='Chain', kde=True, element="step", ax=ax1)
    ax1.set_title('Розподіл середнього чеку за мережами')
    st.pyplot(fig1)

with col2:
    st.subheader("Кореляційна матриця")
    fig2, ax2 = plt.subplots(figsize=(10, 8))
    numeric_df = df.select_dtypes(include=[np.number])
    sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt=".2f", ax=ax2)
    ax2.set_title('Кореляційна матриця ознак')
    st.pyplot(fig2)

# Інтерактивний дешборд
st.markdown("---")
st.header("Інтерактивний дешборд")

# Сайдбар для віджетів (аналог interact)
st.sidebar.header("Параметри фільтрації")

cities_list = df['City'].unique().tolist()
selected_city = st.sidebar.selectbox("Оберіть місто:", cities_list)

min_rating = st.sidebar.slider("Мін. рейтинг:", min_value=2.5, max_value=5.0, value=3.0, step=0.1)

# Фільтрація даних
filtered_df = df[
    (df['City'] == selected_city) &
    (df['Rating'] >= min_rating)
]

if filtered_df.empty:
    st.warning(f"Увага: Немає магазинів у м.{selected_city} з рейтингом >= {min_rating}")
else:
    # Графік Plotly
    st.subheader(f'Виторг vs Трафік у м. {selected_city}')

    fig = px.scatter(
        filtered_df,
        x='Daily_Visitors',
        y='Daily_Revenue',
        size='Square_m',
        color='Chain',
        hover_data=['Store_ID', 'Avg_Check_UAH', 'Rating'],
        title=f'Рейтинг >= {min_rating}',
        labels={'Daily_Visitors': 'Відвідувачів в день', 'Daily_Revenue': 'Денний виторг (грн)'},
        template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Таблиця лідерів
    st.subheader("Топ-3 найприбутковіші магазини вибірки:")
    top_3 = filtered_df.sort_values(by='Daily_Revenue', ascending=False).head(3)[['Chain', 'Daily_Revenue', 'Rating', 'Square_m']]
    st.dataframe(top_3)

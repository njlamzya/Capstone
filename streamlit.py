import streamlit as st
import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv('DATA FINAL EPL 2010-2025.csv')

# Tambahkan kolom season jika belum ada
if 'Season' not in df.columns:
    df['Season'] = df['Date'].apply(lambda x: '2024/2025' if '2024' in x or '2025' in x else 'Other')

# Atur layout penuh
st.set_page_config(layout="wide")

# Layout utama: sidebar kiri dan konten utama kanan
col_side, col_main = st.columns([1, 3], gap="large")

with col_side:
    with st.container(border=True):
        st.image('https://upload.wikimedia.org/wikipedia/en/f/f2/Premier_League_Logo.svg', width=100)
        st.title("🏆 EPL Match Predictor")
        st.markdown("---")
        st.subheader("📅 Pilih Musim")
        season = st.selectbox('Season', ['2024/2025', '2025/2026'], key='season')
        st.subheader("⚽ Pilih Tim")
        filtered_df = df[df['Season'] == season]
        home_team = st.selectbox('Home Team', filtered_df['HomeTeam'].sort_values().unique(), key='home_team')
        away_team = st.selectbox('Away Team', filtered_df['AwayTeam'].sort_values().unique(), key='away_team')
        st.markdown("---")

# Fungsi ambil URL logo tim
def get_team_logo_url(team_name):
    team_logos = {
        'Man United': 'https://resources.premierleague.com/premierleague/badges/t1.png',
        'Arsenal': 'https://resources.premierleague.com/premierleague/badges/t3.png',
        'Chelsea': 'https://resources.premierleague.com/premierleague/badges/t8.png',
        'Liverpool': 'https://resources.premierleague.com/premierleague/badges/t14.png',
        'Man City': 'https://resources.premierleague.com/premierleague/badges/t43.png'
    }
    return team_logos.get(team_name, 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg')

# Tampilkan bagian utama
with col_main:
    st.markdown("<h2 style='text-align: center;'>Hasil Prediksi Pertandingan</h2>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='display: flex; justify-content: center;'>
        <div style='display: flex; align-items: center; border: 2px solid #ccc; border-radius: 12px; padding: 20px; background-color: #fafafa;'>
            <div style='text-align: center; margin: 0 40px;'>
                <img src='{get_team_logo_url(home_team)}' width='100'><br>
                <strong>{home_team}</strong>
            </div>
            <div style='text-align: center; font-size: 24px; padding: 0 30px;'>VS</div>
            <div style='text-align: center; margin: 0 40px;'>
                <img src='{get_team_logo_url(away_team)}' width='100'><br>
                <strong>{away_team}</strong>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Ambil data berdasarkan season & matchup dua arah
    if home_team and away_team and season:
        season_data = df[df['Season'] == season]
        match1 = season_data[(season_data['HomeTeam'] == home_team) & (season_data['AwayTeam'] == away_team)]
        match2 = season_data[(season_data['HomeTeam'] == away_team) & (season_data['AwayTeam'] == home_team)]
        combined = pd.concat([match1, match2])

        home_wins = np.sum((combined['HomeTeam'] == home_team) & (combined['FTR'] == 'H')) + \
                    np.sum((combined['AwayTeam'] == home_team) & (combined['FTR'] == 'A'))
        away_wins = np.sum((combined['HomeTeam'] == away_team) & (combined['FTR'] == 'H')) + \
                    np.sum((combined['AwayTeam'] == away_team) & (combined['FTR'] == 'A'))
        draws = np.sum(combined['FTR'] == 'D')
        total_matches = len(combined)

        if total_matches > 0:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.subheader("📊 Head-to-Head Statistik")
            st.write(f"🔴 {home_team} Menang: {home_wins}")
            st.write(f"🤝 Seri: {draws}")
            st.write(f"🔵 {away_team} Menang: {away_wins}")

            prediction = max(('Home Win', home_wins), ('Draw', draws), ('Away Win', away_wins), key=lambda x: x[1])
            result = home_team if prediction[0] == 'Home Win' else away_team if prediction[0] == 'Away Win' else 'Seri'
            st.success(f"### Prediksi: {result}")
        else:
            st.warning("⚠️ Belum ada data historis untuk pertandingan ini di musim ini.")

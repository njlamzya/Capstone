import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="EPL Actual vs Prediction", layout="wide")
st.title("⚽ EPL 2024/2025 Dashboard - Actual vs Prediction")

# ============================
# LOAD DATA
# ============================
@st.cache_data
def load_data():
    preds = pd.read_csv(r"D:\CAPSTONE PROJECT\EPL_2024_2025_Binary_Predictions.csv")
    actual_df = pd.read_csv(r"D:\CAPSTONE PROJECT\DATA FINAL EPL 2010-2025.csv", parse_dates=['Date'])
    
    actual_df = actual_df[actual_df['FTR'] != 'D']
    actual_df = actual_df[(actual_df['Date'] >= '2024-08-01') & (actual_df['Date'] <= '2025-05-31')]
    
    preds.rename(columns={"Actual": "actual", "Predicted": "predicted"}, inplace=True)
    preds['Date'] = pd.to_datetime(preds['Date'])
    
    mapping_result = {'Home Win': 'H', 'Away Win': 'A', 'Draw': 'D'}
    preds['actual_code'] = preds['actual'].map(mapping_result)
    preds['predicted_code'] = preds['predicted'].map(mapping_result)
    
    return preds, actual_df

preds, actual_df = load_data()

merged = preds.merge(
    actual_df[['Date', 'HomeTeam', 'AwayTeam', 'FTR', 'FTHG', 'FTAG']],
    on=['Date', 'HomeTeam', 'AwayTeam'],
    how='left'
)

# ============================
# Fungsi Hitung Poin
# ============================
def compute_points(df, use_actual=True):
    teams = sorted(set(df['HomeTeam']).union(set(df['AwayTeam'])))
    points_dict = {team: {'Points': 0, 'GD': 0, 'GF': 0, 'GA': 0} for team in teams}

    for _, row in df.iterrows():
        home, away = row['HomeTeam'], row['AwayTeam']
        hg, ag = row['FTHG'], row['FTAG']
        actual = row['FTR']
        pred = row['predicted_code']
        result = actual if use_actual else pred

        if result == 'H':
            points_dict[home]['Points'] += 3
        elif result == 'A':
            points_dict[away]['Points'] += 3

        points_dict[home]['GF'] += hg
        points_dict[home]['GA'] += ag
        points_dict[home]['GD'] += hg - ag
        points_dict[away]['GF'] += ag
        points_dict[away]['GA'] += hg
        points_dict[away]['GD'] += ag - hg

    df_out = pd.DataFrame([{'Team': team, **vals} for team, vals in points_dict.items()])
    return df_out

actual_pts = compute_points(merged, use_actual=True)
predicted_pts = compute_points(merged, use_actual=False)

leaderboard = actual_pts.merge(predicted_pts, on='Team', suffixes=('_Actual', '_Predicted'))
leaderboard['Point_Diff'] = leaderboard['Points_Actual'] - leaderboard['Points_Predicted']
leaderboard = leaderboard.sort_values(by='Points_Actual', ascending=False).reset_index(drop=True)
leaderboard.insert(0, 'Rank', leaderboard.index + 1)

# ============================
# Fungsi Logo
# ============================
def get_logo_url(team_name):
    logos = {
    "Arsenal": "https://upload.wikimedia.org/wikipedia/commons/5/53/Arsenal_FC.svg",
    "Aston Villa": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Aston_Villa_logo.svg",
    "Bournemouth": "https://upload.wikimedia.org/wikipedia/commons/e/e5/AFC_Bournemouth_crest.svg",
    "Brentford": "https://upload.wikimedia.org/wikipedia/commons/2/2a/Brentford_FC_crest.svg",
    "Brighton": "https://upload.wikimedia.org/wikipedia/commons/f/fd/Brighton_%26_Hove_Albion_logo.svg",
    "Burnley": "https://upload.wikimedia.org/wikipedia/commons/0/02/Burnley_FC_badge.svg",
    "Chelsea": "https://upload.wikimedia.org/wikipedia/commons/c/cc/Chelsea_FC.svg",
    "Crystal Palace": "https://upload.wikimedia.org/wikipedia/commons/0/0c/Crystal_Palace_FC_logo.svg",
    "Everton": "https://upload.wikimedia.org/wikipedia/commons/7/7c/Everton_FC_logo.svg",
    "Fulham": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Fulham_FC_crest.svg",
    "Leeds": "https://upload.wikimedia.org/wikipedia/commons/0/05/Leeds_United_Logo.svg",
    "Leicester": "https://upload.wikimedia.org/wikipedia/commons/2/2d/Leicester_City_crest.svg",
    "Liverpool": "https://upload.wikimedia.org/wikipedia/commons/0/0c/Liverpool_FC.svg",
    "Luton": "https://upload.wikimedia.org/wikipedia/commons/f/f4/Luton_Town_F.C._logo.svg",
    "Man City": "https://upload.wikimedia.org/wikipedia/commons/e/eb/Manchester_City_FC_badge.svg",
    "Man United": "https://upload.wikimedia.org/wikipedia/commons/7/7a/Manchester_United_FC_crest.svg",
    "Newcastle": "https://upload.wikimedia.org/wikipedia/commons/5/56/Newcastle_United_Logo.svg",
    "Norwich": "https://upload.wikimedia.org/wikipedia/commons/8/8c/Norwich_City.svg",
    "Nottingham Forest": "https://upload.wikimedia.org/wikipedia/commons/e/e5/Nottingham_Forest_F.C._logo.svg",
    "Sheffield Utd": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Sheffield_United_FC_logo.svg",
    "Southampton": "https://upload.wikimedia.org/wikipedia/commons/c/c9/Southampton_FC_Logo.svg",
    "Tottenham": "https://upload.wikimedia.org/wikipedia/commons/b/b4/Tottenham_Hotspur.svg",
    "Watford": "https://upload.wikimedia.org/wikipedia/commons/e/e2/Watford.svg",
    "West Brom": "https://upload.wikimedia.org/wikipedia/commons/8/8b/West_Bromwich_Albion.svg",
    "West Ham": "https://upload.wikimedia.org/wikipedia/commons/c/c2/West_Ham_United_FC_logo.svg",
    "Wolves": "https://upload.wikimedia.org/wikipedia/commons/f/fc/Wolverhampton_Wanderers.svg",
    }
    return logos.get(team_name, "")

# ============================
# Leaderboard Section
# ============================
st.header("📊 Leaderboards")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Actual Standings")
    df_actual = leaderboard[['Rank', 'Team', 'Points_Actual', 'GD_Actual', 'GF_Actual', 'GA_Actual']]
    df_actual.columns = ['Rank', 'Team', 'Points', 'Goal Diff', 'Goals For', 'Goals Against']
    st.dataframe(df_actual.style.background_gradient(cmap='Greens'), use_container_width=True)

with col2:
    st.subheader("🔮 Predicted Standings")
    df_pred = leaderboard[['Rank', 'Team', 'Points_Predicted', 'GD_Predicted', 'GF_Predicted', 'GA_Predicted']]
    df_pred.columns = ['Rank', 'Team', 'Points', 'Goal Diff', 'Goals For', 'Goals Against']
    st.dataframe(df_pred.style.background_gradient(cmap='Blues'), use_container_width=True)

# Highlight Selisih Poin Terbesar
highlight_team = leaderboard.loc[leaderboard['Point_Diff'].abs().idxmax()]
st.markdown(f"### ⚠️ Highlight: Tim dengan selisih poin terbesar adalah **{highlight_team['Team']}** dengan selisih **{abs(highlight_team['Point_Diff'])}** poin.")

# Statistik Prediksi
st.markdown("---")
st.header("📋 Statistik Prediksi")
total_games = len(merged)
correct_preds = (merged['FTR'] == merged['predicted_code']).sum()
accuracy = correct_preds / total_games * 100

st.metric("Total Pertandingan", total_games)
st.metric("Prediksi Tepat", correct_preds)
st.metric("Akurasi Prediksi", f"{accuracy:.2f}%")

# ============================
# Head to Head Section
# ============================
# Head to Head Section
# --- Fungsi emoji hasil ---
def map_result_home(result):
    return "✅" if result == 'H' else "❌"

def map_result_away(result):
    return "✅" if result == 'A' else "❌"

# --- Head-to-Head Section ---
st.markdown("---")
st.header("🔍 Head-to-Head Analysis")

col1, col2 = st.columns(2)
with col1:
    selected_home = st.selectbox(
        "Pilih Tim Home",
        sorted(merged['HomeTeam'].unique()),
        key="home_team_selectbox"
    )
with col2:
    selected_away = st.selectbox(
        "Pilih Tim Away",
        sorted(merged['AwayTeam'].unique()),
        key="away_team_selectbox"
    )

head2head = merged[(merged['HomeTeam'] == selected_home) & (merged['AwayTeam'] == selected_away)]

if head2head.empty:
    st.warning("Tidak ada pertandingan antara tim tersebut di musim ini.")
else:
    col1, col2 = st.columns([1, 1])

    with col1:
        logo_home = get_logo_url(selected_home)
        if logo_home:
            st.image(logo_home, width=70)
        st.markdown(f"### {selected_home}")
        st.markdown("**5 TERAKHIR**")

        last_home = merged[merged['HomeTeam'] == selected_home].sort_values('Date', ascending=False).head(5)
        last_home_results = [map_result_home(r) for r in last_home['FTR']]
        df_home = pd.DataFrame([last_home_results], columns=[f"{i+1}" for i in range(5)])
        st.table(df_home.style.hide(axis="index"))

    with col2:
        logo_away = get_logo_url(selected_away)
        if logo_away:
            st.image(logo_away, width=70)
        st.markdown(f"### {selected_away}")
        st.markdown("**5 TERAKHIR**")

        last_away = merged[merged['AwayTeam'] == selected_away].sort_values('Date', ascending=False).head(5)
        last_away_results = [map_result_away(r) for r in last_away['FTR']]
        df_away = pd.DataFrame([last_away_results], columns=[f"{i+1}" for i in range(5)])
        st.table(df_away.style.hide(axis="index"))


    # Head to Head Matches
    st.markdown(f"#### 🆚 Pertemuan Langsung {selected_home} vs {selected_away}")
    display_cols = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'predicted_code']
    h2h_show = head2head[display_cols].copy()
    h2h_show['Date'] = h2h_show['Date'].dt.strftime('%Y-%m-%d')
    h2h_show.rename(columns={
        'FTHG': 'Home Goals',
        'FTAG': 'Away Goals',
        'FTR': 'Result',
        'predicted_code': 'Prediction'
    }, inplace=True)
    st.dataframe(h2h_show.reset_index(drop=True))

    # Summary actual and predicted points in these matches
    st.markdown("#### Summary Points H2H Matches")
    h2h_actual = compute_points(head2head, use_actual=True)
    h2h_pred = compute_points(head2head, use_actual=False)
    h2h_summary = h2h_actual.merge(h2h_pred, on='Team', suffixes=('_Actual', '_Predicted'))
    st.dataframe(h2h_summary)

st.markdown("---")
st.caption("Dashboard dibuat oleh El | Data & Prediksi EPL 2024/2025")


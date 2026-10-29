import streamlit as st
import folium
from streamlit_folium import st_folium

from src.osm_data import fetch_yerevan_data
from src.scoring import score_candidates
from src.finance import calculate_financials

st.set_page_config(page_title="EV Location Optimizer | Yerevan", page_icon="⚡", layout="wide")
st.title("⚡ EV Charging Location Optimizer")
st.caption("Երևանի լիցքավորման կայանների տեղադրության նախնական վերլուծություն")

st.sidebar.header("Մոդելի կարգավորումներ")
budget = st.sidebar.selectbox(
    "Ընդհանուր բյուջե (AMD)",
    [5_000_000, 7_500_000, 10_000_000],
    format_func=lambda x: f"{x:,.0f} AMD",
)
charger_type = st.sidebar.selectbox("Լիցքավորիչի տեսակ", ["AC", "DC"])
sessions = st.sidebar.slider("Լիցքավորման սեանսներ՝ օրական", 1, 20, 3 if charger_type == "AC" else 6)
kwh = st.sidebar.slider("Միջին էներգիա մեկ սեանսի համար (kWh)", 5, 60, 20 if charger_type == "AC" else 25)
selling_price = st.sidebar.number_input("Վաճառքի գին (AMD/kWh)", min_value=1, value=120 if charger_type == "AC" else 200)
electricity_cost = st.sidebar.number_input(
    "Էլեկտրաէներգիայի ինքնարժեք (AMD/kWh)", min_value=1, value=60,
    help="Նախնական ենթադրություն է, ոչ թե հաստատված բիզնես սակագին։",
)
fixed_cost = st.sidebar.number_input("Ամսական ֆիքսված ծախսեր (AMD)", min_value=0, value=150_000)
installation_cost = st.sidebar.number_input("Տեղադրման և միացման նախնական ծախս (AMD)", min_value=0, value=500_000)

st.warning(
    "Սարքավորման գները, էլեկտրաէներգիայի արժեքը, օգտագործման ծավալը և տեղադրման ծախսը "
    "նախնական մոդելային ենթադրություններ են։ Հաստատիր դրանք մատակարարի և ցանցային օպերատորի հետ։"
)

@st.cache_data(ttl=3600, show_spinner=False)
def load_data():
    return fetch_yerevan_data()

try:
    with st.spinner("Ներբեռնում ենք OpenStreetMap տվյալները..."):
        data = load_data()
except Exception as exc:
    st.error("Չհաջողվեց ներբեռնել քարտեզային տվյալները։ Ստուգիր ինտերնետ կապը կամ փորձիր ավելի ուշ։")
    st.caption(f"Տեխնիկական մանրամասներ՝ {exc}")
    st.stop()

stations = data[data["category"] == "Existing charger"].copy()
candidates = score_candidates(data)
finance = calculate_financials(
    charger_type=charger_type,
    sessions_per_day=sessions,
    kwh_per_session=kwh,
    selling_price=selling_price,
    electricity_cost=electricity_cost,
    monthly_fixed_cost=fixed_cost,
    installation_cost=installation_cost,
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("OSM-ում գրանցված լիցքավորիչներ", len(stations))
c2.metric("Գնահատվող վայրեր", len(candidates))
c3.metric("Մոդելային ամսական եկամուտ", f'{finance["monthly_revenue_amd"]:,.0f} AMD')
c4.metric("Մոդելային ամսական շահույթ", f'{finance["monthly_profit_amd"]:,.0f} AMD')

if finance["initial_investment_amd"] <= budget:
    st.success(f'Սարքի և նշված տեղադրման ծախսի նախնական գումարը՝ {finance["initial_investment_amd"]:,.0f} AMD, տեղավորվում է բյուջեում։')
else:
    st.warning(f'Նախնական գումարը՝ {finance["initial_investment_amd"]:,.0f} AMD, գերազանցում է ընտրված բյուջեն։')

if finance["payback_months"] is not None:
    st.metric("Պարզ հաշվարկով վերադարձի ժամկետ", f'{finance["payback_months"]:.1f} ամիս')
else:
    st.info("Այս մուտքերով մոդելային գործառնական շահույթը դրական չէ, ուստի վերադարձի ժամկետ չի հաշվարկվում։")

st.subheader("Երևանի քարտեզ")
m = folium.Map(location=[40.1792, 44.4991], zoom_start=12, tiles="OpenStreetMap")

for _, row in stations.iterrows():
    folium.CircleMarker(
        [row["latitude"], row["longitude"]], radius=5, color="blue",
        fill=True, fill_opacity=0.8,
        popup=f'Լիցքավորիչ՝ {row["name"]}<br>Օպերատոր՝ {row["operator"]}<br>Հզորություն՝ {row["power"]}',
    ).add_to(m)

for _, row in candidates.head(50).iterrows():
    folium.CircleMarker(
        [row["latitude"], row["longitude"]], radius=6, color="green",
        fill=True, fill_opacity=0.65,
        popup=f'Հնարավոր վայր՝ {row["name"]}<br>Տեսակ՝ {row["category"]}<br>Գնահատական՝ {row["score"]:.1f}/100<br>Մոտակա քարտեզագրված լիցքավորիչ՝ {row["nearest_station_km"]:.2f} կմ',
    ).add_to(m)

st_folium(m, height=600, use_container_width=True)

st.subheader("Առաջարկվող վայրերի ցանկ")
if not candidates.empty:
    st.dataframe(
        candidates[["name", "category", "nearest_station_km", "score", "latitude", "longitude"]].rename(columns={
            "name": "Վայր", "category": "Տեսակ", "nearest_station_km": "Մոտակա լիցքավորիչ (կմ)",
            "score": "Նախնական գնահատական", "latitude": "Լայնություն", "longitude": "Երկայնություն",
        }),
        use_container_width=True, hide_index=True,
    )
else:
    st.info("OpenStreetMap-ի այս տվյալներով հնարավոր վայրեր չեն գտնվել։")

st.caption("Տվյալների աղբյուր՝ OpenStreetMap contributors։ Գնահատականները նախնական են և չեն ներկայացնում չափված պահանջարկ։")

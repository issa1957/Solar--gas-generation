import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ==========================================
# إعدادات الصفحة والخط العربي
# ==========================================
st.set_page_config(page_title="Hybrid Power Plant Digital Twin", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri&display=swap');
.stMarkdown, .stMetric, .stSelectbox, .stSlider, h1, h2, h3, p, label {
    font-family: 'Amiri', serif !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. نموذج الإنتاج الشمسي (PV System Model)
# ==========================================

class SolarPVModel:
    def __init__(self, capacity_mw, location='Tripoli', efficiency=0.20):
        self.capacity_mw = capacity_mw
        self.location = location
        self.efficiency = efficiency
        self.degradation_rate = 0.005
        
    def get_hourly_generation(self, day_of_year, hour, dust_factor=1.0, temp=25):
        solar_angle = self._calculate_solar_angle(day_of_year, hour)
        if solar_angle <= 0:
            return 0.0
        
        irradiance = 1000 * np.sin(np.radians(solar_angle))
        temp_coefficient = max(0, 1 - 0.005 * (temp - 25))
        
        generation = (
            self.capacity_mw * 
            (irradiance / 1000) * 
            dust_factor * 
            temp_coefficient *
            np.sin(np.radians(solar_angle))
        )
        return max(0, generation)
    
    def _calculate_solar_angle(self, day_of_year, hour):
        declination = 23.45 * np.sin(np.radians((360/365) * (day_of_year - 81)))
        hour_angle = 15 * (hour - 12)
        latitudes = {'Tripoli': 32.9, 'Benghazi': 32.1, 'Sebha': 27.0, 'Sirte': 31.2}
        latitude = latitudes.get(self.location, 32.9)
        
        solar_angle = np.degrees(np.arcsin(
            np.sin(np.radians(latitude)) * np.sin(np.radians(declination)) +
            np.cos(np.radians(latitude)) * np.cos(np.radians(declination)) * np.cos(np.radians(hour_angle))
        ))
        return max(0, solar_angle)


# ==========================================
# 2. نموذج التوربينات الغازية (Gas Turbine Model)
# ==========================================

class GasTurbineModel:
    def __init__(self, capacity_mw, efficiency=0.38, fuel_cost_per_kwh=0.0102):
        self.capacity_mw = capacity_mw
        self.efficiency = efficiency
        self.fuel_cost_per_kwh = fuel_cost_per_kwh
        
    def calculate_cost(self, generation_mw, hours):
        energy_kwh = generation_mw * hours * 1000
        fuel_cost = energy_kwh * self.fuel_cost_per_kwh
        om_cost = energy_kwh * 0.005  # O&M cost
        return fuel_cost + om_cost


# ==========================================
# 3. خوارزمية التحميل الأمثل (Optimal Dispatch)
# ==========================================

class OptimalDispatchOptimizer:
    def __init__(self, solar_plant, gas_plant, load_profile_mw):
        self.solar = solar_plant
        self.gas = gas_plant
        self.load = load_profile_mw
        
    def optimize_24h(self, day_of_year, dust_factor=1.0):
        hourly_results = []
        for hour in range(24):
            current_load = self.load[hour]
            solar_available = self.solar.get_hourly_generation(day_of_year, hour, dust_factor)
            
            if solar_available >= current_load:
                solar_gen = current_load
                gas_gen = 0
            else:
                solar_gen = solar_available
                gas_gen = current_load - solar_available
            
            solar_cost = solar_gen * 0.002  # LCOE for solar
            gas_cost = self.gas.calculate_cost(gas_gen, 1)
            
            hourly_results.append({
                'hour': hour,
                'load_mw': current_load,
                'solar_mw': solar_gen,
                'gas_mw': gas_gen,
                'total_cost': solar_cost + gas_cost
            })
        return pd.DataFrame(hourly_results)


# ==========================================
# 4. واجهة Streamlit التفاعلية
# ==========================================

st.title("⚡ التوأم الرقمي: محطة كهرباء هجينة (شمسي + غازي)")
st.markdown("""
نظام محاكاة متقدم لتحديد المزيج الأمثل بين الطاقة الشمسية والغاز الطبيعي 
لتقليل تكلفة الإنتاج وزيادة الكفاءة التشغيلية.
""")

st.sidebar.header("⚙️ معلمات المحطة")
solar_capacity = st.sidebar.slider("القدرة الشمسية (MW)", 0, 500, 100)
gas_capacity = st.sidebar.slider("القدرة الغازية (MW)", 0, 500, 200)
location = st.sidebar.selectbox("الموقع", ['Tripoli', 'Benghazi', 'Sebha', 'Sirte'])
dust_factor = st.sidebar.slider("عامل نظافة الألواح (1.0 = نظيف تماماً)", 0.5, 1.0, 0.85)

# الحمل الكهربائي الافتراضي (نموذج يومي لمصفاة أو مدينة)
default_load = [
    150, 150, 150, 150, 150, 180,  # 00:00 - 05:00
    220, 260, 280, 300, 320, 340,  # 06:00 - 11:00
    350, 360, 350, 340, 330, 320,  # 12:00 - 17:00
    300, 280, 250, 220, 190, 160   # 18:00 - 23:00
]

# إنشاء النماذج وتشغيل المحاكاة
solar_plant = SolarPVModel(solar_capacity, location)
gas_plant = GasTurbineModel(gas_capacity)
optimizer = OptimalDispatchOptimizer(solar_plant, gas_plant, default_load)

day_of_year = st.sidebar.slider("اليوم في السنة (1-365)", 1, 365, 172)  # 172 = منتصف الصيف
results = optimizer.optimize_24h(day_of_year, dust_factor)

# ==========================================
# 5. عرض النتائج
# ==========================================

st.markdown("### 📊 النتائج اليومية")
col1, col2, col3, col4 = st.columns(4)

total_solar = results['solar_mw'].sum()
total_gas = results['gas_mw'].sum()
total_cost = results['total_cost'].sum()
solar_fraction = total_solar / (total_solar + total_gas) if (total_solar + total_gas) > 0 else 0

col1.metric("إجمالي الإنتاج الشمسي (MWh)", f"{total_solar:.1f}")
col2.metric("إجمالي الإنتاج الغازي (MWh)", f"{total_gas:.1f}")
col3.metric("التكلفة الإجمالية ($)", f"{total_cost:.0f}")
col4.metric("نسبة الاعتماد على الشمس", f"{solar_fraction*100:.1f}%")

st.markdown("---")
st.markdown("### 📈 التحليل البياني")

tab1, tab2 = st.tabs(["توزيع الحمل على 24 ساعة", "التكلفة hourly"])

with tab1:
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(range(24), results['load_mw'], alpha=0.3, label='الحمل الكلي', color='gray')
    ax.bar(range(24), results['solar_mw'], label='الطاقة الشمسية', color='orange')
    ax.bar(range(24), results['gas_mw'], bottom=results['solar_mw'], label='الطاقة الغازية', color='blue')
    ax.set_xlabel('الساعة')
    ax.set_ylabel('القدرة (MW)')
    ax.set_title('توزيع الحمل على مدار 24 ساعة')
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

with tab2:
    fig2, ax2 = plt.subplots(figsize=(12, 4))
    ax2.plot(range(24), results['total_cost'], marker='o', color='red', linewidth=2)
    ax2.set_xlabel('الساعة')
    ax2.set_ylabel('التكلفة ($/hour)')
    ax2.set_title('التكلفة hourly للإنتاج')
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)

st.markdown("---")
st.info("""
💡 **ملاحظة هندسية:** 
- في ساعات الذروة الشمسية (10:00 - 16:00)، يتم الاعتماد بشكل كبير على الطاقة الشمسية.
- عامل نظافة الألواح يؤثر بشكل مباشر على الإنتاج (الغبار يقلل الكفاءة 15-30% في ليبيا).
- التوأم الرقمي يضمن عدم تجاوز قدرة التوربينات الغازية عند انخفاض الإنتاج الشمسي فجأة.
""")

st.success("📩 **مركز التوأم الرقمي للعمليات: contact@thermotwin-center.ly**")

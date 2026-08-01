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
،# new code begins


# nee code ends 

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

class SolarPVModel:
    def __init__(self, capacity_mw, location='Tripoli', efficiency=0.20):
        self.capacity_mw = capacity_mw
        self.location = location
        self.efficiency = efficiency
        self.degradation_rate = 0.005
        

import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from collections import deque
import random
import json

# إعدادات الصفحة
st.set_page_config(
    page_title="منظومة الدفاع الجوي الذكية",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS محسّن واحترافي
st.markdown("""
<style>
    /* خطوط عربية احترافية */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Inter:wght@400;600;700;900&display=swap');
    
    * {
        font-family: 'Cairo', 'Inter', sans-serif !important;
    }
    
    /* إخفاء عناصر Streamlit الافتراضية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* خلفية الصفحة */
    .stApp {
        background: linear-gradient(135deg, #0a0e27, #1a1d3a, #0f1729);
        color: white;
    }
    
    /* العنوان الرئيسي */
    .main-header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #2563eb 100%);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 40px;
        box-shadow: 0 20px 60px rgba(79, 70, 229, 0.4);
        border: 3px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 3rem;
        font-weight: 900;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
        position: relative;
        z-index: 1;
        letter-spacing: 1px;
    }
    
    .main-header p {
        margin: 15px 0 0 0;
        font-size: 1.2rem;
        opacity: 0.95;
        position: relative;
        z-index: 1;
        font-weight: 600;
    }
    
    .main-header .subtitle {
        font-size: 1rem;
        opacity: 0.85;
        margin-top: 10px;
        font-weight: 400;
    }
    
    /* بطاقات الإحصائيات */
    .metric-card {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.15) 0%, rgba(124, 58, 237, 0.15) 100%);
        backdrop-filter: blur(20px);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        border: 2px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transition: left 0.5s;
    }
    
    .metric-card:hover::before {
        left: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 50px rgba(79, 70, 229, 0.5);
        border-color: rgba(255, 255, 255, 0.3);
    }
    
    .metric-card h3 {
        margin: 0 0 20px 0;
        font-size: 1.1rem;
        font-weight: 700;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .metric-card h1 {
        margin: 0;
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 0 30px rgba(96, 165, 250, 0.5));
        line-height: 1.2;
    }
    
    .metric-card .subtitle {
        margin-top: 15px;
        font-size: 0.95rem;
        opacity: 0.8;
        font-weight: 600;
        letter-spacing: 1px;
    }
    
    /* حالة التهديد */
    .threat-alert {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 50%, #f87171 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        animation: alertPulse 2s infinite;
        text-align: center;
        font-weight: 700;
        box-shadow: 0 0 40px rgba(239, 68, 68, 0.7);
        border: 3px solid rgba(255, 255, 255, 0.4);
        font-size: 1.3rem;
        position: relative;
        overflow: hidden;
    }
    
    .threat-alert::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 10px,
            rgba(255,255,255,0.1) 10px,
            rgba(255,255,255,0.1) 20px
        );
        animation: slideStripes 20s linear infinite;
    }
    
    @keyframes slideStripes {
        0% { transform: translate(0, 0); }
        100% { transform: translate(50px, 50px); }
    }
    
    @keyframes alertPulse {
        0%, 100% { 
            box-shadow: 0 0 40px rgba(239, 68, 68, 0.7);
            transform: scale(1);
        }
        50% { 
            box-shadow: 0 0 60px rgba(239, 68, 68, 1);
            transform: scale(1.02);
        }
    }
    
    /* حالة آمن */
    .safe-status {
        background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        text-align: center;
        font-weight: 700;
        box-shadow: 0 0 40px rgba(16, 185, 129, 0.5);
        border: 3px solid rgba(255, 255, 255, 0.4);
        font-size: 1.3rem;
        position: relative;
        overflow: hidden;
    }
    
    .safe-status::after {
        content: '✓';
        position: absolute;
        font-size: 200px;
        opacity: 0.1;
        right: -30px;
        top: -60px;
        font-weight: 900;
    }
    
    /* سجل المحاكاة */
    .simulation-log {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        color: #00ff41;
        padding: 25px;
        border-radius: 15px;
        font-family: 'Courier New', 'Consolas', monospace;
        max-height: 450px;
        overflow-y: auto;
        margin: 20px 0;
        border: 3px solid rgba(0, 255, 65, 0.4);
        box-shadow: 0 0 30px rgba(0, 255, 65, 0.3);
        direction: ltr;
        text-align: left;
    }
    
    .simulation-log::-webkit-scrollbar {
        width: 10px;
    }
    
    .simulation-log::-webkit-scrollbar-track {
        background: #1e1e1e;
        border-radius: 10px;
    }
    
    .simulation-log::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00ff41, #00cc33);
        border-radius: 10px;
        border: 2px solid #1e1e1e;
    }
    
    .log-line {
        margin: 8px 0;
        padding: 8px;
        border-left: 4px solid #00ff41;
        padding-left: 12px;
        transition: all 0.3s ease;
        font-size: 0.95rem;
    }
    
    .log-line:hover {
        background: rgba(0, 255, 65, 0.1);
        padding-left: 20px;
    }
    
    .log-alert {
        color: #ff4444;
        border-left-color: #ff4444;
        font-weight: bold;
        animation: logBlink 1s ease-in-out;
    }
    
    .log-cyber {
        color: #00d4ff;
        border-left-color: #00d4ff;
        font-weight: bold;
    }
    
    .log-success {
        color: #00ff41;
        border-left-color: #00ff41;
    }
    
    .log-warning {
        color: #fbbf24;
        border-left-color: #fbbf24;
        font-weight: bold;
    }
    
    @keyframes logBlink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* بطاقات تتبع الطائرات */
    .drone-card {
        background: linear-gradient(135deg, rgba(51, 65, 85, 0.9) 0%, rgba(71, 85, 105, 0.9) 100%);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        border-right: 6px solid #ef4444;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .drone-card::before {
        content: '✈';
        position: absolute;
        font-size: 100px;
        opacity: 0.05;
        right: -10px;
        top: -20px;
        transform: rotate(-45deg);
    }
    
    .drone-card:hover {
        transform: translateX(-8px);
        box-shadow: 0 8px 30px rgba(239, 68, 68, 0.5);
        border-right-width: 8px;
    }
    
    .drone-card h4 {
        margin: 0 0 15px 0;
        color: #ef4444;
        font-weight: 800;
        font-size: 1.2rem;
        letter-spacing: 1px;
    }
    
    .drone-info {
        display: flex;
        justify-content: space-between;
        margin: 8px 0;
        font-size: 0.95rem;
        font-weight: 600;
    }
    
    /* أزرار الإجراءات */
    .stButton button {
        background: linear-gradient(135deg, #f43f5e 0%, #ec4899 50%, #d946ef 100%);
        color: white;
        padding: 15px 30px;
        border-radius: 12px;
        border: none;
        font-size: 1.05rem;
        font-weight: 700;
        cursor: pointer;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(244, 63, 94, 0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(244, 63, 94, 0.6);
        background: linear-gradient(135deg, #fb7185 0%, #f472b6 50%, #e879f9 100%);
    }
    
    /* قسم الإعدادات */
    .settings-section {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        border: 2px solid rgba(255, 255, 255, 0.15);
    }
    
    /* Expander محسّن */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.2) 0%, rgba(124, 58, 237, 0.2) 100%);
        border-radius: 10px;
        border: 2px solid rgba(255, 255, 255, 0.15);
        color: white !important;
        font-weight: 700;
        padding: 15px !important;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.3) 0%, rgba(124, 58, 237, 0.3) 100%);
        border-color: rgba(255, 255, 255, 0.3);
    }
    
    /* التبويبات */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        color: white;
        font-weight: 700;
        padding: 12px 25px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.5);
    }
    
    /* شريط التقدم */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #60a5fa 0%, #818cf8 100%);
    }
    
    /* مؤشر الحالة */
    .status-indicator {
        display: inline-block;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        margin-left: 10px;
        animation: statusBlink 1.5s infinite;
    }
    
    .status-active {
        background: #10b981;
        box-shadow: 0 0 15px #10b981;
    }
    
    .status-alert {
        background: #ef4444;
        box-shadow: 0 0 15px #ef4444;
    }
    
    @keyframes statusBlink {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.9); }
    }
    
    /* قسم المعلومات */
    .info-box {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.12) 0%, rgba(124, 58, 237, 0.12) 100%);
        border-right: 5px solid #4f46e5;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        color: white;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    .info-box h3 {
        color: #818cf8;
        margin-top: 0;
        font-weight: 800;
        font-size: 1.4rem;
    }
    
    .info-box ul {
        line-height: 1.8;
    }
    
    .info-box li {
        margin: 10px 0;
    }
    
    /* جدول البيانات */
    .dataframe {
        background: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border-radius: 15px;
        overflow: hidden;
    }
    
    /* Footer احترافي */
    .custom-footer {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.2) 0%, rgba(124, 58, 237, 0.2) 100%);
        backdrop-filter: blur(15px);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-top: 40px;
        border: 3px solid rgba(255, 255, 255, 0.15);
    }
    
    /* شارات الحالة */
    .badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 700;
        margin: 0 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .badge-success {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
    }
    
    .badge-danger {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
    }
    
    .badge-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(251, 191, 36, 0.4);
    }
    
    .badge-info {
        background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4);
    }
    
    /* رسالة ترحيب */
    .welcome-message {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.18) 0%, rgba(124, 58, 237, 0.18) 100%);
        backdrop-filter: blur(15px);
        padding: 35px;
        border-radius: 20px;
        margin: 30px 0;
        border: 3px solid rgba(255, 255, 255, 0.15);
        color: white;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    }
    
    .welcome-message h3 {
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 15px;
    }
    
    /* Timeline */
    .timeline-item {
        position: relative;
        padding: 20px;
        border-right: 4px solid #4f46e5;
        margin-right: 25px;
        margin-bottom: 20px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    .timeline-item:hover {
        background: rgba(255, 255, 255, 0.12);
        transform: translateX(-5px);
    }
    
    .timeline-item::before {
        content: '';
        position: absolute;
        right: -10px;
        top: 25px;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #4f46e5;
        box-shadow: 0 0 15px #4f46e5;
        border: 3px solid #1a1d3a;
    }
    
    /* Input fields styling */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-weight: 600 !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus {
        border-color: #4f46e5 !important;
        box-shadow: 0 0 15px rgba(79, 70, 229, 0.5) !important;
    }
    
    /* Slider styling */
    .stSlider {
        padding: 10px 0;
    }
    
    /* Checkbox styling */
    .stCheckbox {
        color: white !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# تهيئة Session State
def init_session_state():
    """تهيئة جميع متغيرات الجلسة"""
    defaults = {
        'threat_log': deque(maxlen=100),
        'cyber_attacks': [],
        'detection_history': [],
        'total_threats': 0,
        'neutralized_threats': 0,
        'active_drones': {},
        'simulation_active': False,
        'system_start_time': datetime.now(),
        'total_frames_processed': 0,
        'detection_alerts': [],
        'performance_metrics': {
            'avg_detection_time': 0,
            'fps': 0,
            'memory_usage': 0
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# وظائف مساعدة
def add_threat_log(message, level="INFO"):
    """إضافة سجل تهديد مع تنسيق محسّن"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    level_colors = {
        'INFO': 'log-success',
        'ALERT': 'log-alert',
        'CYBER': 'log-cyber',
        'WARNING': 'log-warning'
    }
    
    log_entry = {
        'time': timestamp,
        'level': level,
        'message': message,
        'color_class': level_colors.get(level, 'log-success')
    }
    
    st.session_state.threat_log.append(log_entry)
    st.session_state.detection_alerts.append(log_entry)

def get_threat_level_badge(confidence):
    """الحصول على شارة مستوى التهديد"""
    if confidence >= 0.9:
        return '<span class="badge badge-danger">High Risk</span>'
    elif confidence >= 0.7:
        return '<span class="badge badge-warning">Medium Risk</span>'
    else:
        return '<span class="badge badge-info">Low Risk</span>'

def simulate_cyber_attack(drone_id, attack_type, position, confidence):
    """محاكاة هجوم إلكتروني متقدم"""
    attack_id = f"CYB-{len(st.session_state.cyber_attacks) + 1:05d}"
    
    # تحديد خطوات الهجوم بناءً على النوع
    attack_sequences = {
        "GPS Spoofing": [
            "⚡ Initializing electronic jamming system",
            "📡 Scanning and analyzing GPS frequency spectrum (L1: 1575.42 MHz)",
            "🎯 Locking target drone GPS signal",
            "🔐 Decrypting NMEA navigation protocol",
            "⚙️ Generating fake GPS coordinates (Lat: 24.7136, Lon: 46.6753)",
            "📊 Gradually increasing fake signal strength (10dBm → 30dBm)",
            "🛰️ Replacing genuine GPS signal with spoofed signal",
            "🔄 Redirecting drone to safe zone away from airport",
            "✅ Operation successful - Drone exiting restricted airspace"
        ],
        "RF Jamming": [
            "🔍 Starting radio frequency spectrum scan",
            "📊 Identifying communication channels: 2.4GHz & 5.8GHz",
            "⚡ Activating white noise generator",
            "📡 Targeting control frequency: 2.437 GHz (Channel 6)",
            "🔊 Increasing jamming power: 100mW → 500mW → 1W",
            "📵 Severing connection between drone and controller",
            "🛑 Activating RTH (Return to Home) mode on drone",
            "🎯 Monitoring drone response to jamming",
            "✅ Control loss confirmed - Initiating safe auto-landing"
        ],
        "Protocol Hijacking": [
            "🔐 Intercepting wireless data packets (Packet Sniffing)",
            "💻 Analyzing communication protocol (MAVLink/DroneCode)",
            "🔓 Decrypting control messages using reverse engineering",
            "🎮 Spoofing original controller (Controller Spoofing)",
            "📨 Injecting custom commands into data stream",
            "🔄 Sending high-priority RTH command",
            "🛡️ Blocking original operator commands (Command Override)",
            "📍 Confirming drone receipt of spoofed commands",
            "✅ Full control achieved - Drone executing system commands"
        ],
        "Multi-Layer Attack": [
            "🚀 Initializing multi-level attack platform",
            "📡 Layer 1: Starting GPS spoofing (Spoofing Layer)",
            "🔊 Layer 2: Activating RF jamming (Jamming Layer)",
            "💻 Layer 3: Protocol hijacking (Hijacking Layer)",
            "⚡ Coordinating simultaneous attacks on all levels",
            "🎯 Targeting navigation, control and communication systems",
            "🔐 Breaking encryption and protection mechanisms",
            "🛑 Forcing immediate emergency landing",
            "📊 Monitoring all system responses",
            "✅ Comprehensive success - Complete threat neutralization"
        ]
    }
    
    steps = attack_sequences.get(attack_type, attack_sequences["GPS Spoofing"])
    duration = random.uniform(3.5, 7.2)
    
    attack_data = {
        'attack_id': attack_id,
        'drone_id': drone_id,
        'attack_type': attack_type,
        'position': position,
        'confidence': confidence,
        'timestamp': datetime.now(),
        'status': 'SUCCESS',
        'steps': steps,
        'duration': duration,
        'threat_level': 'High' if confidence >= 0.8 else 'Medium'
    }
    
    st.session_state.cyber_attacks.append(attack_data)
    st.session_state.neutralized_threats += 1
    
    # إضافة سجل تفصيلي
    add_threat_log(
        f"🎯 {attack_id} | Target: {drone_id} | Type: {attack_type}",
        "CYBER"
    )
    
    return attack_data

@st.cache_resource
def load_model(model_path):
    """تحميل موديل YOLO مع معالجة الأخطاء"""
    try:
        if not Path(model_path).exists():
            st.error(f"❌ Model not found at path: {model_path}")
            return None
        
        model = YOLO(model_path)
        add_threat_log(f"✅ Model loaded successfully: {model_path}", "INFO")
        return model
    except Exception as e:
        st.error(f"❌ Error loading model: {str(e)}")
        add_threat_log(f"❌ Model loading failed: {str(e)}", "ALERT")
        return None

def process_frame(frame, model, conf_threshold, iou_threshold):
    """معالجة إطار الفيديو مع تحسينات الأداء"""
    start_time = time.time()
    
    # تشغيل الكشف
    results = model.predict(
        frame,
        conf=conf_threshold,
        iou=iou_threshold,
        verbose=False,
        device='cpu'
    )
    
    # رسم النتائج
    annotated_frame = results[0].plot()
    
    # جمع معلومات الطائرات
    detected_drones = []
    for i, box in enumerate(results[0].boxes):
        conf = float(box.conf[0])
        bbox = box.xyxy[0].cpu().numpy()
        center_x = int((bbox[0] + bbox[2]) / 2)
        center_y = int((bbox[1] + bbox[3]) / 2)
        
        drone_info = {
            'id': f"UAV-{i+1:03d}",
            'confidence': conf,
            'bbox': bbox,
            'position': (center_x, center_y),
            'size': int((bbox[2] - bbox[0]) * (bbox[3] - bbox[1])),
            'threat_level': 'High' if conf >= 0.8 else 'Medium' if conf >= 0.6 else 'Low'
        }
        detected_drones.append(drone_info)
    
    num_drones = len(detected_drones)
    
    # تحسين الإطار المعروض
    if num_drones > 0:
        # شريط التحذير العلوي
        overlay = annotated_frame.copy()
        cv2.rectangle(overlay, (0, 0), (annotated_frame.shape[1], 100), (0, 0, 139), -1)
        cv2.addWeighted(overlay, 0.7, annotated_frame, 0.3, 0, annotated_frame)
        
        threat_text = f"THREAT ALERT: {num_drones} UNAUTHORIZED DRONE(S) DETECTED"
        cv2.putText(
            annotated_frame,
            threat_text,
            (30, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (255, 255, 255),
            3,
            cv2.LINE_AA
        )
        
        # معلومات إضافية لكل طائرة
        for i, drone in enumerate(detected_drones):
            x, y = int(drone['bbox'][0]), int(drone['bbox'][1]) - 10
            info_text = f"{drone['id']} | {drone['confidence']*100:.1f}%"
            cv2.putText(
                annotated_frame,
                info_text,
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
                cv2.LINE_AA
            )
    else:
        # شريط الحالة الآمنة
        overlay = annotated_frame.copy()
        cv2.rectangle(overlay, (0, 0), (annotated_frame.shape[1], 70), (0, 139, 0), -1)
        cv2.addWeighted(overlay, 0.6, annotated_frame, 0.4, 0, annotated_frame)
        
        cv2.putText(
            annotated_frame,
            "AIRSPACE SECURE - NO THREATS DETECTED",
            (30, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (255, 255, 255),
            3,
            cv2.LINE_AA
        )
    
    # حساب وقت المعالجة
    processing_time = time.time() - start_time
    fps = 1.0 / processing_time if processing_time > 0 else 0
    
    # عرض معلومات الأداء
    cv2.putText(
        annotated_frame,
        f"FPS: {fps:.1f} | Processing: {processing_time*1000:.1f}ms",
        (annotated_frame.shape[1] - 400, annotated_frame.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )
    
    st.session_state.performance_metrics['fps'] = fps
    st.session_state.performance_metrics['avg_detection_time'] = processing_time
    
    return annotated_frame, num_drones, detected_drones, results[0]

# واجهة المستخدم الرئيسية
def main():
    # العنوان الرئيسي
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ منظومة الدفاع الجوي الذكية المتقدمة</h1>
        <p>Advanced AI-Powered Airport Defense & Counter-Drone System</p>
        <p class="subtitle">
            نظام متكامل للكشف والتتبع والإجراءات المضادة | Powered by YOLOv11 & Deep Learning
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # رسالة الترحيب
    if st.session_state.total_threats == 0:
        st.markdown("""
        <div class="welcome-message">
            <h3>🎯 Welcome to the Advanced Air Defense System</h3>
            <p style="font-size: 1.1rem;">نظام متقدم للكشف المبكر عن الطائرات المسيرة غير المصرح بها وتنفيذ الإجراءات المضادة الإلكترونية</p>
            <p style="font-size: 1rem; margin-top: 10px;">Advanced system for early detection of unauthorized drones and electronic countermeasure execution</p>
            <p style="margin-top: 20px;">
                <span class="badge badge-info">AI-Powered Detection</span>
                <span class="badge badge-success">Real-Time Processing</span>
                <span class="badge badge-warning">Advanced Countermeasures</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # لوحة الإحصائيات الرئيسية
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎯 Total Detections<br>إجمالي الكشوفات</h3>
            <h1>{st.session_state.total_threats}</h1>
            <p class="subtitle">Detected Threats</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>✅ Neutralized<br>التهديدات المحيدة</h3>
            <h1>{st.session_state.neutralized_threats}</h1>
            <p class="subtitle">Successfully Eliminated</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        success_rate = (st.session_state.neutralized_threats / st.session_state.total_threats * 100) if st.session_state.total_threats > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Success Rate<br>معدل النجاح</h3>
            <h1>{success_rate:.1f}%</h1>
            <p class="subtitle">Mission Effectiveness</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        active_count = len(st.session_state.active_drones)
        status_class = "status-alert" if active_count > 0 else "status-active"
        st.markdown(f"""
        <div class="metric-card">
            <h3>⚡ Active Threats<br>تهديدات نشطة <span class="status-indicator {status_class}"></span></h3>
            <h1>{active_count}</h1>
            <p class="subtitle">Currently Tracked</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # الشريط الجانبي
    with st.sidebar:
        st.markdown("### ⚙️ Main Control Panel | لوحة التحكم")
        st.markdown("---")
        
        # إعدادات الموديل
        with st.expander("🤖 Model Configuration | إعدادات الموديل", expanded=True):
            model_path = st.text_input(
                "Model Path | مسار الموديل",
                value="/Users/mazin/Desktop/UJ/best_drone_model.pt",
                help="Enter YOLOv11 model file path | أدخل مسار ملف موديل YOLOv11",
                key="model_path_input"
            )
            
            if st.button("🔄 Reload Model | إعادة تحميل الموديل", use_container_width=True):
                st.cache_resource.clear()
                st.rerun()
        
        st.markdown("---")
        
        # إعدادات الكشف
        with st.expander("🎯 Detection Settings | إعدادات الكشف", expanded=True):
            confidence_threshold = st.slider(
                "Confidence Threshold | عتبة الثقة",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.05,
                help="Minimum detection confidence | الحد الأدنى لثقة الكشف"
            )
            
            iou_threshold = st.slider(
                "IOU Threshold | عتبة IOU",
                min_value=0.0,
                max_value=1.0,
                value=0.45,
                step=0.05,
                help="Bounding box overlap threshold | عتبة تداخل الصناديق المحيطة"
            )
        
        st.markdown("---")
        
        # إعدادات الدفاع
        with st.expander("🛡️ Defense Configuration | إعدادات الدفاع", expanded=True):
            airport_radius = st.number_input(
                "Protection Radius (km) | نطاق الحماية",
                min_value=1,
                max_value=50,
                value=5,
                help="Restricted zone radius around airport | نطاق المنطقة المحظورة حول المطار"
            )
            
            auto_countermeasure = st.checkbox(
                "🤖 Automatic Countermeasures | الإجراءات المضادة التلقائية",
                value=False,
                help="Enable automatic response upon detection | تفعيل الاستجابة التلقائية عند الكشف"
            )
            
            cyber_attack_type = st.selectbox(
                "⚡ Countermeasure Type | نوع الإجراء المضاد",
                [
                    "GPS Spoofing",
                    "RF Jamming",
                    "Protocol Hijacking",
                    "Multi-Layer Attack"
                ],
                help="Select electronic counter-attack type | اختر نوع الهجوم الإلكتروني المضاد"
            )
        
        st.markdown("---")
        
        # معلومات النظام
        with st.expander("ℹ️ System Information | معلومات النظام"):
            uptime = datetime.now() - st.session_state.system_start_time
            st.write(f"**Uptime | وقت التشغيل:** {str(uptime).split('.')[0]}")
            st.write(f"**Frames Processed | الإطارات المعالجة:** {st.session_state.total_frames_processed}")
            st.write(f"**Average FPS | متوسط FPS:** {st.session_state.performance_metrics['fps']:.1f}")
            st.write(f"**Processing Time | وقت المعالجة:** {st.session_state.performance_metrics['avg_detection_time']*1000:.1f}ms")
        
        st.markdown("---")
        
        # أزرار التحكم
        if st.button("🗑️ Clear Logs | مسح السجلات", use_container_width=True):
            st.session_state.threat_log.clear()
            st.session_state.cyber_attacks.clear()
            st.session_state.detection_alerts.clear()
            st.success("✅ Logs cleared successfully | تم مسح السجلات")
            time.sleep(1)
            st.rerun()
        
        if st.button("🔄 Reset Statistics | إعادة تعيين الإحصائيات", use_container_width=True):
            st.session_state.total_threats = 0
            st.session_state.neutralized_threats = 0
            st.session_state.active_drones.clear()
            st.success("✅ Statistics reset successfully | تم إعادة التعيين")
            time.sleep(1)
            st.rerun()
    
    # تحميل الموديل
    model = load_model(model_path)
    
    if model is None:
        st.error("⚠️ Please verify the correct model path and try again | الرجاء التأكد من مسار الموديل الصحيح")
        st.stop()
    
    # اختيار المصدر
    st.markdown("### 📹 Surveillance Source | مصدر المراقبة")
    source_tabs = st.tabs(["📁 Upload Video | رفع فيديو", "📹 Live Camera | كاميرا مباشرة"])
    
    # تبويب رفع الفيديو
    with source_tabs[0]:
        uploaded_file = st.file_uploader(
            "Choose video file for analysis | اختر ملف فيديو للتحليل",
            type=["mp4", "avi", "mov", "mkv", "flv"],
            help="Supported formats: MP4, AVI, MOV, MKV, FLV | صيغ مدعومة"
        )
        
        if uploaded_file is not None:
            # إنشاء أعمدة للعرض
            main_col, sidebar_col = st.columns([2, 1])
            
            with main_col:
                # حفظ الفيديو
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tfile:
                    tfile.write(uploaded_file.read())
                    video_path = tfile.name
                
                # فتح الفيديو
                cap = cv2.VideoCapture(video_path)
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = total_frames / fps if fps > 0 else 0
                
                st.success(f"✅ Video loaded | Duration: {duration:.1f}s | Frames: {total_frames} | FPS: {fps}")
                
                # أزرار التحكم
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    start_analysis = st.button("▶️ Start Analysis | بدء التحليل", use_container_width=True, type="primary")
                with col2:
                    pause_analysis = st.button("⏸️ Pause | إيقاف مؤقت", use_container_width=True)
                with col3:
                    stop_analysis = st.button("⏹️ Stop | إيقاف", use_container_width=True)
                
                if start_analysis:
                    # عناصر العرض
                    video_placeholder = st.empty()
                    progress_bar = st.progress(0)
                    status_col1, status_col2 = st.columns(2)
                    
                    frame_count = 0
                    is_paused = False
                    
                    while cap.isOpened() and not stop_analysis:
                        if not is_paused:
                            ret, frame = cap.read()
                            if not ret:
                                break
                            
                            # معالجة الإطار
                            annotated_frame, num_drones, detected_drones, _ = process_frame(
                                frame, model, confidence_threshold, iou_threshold
                            )
                            
                            frame_count += 1
                            st.session_state.total_frames_processed += 1
                            
                            # معالجة الكشوفات
                            if num_drones > 0:
                                st.session_state.total_threats += num_drones
                                
                                for drone in detected_drones:
                                    drone_id = f"{drone['id']}-F{frame_count:05d}"
                                    st.session_state.active_drones[drone_id] = {
                                        **drone,
                                        'detection_time': datetime.now(),
                                        'frame': frame_count
                                    }
                                    
                                    add_threat_log(
                                        f"🚨 [{drone_id}] Drone detected | Confidence: {drone['confidence']:.1%} | Frame: {frame_count}",
                                        "ALERT"
                                    )
                                    
                                    # تفعيل الإجراء المضاد
                                    if auto_countermeasure:
                                        attack_data = simulate_cyber_attack(
                                            drone_id,
                                            cyber_attack_type,
                                            drone['position'],
                                            drone['confidence']
                                        )
                                        add_threat_log(
                                            f"⚡ [{attack_data['attack_id']}] Countermeasure executed on {drone_id}",
                                            "CYBER"
                                        )
                            
                            # عرض الإطار
                            video_placeholder.image(
                                cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB),
                                channels="RGB",
                                use_container_width=True
                            )
                            
                            # تحديث شريط التقدم
                            progress = int((frame_count / total_frames) * 100)
                            progress_bar.progress(progress, text=f"Progress: {progress}% | Frame: {frame_count}/{total_frames}")
                            
                            # عرض الحالة
                            with status_col1:
                                if num_drones > 0:
                                    st.markdown(f"""
                                    <div class="threat-alert">
                                        <strong>🚨 SECURITY ALERT!</strong><br>
                                        {num_drones} drone(s) detected in frame {frame_count}
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown("""
                                    <div class="safe-status">
                                        <strong>✅ AIRSPACE SECURE</strong><br>
                                        No threats detected
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            with status_col2:
                                st.markdown(f"""
                                <div class="info-box" style="margin: 0;">
                                    <strong>📊 Frame Statistics:</strong><br>
                                    • Detections: {num_drones}<br>
                                    • FPS: {st.session_state.performance_metrics['fps']:.1f}<br>
                                    • Time: {st.session_state.performance_metrics['avg_detection_time']*1000:.1f}ms
                                </div>
                                """, unsafe_allow_html=True)
                        
                        if pause_analysis:
                            is_paused = not is_paused
                        
                        if stop_analysis:
                            break
                    
                    cap.release()
                    st.success("✅ Analysis completed successfully!")
                    add_threat_log(f"✅ Video analysis complete | Frames: {frame_count} | Detections: {st.session_state.total_threats}", "INFO")
            
            with sidebar_col:
                display_sidebar_controls(cyber_attack_type)
    
    # تبويب الكاميرا المباشرة
    with source_tabs[1]:
        st.info("📹 Make sure to grant browser access to camera permissions")
        
        camera_index = st.number_input(
            "Camera Index | رقم الكاميرا",
            min_value=0,
            max_value=10,
            value=0,
            help="Camera identification number in system | رقم تعريف الكاميرا"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            start_camera = st.button("📹 Start Live Monitoring | تشغيل المراقبة", use_container_width=True, type="primary")
        with col2:
            stop_camera = st.button("⏹️ Stop Monitoring | إيقاف المراقبة", use_container_width=True)
        
        if start_camera:
            cap = cv2.VideoCapture(camera_index)
            
            if not cap.isOpened():
                st.error("❌ Failed to access camera. Check connection and browser permissions.")
            else:
                add_threat_log("📹 Live monitoring started", "INFO")
                
                main_col, sidebar_col = st.columns([2, 1])
                
                with main_col:
                    camera_placeholder = st.empty()
                    status_placeholder = st.empty()
                
                frame_count = 0
                
                while cap.isOpened() and not stop_camera:
                    ret, frame = cap.read()
                    if not ret:
                        st.error("❌ Failed to read frame from camera")
                        break
                    
                    # معالجة الإطار
                    annotated_frame, num_drones, detected_drones, _ = process_frame(
                        frame, model, confidence_threshold, iou_threshold
                    )
                    
                    frame_count += 1
                    st.session_state.total_frames_processed += 1
                    
                    # معالجة الكشوفات
                    if num_drones > 0:
                        st.session_state.total_threats += num_drones
                        
                        for drone in detected_drones:
                            drone_id = f"{drone['id']}-LIVE-{int(time.time()*1000)}"
                            st.session_state.active_drones[drone_id] = {
                                **drone,
                                'detection_time': datetime.now(),
                                'frame': frame_count
                            }
                            
                            add_threat_log(
                                f"🚨 [LIVE] {drone_id} | Confidence: {drone['confidence']:.1%}",
                                "ALERT"
                            )
                            
                            if auto_countermeasure:
                                attack_data = simulate_cyber_attack(
                                    drone_id,
                                    cyber_attack_type,
                                    drone['position'],
                                    drone['confidence']
                                )
                    
                    # عرض الإطار
                    camera_placeholder.image(
                        cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB),
                        channels="RGB",
                        use_container_width=True
                    )
                    
                    # عرض الحالة
                    if num_drones > 0:
                        status_placeholder.markdown(f"""
                        <div class="threat-alert">
                            <strong>🚨 LIVE ALERT!</strong><br>
                            {num_drones} drone(s) currently detected
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        status_placeholder.markdown("""
                        <div class="safe-status">
                            <strong>✅ MONITORING ACTIVE</strong><br>
                            Airspace secure
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with sidebar_col:
                        display_sidebar_controls(cyber_attack_type)
                    
                    time.sleep(0.03)
                
                cap.release()
                add_threat_log("⏹️ Live monitoring stopped", "INFO")
                st.success("✅ Live monitoring stopped successfully")
    
    # قسم التحليلات
    display_analytics_section()
    
    # معلومات ختامية
    display_footer()

def display_sidebar_controls(cyber_attack_type):
    """عرض عناصر التحكم في الشريط الجانبي"""
    st.markdown("### 🎮 Control Panel | لوحة التحكم")
    
    # الطائرات النشطة
    if len(st.session_state.active_drones) > 0:
        st.markdown("#### ⚡ Active Threats | التهديدات النشطة")
        
        for drone_id, drone in list(st.session_state.active_drones.items())[:5]:
            with st.container():
                st.markdown(f"""
                <div class="drone-card">
                    <h4>🎯 {drone_id}</h4>
                    <div class="drone-info">
                        <span>Confidence | الثقة:</span>
                        <span>{drone['confidence']:.1%}</span>
                    </div>
                    <div class="drone-info">
                        <span>Level | المستوى:</span>
                        <span>{get_threat_level_badge(drone['confidence'])}</span>
                    </div>
                    <div class="drone-info">
                        <span>Time | الوقت:</span>
                        <span>{drone.get('detection_time', datetime.now()).strftime('%H:%M:%S')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(
                    f"⚡ Neutralize | تحييد {drone_id}",
                    key=f"neutralize_{drone_id}_{int(time.time()*1000)}",
                    use_container_width=True
                ):
                    attack_data = simulate_cyber_attack(
                        drone_id,
                        cyber_attack_type,
                        drone['position'],
                        drone['confidence']
                    )
                    
                    with st.expander(f"📋 {attack_data['attack_id']}", expanded=True):
                        st.markdown(f"**Target | الهدف:** {drone_id}")
                        st.markdown(f"**Type | النوع:** {attack_data['attack_type']}")
                        st.markdown(f"**Duration | المدة:** {attack_data['duration']:.2f}s")
                        st.markdown("**Execution Steps | خطوات التنفيذ:**")
                        
                        for i, step in enumerate(attack_data['steps'], 1):
                            st.write(f"{i}. {step}")
                            time.sleep(0.1)
                    
                    st.success(f"✅ {drone_id} neutralized successfully!")
                    del st.session_state.active_drones[drone_id]
                    time.sleep(1)
                    st.rerun()
                
                st.markdown("---")
    else:
        st.info("No active threats currently | لا توجد تهديدات نشطة حالياً")
    
    # سجل النظام
    st.markdown("### 📊 System Log | سجل النظام")
    
    if len(st.session_state.threat_log) > 0:
        log_html = "<div class='simulation-log'>"
        for log in list(st.session_state.threat_log)[-12:]:
            log_html += f"<div class='log-line {log['color_class']}'>[{log['time']}] {log['level']}: {log['message']}</div>"
        log_html += "</div>"
        st.markdown(log_html, unsafe_allow_html=True)
    else:
        st.info("No logs yet... | لا توجد سجلات بعد")

def display_analytics_section():
    """عرض قسم التحليلات والإحصائيات"""
    st.markdown("---")
    st.markdown("## 📊 Analytics & Reports | التحليلات والتقارير")
    
    if len(st.session_state.cyber_attacks) > 0:
        tabs = st.tabs([
            "📈 Statistics | الإحصائيات",
            "⚡ Cyber Operations | العمليات الإلكترونية",
            "📋 Comprehensive Report | التقرير الشامل",
            "📉 Visualizations | الرسوم البيانية"
        ])
        
        # تبويب الإحصائيات
        with tabs[0]:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_attacks = len(st.session_state.cyber_attacks)
                st.metric("Total Counter-Operations | إجمالي العمليات", total_attacks, delta=f"+{total_attacks}")
            
            with col2:
                avg_duration = np.mean([a['duration'] for a in st.session_state.cyber_attacks])
                st.metric("Average Duration | متوسط المدة", f"{avg_duration:.2f}s", delta="Fast")
            
            with col3:
                success_rate = 100.0
                st.metric("Success Rate | معدل النجاح", f"{success_rate}%", delta="Excellent")
            
            st.markdown("---")
            
            # الرسوم البيانية
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # توزيع أنواع الهجمات
                attack_types = [a['attack_type'] for a in st.session_state.cyber_attacks]
                attack_df = pd.DataFrame({'Type': attack_types})
                type_counts = attack_df['Type'].value_counts()
                
                fig = px.pie(
                    values=type_counts.values,
                    names=type_counts.index,
                    title="Counter-Operation Type Distribution | توزيع أنواع العمليات",
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Plasma
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', family='Cairo, Inter')
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with chart_col2:
                # مدة العمليات
                durations = [a['duration'] for a in st.session_state.cyber_attacks]
                attacks_ids = [a['attack_id'] for a in st.session_state.cyber_attacks]
                
                fig = px.bar(
                    x=attacks_ids[-10:],
                    y=durations[-10:],
                    title="Last 10 Operations Duration | مدة آخر 10 عمليات",
                    labels={'x': 'Operation ID | رقم العملية', 'y': 'Duration (seconds) | المدة'},
                    color=durations[-10:],
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', family='Cairo, Inter')
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # تبويب الهجمات
        with tabs[1]:
            st.markdown("### ⚡ Detailed Cyber Operations Log | سجل العمليات الإلكترونية")
            
            for attack in reversed(st.session_state.cyber_attacks[-15:]):
                with st.expander(
                    f"🎯 {attack['attack_id']} | {attack['drone_id']} | "
                    f"{attack['timestamp'].strftime('%H:%M:%S')} | "
                    f"{attack['attack_type']}",
                    expanded=False
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        **Operation Information | معلومات العملية:**
                        - **Operation ID | معرف العملية:** {attack['attack_id']}
                        - **Target | الهدف:** {attack['drone_id']}
                        - **Attack Type | نوع الهجوم:** {attack['attack_type']}
                        - **Threat Level | مستوى التهديد:** {attack['threat_level']}
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        **Results | النتائج:**
                        - **Status | الحالة:** ✅ {attack['status']}
                        - **Duration | المدة:** {attack['duration']:.2f} seconds
                        - **Confidence | الثقة:** {attack['confidence']:.1%}
                        - **Time | الوقت:** {attack['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                        """)
                    
                    st.markdown("**Execution Steps | خطوات التنفيذ:**")
                    for i, step in enumerate(attack['steps'], 1):
                        st.markdown(f"{i}. {step}")
        
        # تبويب التقرير الشامل
        with tabs[2]:
            st.markdown("### 📋 Comprehensive Detailed Report | التقرير التفصيلي الشامل")
            
            # إحصائيات عامة
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Detections | إجمالي الكشوفات", st.session_state.total_threats)
            with col2:
                st.metric("Neutralized | المحيدة", st.session_state.neutralized_threats)
            with col3:
                st.metric("Success Rate | معدل النجاح", f"{(st.session_state.neutralized_threats/st.session_state.total_threats*100) if st.session_state.total_threats > 0 else 0:.1f}%")
            with col4:
                st.metric("Frames Processed | الإطارات", st.session_state.total_frames_processed)
            
            st.markdown("---")
            
            # جدول تفصيلي
            if st.checkbox("📊 Show Detailed Operations Table | عرض الجدول التفصيلي"):
                attacks_data = []
                for a in st.session_state.cyber_attacks:
                    attacks_data.append({
                        'Operation ID': a['attack_id'],
                        'Target Drone': a['drone_id'],
                        'Attack Type': a['attack_type'],
                        'Threat Level': a['threat_level'],
                        'Confidence': f"{a['confidence']:.1%}",
                        'Duration (s)': f"{a['duration']:.2f}",
                        'Time': a['timestamp'].strftime('%H:%M:%S'),
                        'Status': '✅ ' + a['status']
                    })
                
                attacks_df = pd.DataFrame(attacks_data)
                st.dataframe(
                    attacks_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # تصدير البيانات
                col1, col2 = st.columns(2)
                with col1:
                    csv = attacks_df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        "📥 Download as CSV",
                        csv,
                        "defense_report.csv",
                        "text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    json_data = json.dumps(attacks_data, ensure_ascii=False, indent=2).encode('utf-8')
                    st.download_button(
                        "📥 Download as JSON",
                        json_data,
                        "defense_report.json",
                        "application/json",
                        use_container_width=True
                    )
        
        # تبويب الرسوم البيانية
        with tabs[3]:
            st.markdown("### 📉 Advanced Visualizations | الرسوم البيانية المتقدمة")
            
            # Timeline
            fig = go.Figure()
            
            for attack in st.session_state.cyber_attacks:
                fig.add_trace(go.Scatter(
                    x=[attack['timestamp']],
                    y=[attack['duration']],
                    mode='markers',
                    marker=dict(
                        size=15,
                        color=attack['confidence'],
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title="Confidence")
                    ),
                    text=f"{attack['attack_id']}<br>{attack['drone_id']}",
                    hovertemplate="<b>%{text}</b><br>Time: %{x}<br>Duration: %{y:.2f}s<extra></extra>"
                ))
            
            fig.update_layout(
                title="Counter-Operations Timeline | Timeline العمليات",
                xaxis_title="Time | الوقت",
                yaxis_title="Duration (seconds) | المدة",
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', family='Cairo, Inter')
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No analytics data yet. Start by analyzing a video or activating live camera. | لا توجد بيانات تحليلية بعد")

def display_footer():
    """عرض معلومات ختامية احترافية"""
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h3>🎯 About the System | عن المنظومة</h3>
            
            <p><strong>Advanced Air Defense System</strong> is an integrated and advanced solution for protecting airport and critical facility airspace against unauthorized aerial threats.</p>
            
            <p><strong>Key Features | المزايا الرئيسية:</strong></p>
            <ul style="text-align: right; direction: rtl;">
                <li>🔍 Intelligent real-time detection using YOLOv11</li>
                <li>⚡ Multi-level electronic countermeasures</li>
                <li>📊 Detailed real-time analytics and statistics</li>
                <li>🤖 Full automation of defensive operations</li>
                <li>📋 Comprehensive event logging</li>
                <li>🎨 Advanced professional bilingual interface</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box">
            <h3>⚠️ Important Notices | تنبيهات وإرشادات</h3>
            
            <p><strong>Important Information | معلومات مهمة:</strong></p>
            <ul style="text-align: right; direction: rtl;">
                <li>🔒 <strong>Educational Simulation:</strong> All electronic operations are simulated and not executed in reality</li>
                <li>⚖️ <strong>Legal Use:</strong> For authorized security and military entities only</li>
                <li>🎓 <strong>Educational Purpose:</strong> For understanding and developing air defense systems</li>
                <li>🛡️ <strong>Safety First:</strong> Full compliance with local laws and regulations</li>
                <li>📚 <strong>Research & Development:</strong> For scientific research and development purposes</li>
            </ul>
            
            <p style="margin-top: 20px; padding: 20px; background: rgba(255,255,255,0.12); border-radius: 12px; border-right: 5px solid #4f46e5;">
                <strong>Development | تطوير:</strong> Mazen 🇸🇦<br>
                <strong>Version | النسخة:</strong> 3.0 Professional<br>
                <strong>Technology | التقنية:</strong> YOLOv11 + Streamlit + OpenCV<br>
                <strong>Date | التاريخ:</strong> December 2025
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer نهائي
    st.markdown("""
    <div class="custom-footer">
        <h3>🛡️ Advanced AI-Powered Airport Defense System</h3>
        <h4>منظومة الدفاع الجوي الذكية المتقدمة</h4>
        <p style="font-size: 1.15rem; margin: 20px 0; line-height: 1.6;">
            Integrated system for detection, tracking and countermeasures against unmanned aerial vehicles<br>
            منظومة متكاملة للكشف والتتبع والإجراءات المضادة ضد الطائرات المسيرة
        </p>
        <p style="opacity: 0.85; margin-top: 25px; font-size: 1rem;">
            ⚠️ This system is purely an educational simulation and does not perform any actual jamming or electronic attacks<br>
            هذا النظام محاكاة تعليمية بحتة ولا يقوم بأي عمليات تشويش أو هجمات إلكترونية فعلية
        </p>
        <p style="opacity: 0.9; margin-top: 20px;">
            All Rights Reserved © 2025 | جميع الحقوق محفوظة<br>
            Developed by Mazen | تطوير: مازن
        </p>
        <p style="margin-top: 20px;">
            <span class="badge badge-info">Powered by AI</span>
            <span class="badge badge-success">Made in Saudi Arabia 🇸🇦</span>
            <span class="badge badge-warning">Educational Purpose</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

# تشغيل التطبيق
if __name__ == "__main__":
    main()
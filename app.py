from flask import Flask, jsonify, render_template
from flask_cors import CORS
import random
from predictive_engine import FreightPredictor, generate_synthetic_data

app = Flask(__name__)
CORS(app)

# --- INITIALIZE AI BRAIN ---
print("Booting JEL Core Systems...")
ai_brain = FreightPredictor()
ai_brain.train(generate_synthetic_data())
print("AI Systems Online.")

# --- INITIALIZE FLEET STATE ---
# Status types: 'active' (loaded), 'empty' (returning), 'warning' (maintenance), 'alert' (critical)
fleet = [
    {"id": "JH-01-AB-1001", "status": "active", "lat": 30, "lng": 30, "fuel": 78, "speed": 65, "temp": 88, "oil": 45, "vib": 0.2, "revenue": 45000, "alert_msg": None},
    {"id": "JH-01-XX-5555", "status": "empty", "lat": 60, "lng": 80, "fuel": 45, "speed": 55, "temp": 85, "oil": 42, "vib": 0.3, "revenue": 0, "alert_msg": None},
    {"id": "JH-01-XY-9876", "status": "warning", "lat": 45, "lng": 55, "fuel": 60, "speed": 40, "temp": 92, "oil": 38, "vib": 0.85, "revenue": 32000, "alert_msg": "Pred: Axle Failure (500km)"},
    {"id": "JH-05-ZZ-2233", "status": "active", "lat": 20, "lng": 60, "fuel": 90, "speed": 70, "temp": 82, "oil": 48, "vib": 0.1, "revenue": 51000, "alert_msg": None},
    {"id": "JH-09-QQ-1122", "status": "alert", "lat": 70, "lng": 20, "fuel": 15, "speed": 0, "temp": 90, "oil": 40, "vib": 0.1, "revenue": 12000, "alert_msg": "THEFT: -20L Detected"}
]

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/api/fleet-data')
def get_fleet_data():
    global fleet
    
    # 1. Calculate Aggregate KPIs for Top Ribbon
    total_trucks = len(fleet)
    active_trucks = len([t for t in fleet if t['status'] == 'active'])
    empty_trucks = len([t for t in fleet if t['status'] == 'empty'])
    total_revenue = sum([t['revenue'] for t in fleet])
    alert_count = len([t for t in fleet if t['status'] in ['alert', 'warning']])
    
    utilization = int((active_trucks / total_trucks) * 100) if total_trucks > 0 else 0
    empty_rate = int((empty_trucks / total_trucks) * 100) if total_trucks > 0 else 0

    # 2. Simulate Real-Time Movement & Sensors
    for t in fleet:
        # Reset active trucks to normal state unless an anomaly occurs
        if t['status'] == 'active': 
            t['alert_msg'] = None
        
        if t['status'] not in ['alert']: # Alerts usually mean stopped
             # Movement
            t['lng'] = (t['lng'] + random.uniform(-0.3, 0.8)) % 98
            t['lat'] = (t['lat'] + random.uniform(-0.3, 0.3)) % 95
            t['fuel'] = max(0, t['fuel'] - 0.03)
            t['speed'] = random.randint(40, 80)
            
            # Telematics Fluctuations
            t['temp'] = random.randint(80, 98)
            t['oil'] = random.randint(40, 55)
            t['vib'] = random.uniform(0.1, 0.45)

            # --- INJECT SIMULATED ANOMALIES ---
            rand = random.random()
            # Module C: Maintenance Anomaly (1% chance)
            if rand < 0.01 and t['status'] == 'active':
                 t['status'] = 'warning'
                 t['vib'] = 0.92
                 t['alert_msg'] = "Pred: High Vibration Risk"
            # Module B: Theft Anomaly (0.5% chance)
            elif rand > 0.995 and t['status'] == 'active':
                 t['status'] = 'alert'
                 t['fuel'] -= 10
                 t['speed'] = 0
                 t['alert_msg'] = "THEFT: Sudden Fuel Drop"

    # 3. Get AI Prediction (Module A)
    # Simulating a truck currently in Kolkata needing a return load
    ai_prediction = ai_brain.predict_opportunity(10, "Open Body", 1, 18500, 98)

    # Combine all data into one response payload
    response = {
        "kpis": {
            "utilization": utilization,
            "empty_rate": empty_rate,
            "revenue": f"₹{total_revenue/1000:.1f}K",
            "alerts": alert_count
        },
        "fleet": fleet,
        "ai_freight": ai_prediction
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
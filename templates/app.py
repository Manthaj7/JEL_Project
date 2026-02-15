from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

# --- INITIAL DATA (The starting point) ---
trucks = [
    {"id": "TRUCK-01", "x": 10, "y": 20, "fuel": 90, "status": "active"},
    {"id": "TRUCK-02", "x": 30, "y": 40, "fuel": 85, "status": "empty"},
    {"id": "TRUCK-03", "x": 60, "y": 60, "fuel": 40, "status": "alert"},
    {"id": "TRUCK-04", "x": 80, "y": 80, "fuel": 72, "status": "active"}
]

# --- 1. THE HOMEPAGE ---
# When you open the browser, show the HTML file
@app.route('/')
def home():
    return render_template('dashboard.html')

# --- 2. THE DATA GENERATOR ---
# This runs in the background to simulate movement
@app.route('/get_data')
def get_data():
    global trucks
    for t in trucks:
        if t["status"] != "alert": # Broken trucks don't move!
            # Move randomly
            t["x"] += random.uniform(-1, 2)
            t["y"] += random.uniform(-0.5, 0.5)
            
            # Burn fuel
            t["fuel"] -= 0.1
            
            # Keep inside the screen (0-100%)
            t["x"] = max(0, min(100, t["x"]))
            t["y"] = max(0, min(100, t["y"]))
            
            # Refuel if empty
            if t["fuel"] <= 0:
                t["fuel"] = 100

    return jsonify(trucks)

if __name__ == '__main__':
    print("Dashboard is starting...")
    print("Go to http://127.0.0.1:5000 in your browser")
    app.run(debug=True)
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

def generate_synthetic_data(num_records=1000):
    np.random.seed(42)
    data = {
        'month': np.random.randint(1, 13, num_records),
        'truck_type': np.random.choice(['Open Body', 'Container', 'Trailer'], num_records),
        'is_festival': np.random.choice([0, 1], num_records, p=[0.8, 0.2]),
        'competitor_rate': np.random.uniform(15000, 22000, num_records),
        'fuel_price': np.random.uniform(90, 105, num_records)
    }
    df = pd.DataFrame(data)
    
    # Logic: High demand during festivals (Oct-Nov)
    def get_prob(row):
        prob = 0.4
        if row['is_festival'] == 1: prob += 0.3
        if row['month'] in [10, 11, 12]: prob += 0.2
        return min(prob, 0.95)

    df['load_found'] = df.apply(lambda row: np.random.choice([0, 1], p=[1-get_prob(row), get_prob(row)]), axis=1)
    df['winning_price'] = df['competitor_rate'] * np.random.uniform(0.9, 1.1)
    df.loc[df['load_found'] == 0, 'winning_price'] = 0
    return df

class FreightPredictor:
    def __init__(self):
        self.clf = RandomForestClassifier(n_estimators=100, random_state=42)
        self.reg = RandomForestRegressor(n_estimators=100, random_state=42)
        self.enc = LabelEncoder()

    def train(self, df):
        df['truck_enc'] = self.enc.fit_transform(df['truck_type'])
        features = ['month', 'is_festival', 'truck_enc', 'competitor_rate', 'fuel_price']
        
        self.clf.fit(df[features], df['load_found'])
        
        df_success = df[df['load_found'] == 1]
        self.reg.fit(df_success[features], df_success['winning_price'])

    def predict_opportunity(self, month, truck_type, is_festival, market_rate, fuel_price):
        truck_code = self.enc.transform([truck_type])[0]
        inputs = [[month, is_festival, truck_code, market_rate, fuel_price]]
        
        prob = self.clf.predict_proba(inputs)[0][1] * 100
        price = self.reg.predict(inputs)[0]
        
        advice = "Low Demand! Offer Discount."
        if prob > 80: advice = "High Demand! Quote High."
        elif prob > 50: advice = "Moderate Demand."
        
        return {
            "Backhaul Probability": f"{prob:.1f}%",
            "AI Recommended Offer": f"₹{price:,.0f}",
            "Strategy": advice
        }
import logging
from typing import Dict, Any, List

logger = logging.getLogger("agrivision.decision_engine")

class SmartDecisionEngine:
    """
    Multi-sensor fusion decision engine combining AI plant health diagnostics,
    soil moisture, temperature, humidity, rain forecast, pH, and flow rate.
    """
    
    @staticmethod
    def evaluate(
        soil_moisture: float,
        temperature: float,
        humidity: float,
        rain: bool,
        ph: float,
        water_flow: float,
        rain_prob_pct: float,
        plant_health_score: float = 90.0,
        latest_disease: str = "Healthy",
        target_moisture_min: float = 35.0,
        target_moisture_max: float = 70.0
    ) -> Dict[str, Any]:
        """
        Executes multi-factor agronomic rules to determine whether irrigation should occur.
        """
        reasons_pro: List[str] = []
        reasons_con: List[str] = []
        
        confidence = 90.0
        recommendation_status = "HOLD"
        recommended_action = "Maintain current field monitoring."
        target_pump = "PUMP_1"
        duration_seconds = 0
        
        # Rule 1: Rain Detection
        if rain:
            reasons_con.append("Rain sensor actively detecting precipitation in the field.")
            confidence += 5.0
            
        if rain_prob_pct >= 60.0:
            reasons_con.append(f"High rain probability expected ({rain_prob_pct}%). Conserving water.")
            confidence += 3.0
            
        # Rule 2: Soil Moisture Check
        if soil_moisture < target_moisture_min:
            reasons_pro.append(f"Soil moisture ({soil_moisture}%) is below minimum threshold ({target_moisture_min}%).")
        elif soil_moisture > target_moisture_max:
            reasons_con.append(f"Soil moisture ({soil_moisture}%) is above maximum target ({target_moisture_max}%). Root saturation risk.")
        else:
            reasons_con.append(f"Soil moisture ({soil_moisture}%) is within optimal range ({target_moisture_min}% - {target_moisture_max}%).")
            
        # Rule 3: Temperature & Evapotranspiration
        if temperature > 34.0:
            reasons_pro.append(f"High ambient temperature ({temperature}°C) increases evapotranspiration loss.")
            
        # Rule 4: Plant Vision Fusion
        if latest_disease in ["Early Blight", "Late Blight", "Bacterial Spot"]:
            if soil_moisture >= target_moisture_min:
                reasons_con.append(f"AI Vision detected '{latest_disease}'. Leaf wetness must be minimized. Irrigation withheld despite slight moisture droop.")
                confidence += 4.0
            else:
                reasons_pro.append(f"Plant under disease stress ({latest_disease}). Targeted subsurface drip irrigation required to prevent moisture collapse without wetting canopy.")
                target_pump = "PUMP_1" # Use drip line only
                
        # Rule 5: pH Anomaly
        if ph < 5.8 or ph > 7.8:
            reasons_con.append(f"Abnormal soil pH detected ({ph}). Nutrient lockout risk; consult soil amendment guidelines.")
            
        # Final Decision Matrix Synthesis
        if soil_moisture < target_moisture_min and not rain and rain_prob_pct < 60.0:
            if latest_disease in ["Early Blight", "Late Blight"] and soil_moisture > target_moisture_min - 5.0:
                recommendation_status = "IRRIGATION SUPPRESSED"
                recommended_action = "Fungal disease present with adequate soil moisture. Irrigation suppressed to prevent fungal sporulation."
                duration_seconds = 0
            else:
                recommendation_status = "IRRIGATION RECOMMENDED"
                duration_seconds = 60 if soil_moisture > target_moisture_min - 10 else 120
                recommended_action = f"Activate {target_pump} for {duration_seconds} seconds (Subsurface Drip)."
        else:
            recommendation_status = "IRRIGATION NOT RECOMMENDED"
            duration_seconds = 0
            recommended_action = "No irrigation required at this time."
            
        # Bound confidence between 50% and 99%
        confidence_final = round(min(99.0, max(50.0, confidence)), 1)
        
        return {
            "decision": recommendation_status,
            "confidence_pct": confidence_final,
            "action": recommended_action,
            "target_pump": target_pump if recommendation_status == "IRRIGATION RECOMMENDED" else None,
            "duration_seconds": duration_seconds,
            "reasons_pro": reasons_pro,
            "reasons_con": reasons_con,
            "input_summary": {
                "soil_moisture": soil_moisture,
                "temperature": temperature,
                "humidity": humidity,
                "rain": rain,
                "ph": ph,
                "rain_prob_pct": rain_prob_pct,
                "plant_health_score": plant_health_score,
                "latest_disease": latest_disease
            }
        }

from typing import Dict, Any

INTENT_RULES = {
  "ROUTE_SAFETY": ["safe", "safety", "risk", "dangerous", "hazard", "sail", "sailing", "voyage", "travel", "navigate", "safe to", "is it safe"],
  "ROUTE_OPTIMIZE": ["route", "find", "optimize", "path", "navigate", "go to", "get to", "reach", "go from", "route to"],
  "ROUTE_COMPARE": ["compare", "trade-off", "alternative", "options", "which is better", "which one", "difference"],
  "ICEBERG_TRACK": ["iceberg", "drift", "trajectory", "where will", "where is", "drifting"],
  "SIC_FORECAST": ["sea-ice", "sic", "ice concentration", "ice forecast", "ice cover", "ice", "frozen"],
  "EXPLAIN_ROUTE": ["why", "explain", "reason", "justify", "how did you", "what made you", "reason for"],
}

def classify_intent(query: str) -> Dict[str, Any]:
    lower_query = query.lower()
    best_intent = "ROUTE_OPTIMIZE"
    best_score = 0
    
    for intent, keywords in INTENT_RULES.items():
        score = sum(1 for kw in keywords if kw in lower_query)
        if score > best_score or (score == best_score and intent == "EXPLAIN_ROUTE"):
            best_score = score
            best_intent = intent
            
    if best_score > 0:
        confidence = 0.85 + (0.15 * min(best_score, 3) / 3)
    else:
        confidence = 0.3
        
    confidence = min(confidence, 0.99)
        
    return {
        "intent": best_intent,
        "confidence": float(confidence),
        "matched_rule": best_intent if best_score > 0 else "DEFAULT"
    }

def extract_slots(query: str) -> Dict[str, Any]:
    lower_query = query.lower()
    slots = {}
    
    if "bharati" in lower_query:
        slots["origin_lat"] = -69.4
        slots["origin_lon"] = 76.2
    if "maitri" in lower_query:
        slots["dest_lat"] = -70.7
        slots["dest_lon"] = 11.7
        
    # Default to Bharati -> Maitri if not specified
    if "origin_lat" not in slots:
        slots["origin_lat"] = -69.4
        slots["origin_lon"] = 76.2
    if "dest_lat" not in slots:
        slots["dest_lat"] = -70.7
        slots["dest_lon"] = 11.7
        
    return slots

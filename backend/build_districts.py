"""
Generates app/data/india_districts.json.

This produces a curated list of real Indian districts/cities with genuine
lat/lon centroids and a climate/pollution zone tag used by the synthetic
model. It is intentionally hand-verified rather than machine-extracted from
GADM, so every coordinate is real and every zone assignment is sensible.

Run:  python build_districts.py
"""
import json
import re
from pathlib import Path

# (name, state, lat, lon, zone)
# zones: igp, coastal, peninsular, arid, gangetic-delta, northeast, central, himalayan
RAW = [
    # --- Delhi-NCR / IGP core (worst air) ---
    ("New Delhi", "Delhi", 28.6139, 77.2090, "igp"),
    ("Anand Vihar", "Delhi", 28.6469, 77.3160, "igp"),
    ("ITO", "Delhi", 28.6289, 77.2410, "igp"),
    ("Punjabi Bagh", "Delhi", 28.6740, 77.1310, "igp"),
    ("Rohini", "Delhi", 28.7439, 77.0728, "igp"),
    ("Dwarka", "Delhi", 28.5921, 77.0460, "igp"),
    ("Gurugram", "Haryana", 28.4595, 77.0266, "igp"),
    ("Faridabad", "Haryana", 28.4089, 77.3178, "igp"),
    ("Ghaziabad Vasundhara", "Uttar Pradesh", 28.6600, 77.3730, "igp"),
    ("Noida", "Uttar Pradesh", 28.5355, 77.3910, "igp"),
    ("Greater Noida", "Uttar Pradesh", 28.4744, 77.5040, "igp"),
    ("Meerut", "Uttar Pradesh", 28.9845, 77.7064, "igp"),
    ("Sonipat", "Haryana", 28.9931, 77.0151, "igp"),
    ("Panipat", "Haryana", 29.3909, 76.9635, "igp"),
    ("Rohtak", "Haryana", 28.8955, 76.6066, "igp"),
    ("Karnal", "Haryana", 29.6857, 76.9905, "igp"),
    ("Hisar", "Haryana", 29.1492, 75.7217, "arid"),
    ("Ambala", "Haryana", 30.3752, 76.7821, "igp"),
    # --- Punjab (IGP, stubble-burning belt) ---
    ("Ludhiana", "Punjab", 30.9010, 75.8573, "igp"),
    ("Amritsar", "Punjab", 31.6340, 74.8723, "igp"),
    ("Jalandhar", "Punjab", 31.3260, 75.5762, "igp"),
    ("Patiala", "Punjab", 30.3398, 76.3869, "igp"),
    ("Bathinda", "Punjab", 30.2110, 74.9455, "arid"),
    ("Mohali", "Punjab", 30.7046, 76.7179, "igp"),
    ("Chandigarh", "Chandigarh", 30.7333, 76.7794, "igp"),
    # --- Uttar Pradesh (IGP) ---
    ("Lucknow Talkatora", "Uttar Pradesh", 26.8467, 80.9462, "igp"),
    ("Kanpur Nehru Nagar", "Uttar Pradesh", 26.4499, 80.3319, "igp"),
    ("Agra", "Uttar Pradesh", 27.1767, 78.0081, "igp"),
    ("Varanasi", "Uttar Pradesh", 25.3176, 82.9739, "igp"),
    ("Prayagraj", "Uttar Pradesh", 25.4358, 81.8463, "igp"),
    ("Bareilly", "Uttar Pradesh", 28.3670, 79.4304, "igp"),
    ("Moradabad", "Uttar Pradesh", 28.8386, 78.7733, "igp"),
    ("Aligarh", "Uttar Pradesh", 27.8974, 78.0880, "igp"),
    ("Gorakhpur", "Uttar Pradesh", 26.7606, 83.3732, "igp"),
    ("Jhansi", "Uttar Pradesh", 25.4484, 78.5685, "central"),
    ("Mathura", "Uttar Pradesh", 27.4924, 77.6737, "igp"),
    ("Firozabad", "Uttar Pradesh", 27.1591, 78.3958, "igp"),
    # --- Bihar / Jharkhand (IGP + eastern) ---
    ("Patna", "Bihar", 25.5941, 85.1376, "igp"),
    ("Gaya", "Bihar", 24.7955, 84.9994, "igp"),
    ("Muzaffarpur", "Bihar", 26.1209, 85.3647, "igp"),
    ("Bhagalpur", "Bihar", 25.2445, 86.9718, "igp"),
    ("Ranchi", "Jharkhand", 23.3441, 85.3096, "central"),
    ("Jamshedpur", "Jharkhand", 22.8046, 86.2029, "central"),
    ("Dhanbad", "Jharkhand", 23.7957, 86.4304, "central"),
    # --- West Bengal (gangetic delta) ---
    ("Kolkata", "West Bengal", 22.5726, 88.3639, "gangetic-delta"),
    ("Howrah Ghusuri", "West Bengal", 22.6000, 88.3300, "gangetic-delta"),
    ("Durgapur", "West Bengal", 23.5204, 87.3119, "gangetic-delta"),
    ("Asansol", "West Bengal", 23.6739, 86.9524, "central"),
    ("Siliguri", "West Bengal", 26.7271, 88.3953, "northeast"),
    # --- Maharashtra (coastal + peninsular) ---
    ("Mumbai", "Maharashtra", 19.0760, 72.8777, "coastal"),
    ("Navi Mumbai", "Maharashtra", 19.0330, 73.0297, "coastal"),
    ("Thane", "Maharashtra", 19.2183, 72.9781, "coastal"),
    ("Pune", "Maharashtra", 18.5204, 73.8567, "peninsular"),
    ("Nagpur", "Maharashtra", 21.1458, 79.0882, "central"),
    ("Nashik", "Maharashtra", 19.9975, 73.7898, "peninsular"),
    ("Aurangabad", "Maharashtra", 19.8762, 75.3433, "peninsular"),
    ("Solapur", "Maharashtra", 17.6599, 75.9064, "peninsular"),
    ("Kolhapur", "Maharashtra", 16.7050, 74.2433, "peninsular"),
    # --- Gujarat (arid + coastal) ---
    ("Ahmedabad Airport", "Gujarat", 23.0772, 72.6347, "arid"),
    ("Surat", "Gujarat", 21.1702, 72.8311, "coastal"),
    ("Vadodara", "Gujarat", 22.3072, 73.1812, "arid"),
    ("Rajkot", "Gujarat", 22.3039, 70.8022, "arid"),
    ("Bhavnagar", "Gujarat", 21.7645, 72.1519, "coastal"),
    ("Jamnagar", "Gujarat", 22.4707, 70.0577, "coastal"),
    ("Gandhinagar", "Gujarat", 23.2156, 72.6369, "arid"),
    # --- Rajasthan (arid) ---
    ("Jaipur", "Rajasthan", 26.9124, 75.7873, "arid"),
    ("Jodhpur", "Rajasthan", 26.2389, 73.0243, "arid"),
    ("Udaipur", "Rajasthan", 24.5854, 73.7125, "arid"),
    ("Kota", "Rajasthan", 25.2138, 75.8648, "arid"),
    ("Bikaner", "Rajasthan", 28.0229, 73.3119, "arid"),
    ("Ajmer", "Rajasthan", 26.4499, 74.6399, "arid"),
    ("Alwar", "Rajasthan", 27.5530, 76.6346, "arid"),
    # --- Madhya Pradesh (central) ---
    ("Bhopal", "Madhya Pradesh", 23.2599, 77.4126, "central"),
    ("Indore", "Madhya Pradesh", 22.7196, 75.8577, "central"),
    ("Gwalior", "Madhya Pradesh", 26.2183, 78.1828, "central"),
    ("Jabalpur", "Madhya Pradesh", 23.1815, 79.9864, "central"),
    ("Ujjain", "Madhya Pradesh", 23.1793, 75.7849, "central"),
    ("Sagar", "Madhya Pradesh", 23.8388, 78.7378, "central"),
    # --- Chhattisgarh (central) ---
    ("Raipur", "Chhattisgarh", 21.2514, 81.6296, "central"),
    ("Bhilai", "Chhattisgarh", 21.1938, 81.3509, "central"),
    ("Bilaspur", "Chhattisgarh", 22.0797, 82.1409, "central"),
    ("Korba", "Chhattisgarh", 22.3595, 82.7501, "central"),
    # --- Karnataka (peninsular + coastal) ---
    ("Bengaluru", "Karnataka", 12.9716, 77.5946, "peninsular"),
    ("Mysuru", "Karnataka", 12.2958, 76.6394, "peninsular"),
    ("Hubli-Dharwad", "Karnataka", 15.3647, 75.1240, "peninsular"),
    ("Mangaluru", "Karnataka", 12.9141, 74.8560, "coastal"),
    ("Belagavi", "Karnataka", 15.8497, 74.4977, "peninsular"),
    ("Kalaburagi", "Karnataka", 17.3297, 76.8343, "peninsular"),
    ("Ballari", "Karnataka", 15.1394, 76.9214, "peninsular"),
    # --- Telangana / Andhra (peninsular + coastal) ---
    ("Hyderabad", "Telangana", 17.3850, 78.4867, "peninsular"),
    ("Warangal", "Telangana", 17.9689, 79.5941, "peninsular"),
    ("Nizamabad", "Telangana", 18.6725, 78.0940, "peninsular"),
    ("Visakhapatnam", "Andhra Pradesh", 17.6868, 83.2185, "coastal"),
    ("Vijayawada", "Andhra Pradesh", 16.5062, 80.6480, "coastal"),
    ("Guntur", "Andhra Pradesh", 16.3067, 80.4365, "coastal"),
    ("Tirupati", "Andhra Pradesh", 13.6288, 79.4192, "peninsular"),
    ("Nellore", "Andhra Pradesh", 14.4426, 79.9865, "coastal"),
    ("Kurnool", "Andhra Pradesh", 15.8281, 78.0373, "peninsular"),
    # --- Tamil Nadu (coastal + peninsular) ---
    ("Chennai", "Tamil Nadu", 13.0827, 80.2707, "coastal"),
    ("Coimbatore", "Tamil Nadu", 11.0168, 76.9558, "peninsular"),
    ("Madurai", "Tamil Nadu", 9.9252, 78.1198, "peninsular"),
    ("Tiruchirappalli", "Tamil Nadu", 10.7905, 78.7047, "peninsular"),
    ("Salem", "Tamil Nadu", 11.6643, 78.1460, "peninsular"),
    ("Tirunelveli", "Tamil Nadu", 8.7139, 77.7567, "peninsular"),
    ("Tuticorin", "Tamil Nadu", 8.7642, 78.1348, "coastal"),
    ("Vellore", "Tamil Nadu", 12.9165, 79.1325, "peninsular"),
    # --- Kerala (coastal) ---
    ("Thiruvananthapuram", "Kerala", 8.5241, 76.9366, "coastal"),
    ("Kochi", "Kerala", 9.9312, 76.2673, "coastal"),
    ("Kozhikode", "Kerala", 11.2588, 75.7804, "coastal"),
    ("Thrissur", "Kerala", 10.5276, 76.2144, "coastal"),
    ("Kollam", "Kerala", 8.8932, 76.6141, "coastal"),
    ("Kannur", "Kerala", 11.8745, 75.3704, "coastal"),
    # --- Odisha (coastal + peninsular) ---
    ("Bhubaneswar", "Odisha", 20.2961, 85.8245, "peninsular"),
    ("Cuttack", "Odisha", 20.4625, 85.8830, "peninsular"),
    ("Rourkela", "Odisha", 22.2604, 84.8536, "central"),
    ("Puri", "Odisha", 19.8135, 85.8312, "coastal"),
    ("Berhampur", "Odisha", 19.3149, 84.7941, "coastal"),
    # --- Northeast ---
    ("Guwahati", "Assam", 26.1445, 91.7362, "northeast"),
    ("Dibrugarh", "Assam", 27.4728, 94.9120, "northeast"),
    ("Silchar", "Assam", 24.8333, 92.7789, "northeast"),
    ("Agartala", "Tripura", 23.8315, 91.2868, "northeast"),
    ("Shillong", "Meghalaya", 25.5788, 91.8933, "northeast"),
    ("Imphal", "Manipur", 24.8170, 93.9368, "northeast"),
    ("Aizawl", "Mizoram", 23.7271, 92.7176, "northeast"),
    ("Kohima", "Nagaland", 25.6751, 94.1086, "northeast"),
    ("Itanagar", "Arunachal Pradesh", 27.0844, 93.6053, "northeast"),
    ("Gangtok", "Sikkim", 27.3389, 88.6065, "himalayan"),
    # --- Himalayan belt ---
    ("Srinagar", "Jammu and Kashmir", 34.0837, 74.7973, "himalayan"),
    ("Jammu", "Jammu and Kashmir", 32.7266, 74.8570, "himalayan"),
    ("Shimla", "Himachal Pradesh", 31.1048, 77.1734, "himalayan"),
    ("Dharamshala", "Himachal Pradesh", 32.2190, 76.3234, "himalayan"),
    ("Solan", "Himachal Pradesh", 30.9045, 77.0967, "himalayan"),
    ("Dehradun", "Uttarakhand", 30.3165, 78.0322, "himalayan"),
    ("Haridwar", "Uttarakhand", 29.9457, 78.1642, "igp"),
    ("Nainital", "Uttarakhand", 29.3803, 79.4636, "himalayan"),
    ("Haldwani", "Uttarakhand", 29.2183, 79.5130, "igp"),
    ("Leh", "Ladakh", 34.1526, 77.5771, "himalayan"),
    # --- Goa (coastal) ---
    ("Panaji", "Goa", 15.4909, 73.8278, "coastal"),
    ("Margao", "Goa", 15.2832, 73.9862, "coastal"),
    # --- Union territories / islands ---
    ("Port Blair", "Andaman and Nicobar", 11.6234, 92.7265, "coastal"),
    ("Puducherry", "Puducherry", 11.9416, 79.8083, "coastal"),
]


def slugify(name, state):
    base = f"{name}-{state}".lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base


def build():
    seen = set()
    stations = []
    for name, state, lat, lon, zone in RAW:
        sid = slugify(name, state)
        if sid in seen:
            continue
        seen.add(sid)
        stations.append({
            "id": sid,
            "name": name,
            "state": state,
            "area": state,
            "lat": lat,
            "lon": lon,
            "zone": zone,
        })
    out = Path(__file__).resolve().parent / "app" / "data" / "india_districts.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(stations, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(stations)} districts to {out}")


if __name__ == "__main__":
    build()

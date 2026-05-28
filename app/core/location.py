from typing import List, Tuple

# Central coordinate anchors matching the active localized dataset tags in Lagos
LAGOS_SECTORS = {
    "Yaba": (6.5165, 3.3712),
    "Lekki Phase 1": (6.4474, 3.4716),
    "Ikeja": (6.5913, 3.3411)
}

def identify_closest_lagos_sector(user_lat: float, user_lon: float) -> Tuple[str, List[float]]:
    """
    Normalizes a user's raw GPS latitude/longitude coordinates by mapping them 
    to the closest operational business sector (Yaba, Lekki, or Ikeja).
    
    Uses standard Euclidean distance formula for ultra-fast, zero-dependency processing.
    """
    # Fallback to Ikeja if coordinates are missing, unreadable, or defaulted to 0
    if user_lat == 0.0 or user_lon == 0.0:
        return "Ikeja", list(LAGOS_SECTORS["Ikeja"])

    closest_sector = "Ikeja"
    min_distance = float('inf')

    # Distance matching calculation block
    for sector_name, sector_coords in LAGOS_SECTORS.items():
        # d = √((x2 - x1)² + (y2 - y1)²)
        distance = ((user_lat - sector_coords[0]) ** 2 + (user_lon - sector_coords[1]) ** 2) ** 0.5
        
        if distance < min_distance:
            min_distance = distance
            closest_sector = sector_name
            
    return closest_sector, list(LAGOS_SECTORS[closest_sector])
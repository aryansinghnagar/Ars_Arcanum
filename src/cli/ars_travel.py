#!/usr/bin/env python3
"""
/usr/local/bin/ars-travel — Ars Arcanum Travel & Transit Time Calculator
Calculates medieval & speculative transit durations across custom geography to prevent narrative teleportation.
"""

import sys
import argparse
from typing import Dict, Any

VELOCITIES: Dict[str, Dict[str, Any]] = {
    "infantry": {"name": "Infantry Regular March", "speed_mpd": 20.0, "type": "land"},
    "forced_march": {"name": "Infantry Forced March", "speed_mpd": 30.0, "type": "land"},
    "cavalry": {"name": "Cavalry / Mounted Party", "speed_mpd": 35.0, "type": "land"},
    "courier": {"name": "Mounted Courier (Relay)", "speed_mpd": 60.0, "type": "land"},
    "cart": {"name": "Heavy Wagon / Supply Train", "speed_mpd": 14.0, "type": "land"},
    "galley": {"name": "Sailing Galley / Warship", "speed_mpd": 75.0, "type": "water"},
    "barge": {"name": "River Barge / Keelboat", "speed_mpd": 25.0, "type": "water"},
    "dragon": {"name": "Dragonback / Beast of Burden", "speed_mpd": 220.0, "type": "aerial"},
    "airship": {"name": "Magical Skyship / Zephyr", "speed_mpd": 140.0, "type": "aerial"},
}

TERRAIN_FRICTION: Dict[str, float] = {
    "plains": 1.0,
    "road": 0.8,
    "hills": 1.25,
    "forest": 1.6,
    "mountains": 2.4,
    "swamp": 2.2,
    "desert": 1.8,
    "ocean": 1.0,
    "straits": 1.5,
}

WEATHER_MODIFIERS: Dict[str, float] = {
    "clear": 1.0,
    "rain": 1.3,
    "storm": 2.0,
    "blizzard": 2.8,
    "magical_surge": 3.0,
}


def calculate_transit(
    distance_miles: float,
    mode: str = "infantry",
    terrain: str = "plains",
    weather: str = "clear",
    party_size: int = 4,
) -> Dict[str, Any]:
    v_data = VELOCITIES.get(mode, VELOCITIES["infantry"])
    base_speed = v_data["speed_mpd"]
    t_friction = TERRAIN_FRICTION.get(terrain, 1.0)
    w_friction = WEATHER_MODIFIERS.get(weather, 1.0)

    # Calculate effective speed
    effective_speed = base_speed / (t_friction * w_friction)
    days_required = distance_miles / effective_speed
    hours_traveling = days_required * 8.0  # standard 8-hour marching day

    # Calculate supplies
    rations_per_person_day = 1.5  # lbs
    total_rations = days_required * party_size * rations_per_person_day

    return {
        "distance": distance_miles,
        "mode_name": v_data["name"],
        "terrain": terrain,
        "weather": weather,
        "party_size": party_size,
        "effective_speed_mpd": round(effective_speed, 1),
        "days": round(days_required, 2),
        "hours": round(hours_traveling, 1),
        "camp_stops": max(0, int(days_required)),
        "rations_lbs": round(total_rations, 1),
    }


def print_travel_report(res: Dict[str, Any]) -> None:
    print(f"\n=======================================================")
    print(f"       ARS ARCANUM TRAVEL & TRANSIT DISPATCH           ")
    print(f"=======================================================")
    print(f"  Distance:        {res['distance']} miles ({res['distance'] * 1.609:.1f} km)")
    print(f"  Transit Mode:    {res['mode_name']}")
    print(f"  Terrain:         {res['terrain'].capitalize()} (Friction: {TERRAIN_FRICTION.get(res['terrain'], 1.0)}x)")
    print(f"  Weather:         {res['weather'].capitalize()} (Modifier: {WEATHER_MODIFIERS.get(res['weather'], 1.0)}x)")
    print(f"  Effective Speed: {res['effective_speed_mpd']} miles/day")
    print(f"-------------------------------------------------------")
    print(f"  Total Duration:  {res['days']} Days (~{res['hours']} marching hours)")
    print(f"  Required Camps:  {res['camp_stops']} night(s) in the field")
    print(f"  Provisions:      {res['rations_lbs']} lbs of rations for {res['party_size']} traveler(s)")
    print(f"=======================================================\n")


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Travel & Transit Time Calculator")
    parser.add_argument("distance", type=float, help="Distance in miles")
    parser.add_argument("-m", "--mode", choices=list(VELOCITIES.keys()), default="infantry", help="Transportation mode")
    parser.add_argument("-t", "--terrain", choices=list(TERRAIN_FRICTION.keys()), default="plains", help="Terrain category")
    parser.add_argument("-w", "--weather", choices=list(WEATHER_MODIFIERS.keys()), default="clear", help="Weather conditions")
    parser.add_argument("-p", "--party", type=int, default=4, help="Party size")
    args = parser.parse_args()

    result = calculate_transit(
        distance_miles=args.distance,
        mode=args.mode,
        terrain=args.terrain,
        weather=args.weather,
        party_size=args.party,
    )
    print_travel_report(result)


if __name__ == "__main__":
    main()

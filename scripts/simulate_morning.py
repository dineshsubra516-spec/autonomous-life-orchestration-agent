#!/usr/bin/env python3
"""
Morning Routine Simulation Script
Demonstrates the autonomous life orchestration agent
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_api():
    """Test the API endpoints"""
    print_section("Testing API Endpoints")
    
    # Test config
    try:
        response = requests.get(f"{BASE_URL}/api/config")
        print("Config:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error fetching config: {e}")
        return False
    
    return True

def run_planner(class_time="09:00", location="IIT Madras"):
    """Run the morning routine planner"""
    print_section(f"Running Morning Routine Planner")
    print(f"Class Time: {class_time}")
    print(f"Location: {location}\n")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/run",
            params={
                "class_time": class_time,
                "location": location
            }
        )
        
        data = response.json()
        
        # Display results
        if data.get("state") == "ERROR":
            print("ERROR:", data.get("error"))
            return
        
        # Context
        context = data.get("context", {})
        print("CONTEXT")
        print(f"  Time: {context.get('current_time')}")
        print(f"  Date: {context.get('date')}")
        print(f"  Minutes until class: {context.get('minutes_until_class')}")
        print(f"  Distance: {context.get('distance_km')} km")
        
        # Food Options
        print("\nFOOD OPTIONS")
        for i, food in enumerate(data.get("food_options", []), 1):
            selected = " [SELECTED]" if data.get("selected_food", {}).get("restaurant") == food.get("restaurant") else ""
            print(f"  {i}. {food.get('item')} - {food.get('restaurant')}")
            print(f"     Price: Rs {food.get('price')} | Time: {food.get('eta_minutes')} min | Service: {food.get('service')}")
            print(f"     Rating: {food.get('rating')}{selected}")
        
        # Travel Options
        print("\nTRAVEL OPTIONS")
        for i, travel in enumerate(data.get("travel_options", []), 1):
            selected = " [SELECTED]" if (data.get("selected_travel", {}).get("service") == travel.get("service") and 
                                        data.get("selected_travel", {}).get("mode") == travel.get("mode")) else ""
            print(f"  {i}. {travel.get('service')} {travel.get('mode')}")
            print(f"     Cost: Rs {travel.get('cost')} | Time: {travel.get('eta_minutes')} min | Rating: {travel.get('rating')}{selected}")
        
        # Risk Assessment
        print("\nRISK ASSESSMENT")
        risk = data.get("risk", {})
        confidence = risk.get("confidence", 0)
        percentage = int(confidence * 100)
        conf_level = "HIGH" if confidence >= 0.8 else "MODERATE" if confidence >= 0.6 else "LOW"
        print(f"  Confidence: {percentage}% ({conf_level})")
        print(f"  Buffer Time: {risk.get('buffer_minutes')} minutes")
        print(f"  Recommendation: {risk.get('recommendation')}")
        
        reasoning = risk.get("reasoning", {})
        if reasoning:
            print("\n  Reasoning:")
            for key, value in reasoning.items():
                if key != "confidence":
                    print(f"    - {key}: {value}")
        
        # Decision
        state = data.get("state", "UNKNOWN")
        print(f"\nDECISION: {state}")
        
        if data.get("message"):
            print(f"Message: {data.get('message')}")
        
        # Execution
        if data.get("execution"):
            print("\nEXECUTION")
            exec_data = data.get("execution")
            print(f"  Food Ordered: {exec_data.get('food_ordered')}")
            print(f"  Travel Booked: {exec_data.get('travel_booked')}")
            print(f"  Status: {exec_data.get('status')}")
            print(f"  Confirmation Time: {exec_data.get('confirmation_time')}")
        
        # Schedule
        print("\nTODAY'S SCHEDULE")
        for item in data.get("schedule", []):
            print(f"  - {item}")
        
        return data
        
    except Exception as e:
        print(f"Error running planner: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_preferences():
    """Test user preferences endpoints"""
    print_section("Testing User Preferences")
    
    try:
        # Get preferences
        response = requests.get(f"{BASE_URL}/api/preferences")
        print("Current Preferences:")
        print(json.dumps(response.json(), indent=2))
        
    except Exception as e:
        print(f"Error getting preferences: {e}")

def test_multiple_scenarios():
    """Test multiple scenarios"""
    print_section("Testing Multiple Scenarios")
    
    scenarios = [
        ("09:00", "IIT Madras"),
        ("08:30", "Presidency College"),
        ("10:00", "Anna University")
    ]
    
    for class_time, location in scenarios:
        data = run_planner(class_time, location)
        if data:
            print(f"\nscenario completed: {class_time} at {location}")
        input("Press Enter for next scenario...")

def main():
    """Main function"""
    print_section("Autonomous Life Orchestration Agent - Test Suite")
    
    print("Available tests:")
    print("  1. Test API config")
    print("  2. Run morning planner (default time)")
    print("  3. Run morning planner (custom time)")
    print("  4. Test preferences")
    print("  5. Run all scenarios")
    print("  6. Exit")
    
    while True:
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            test_api()
        elif choice == "2":
            run_planner()
        elif choice == "3":
            class_time = input("Enter class time (HH:MM): ").strip()
            location = input("Enter location: ").strip()
            if class_time and location:
                run_planner(class_time, location)
        elif choice == "4":
            test_preferences()
        elif choice == "5":
            test_multiple_scenarios()
        elif choice == "6":
            print("\nExiting...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick test mode
        print_section("Quick Test - Running Morning Planner")
        run_planner("09:00", "IIT Madras")
    else:
        # Interactive mode
        main()

#!/usr/bin/env python3
"""Test Azure Functions endpoints"""

import requests
import json
import time
import os

# Set up environment
os.environ['TESTING_MODE'] = 'true'
os.environ['IDEA_GUY_SHEET_ID'] = '1bGxOTEPxx3vF3UwPAK7SBUAt1dNqVWAvl3W07Zdj4rs'

BASE_URL = "http://localhost:7071/api"

def test_endpoint(method, endpoint, data=None, params=None):
    """Test an endpoint and return results."""
    url = f"{BASE_URL}/{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        print(f"\n{'='*60}")
        print(f"Testing {method} {endpoint}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Response Type: {type(result)}")
                if isinstance(result, dict):
                    print("Response Keys:", list(result.keys()))
                    # Show first few characters of each value
                    for key, value in result.items():
                        if isinstance(value, str) and len(value) > 100:
                            print(f"  {key}: {value[:100]}...")
                        elif isinstance(value, list) and len(value) > 0:
                            print(f"  {key}: [{len(value)} items] {value[0] if value else ''}")
                        else:
                            print(f"  {key}: {value}")
                else:
                    print(f"Response: {result}")
                print("✅ PASSED")
                return True, result
            except json.JSONDecodeError:
                print(f"Response Text: {response.text[:200]}...")
                print("⚠️  Non-JSON response but status 200")
                return True, response.text
        else:
            print(f"Error: {response.text}")
            print("❌ FAILED")
            return False, None
            
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"Testing {method} {endpoint}")
        print(f"Exception: {str(e)}")
        print("❌ FAILED")
        return False, None

def main():
    print("🧪 Testing Azure Functions Endpoints")
    print("=====================================")
    
    results = {}
    
    # Test 1: Get Instructions
    print("\n1. Testing GET /api/get_instructions")
    success, result = test_endpoint("GET", "get_instructions")
    results["get_instructions"] = success
    
    # Test 2: Get Price Points  
    print("\n2. Testing POST /api/get_pricepoints")
    success, result = test_endpoint("POST", "get_pricepoints", data={})
    results["get_pricepoints"] = success
    
    # Test 3: Read Sheet
    print("\n3. Testing GET /api/read_sheet")
    success, result = test_endpoint("GET", "read_sheet")
    results["read_sheet"] = success
    
    # Test 4: Execute Analysis
    print("\n4. Testing POST /api/execute_analysis")
    test_data = {
        "user_input": {
            "Idea_Overview": "AI-powered fitness app for busy professionals",
            "Deliverable": "Mobile app with personalized workout plans", 
            "Motivation": "Help people stay healthy despite busy schedules"
        },
        "budget_tier": "basic"
    }
    success, result = test_endpoint("POST", "execute_analysis", data=test_data)
    results["execute_analysis"] = success
    
    # If execute_analysis worked, test process_idea
    if success and result and isinstance(result, dict) and "job_id" in result:
        job_id = result["job_id"]
        print(f"\n5. Testing GET /api/process_idea with job_id: {job_id}")
        success, result = test_endpoint("GET", "process_idea", params={"id": job_id})
        results["process_idea"] = success
    else:
        print("\n5. Skipping /api/process_idea (no job_id from execute_analysis)")
        results["process_idea"] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("ENDPOINT TESTING SUMMARY")
    print(f"{'='*60}")
    
    total = len(results)
    passed = sum(1 for success in results.values() if success)
    
    for endpoint, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{endpoint:20} {status}")
    
    print(f"\nOverall: {passed}/{total} endpoints working ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("🎉 All endpoints are working correctly!")
    else:
        print("⚠️  Some endpoints need attention")

if __name__ == "__main__":
    main()
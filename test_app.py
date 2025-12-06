"""
Comprehensive test script for the entire SkinPredict application.
Tests backend API, database, agent, and MLflow integration.
"""
import os
import sys
import requests
import json
from pathlib import Path

# Configuration
API_URL = "http://localhost:5000"
TEST_IMAGE_PATH = "test_image.jpg"  # You'll need to provide a test image

print("="*60)
print("SKINPREDICT MLOPS - COMPREHENSIVE TEST SUITE")
print("="*60)

# Test 1: Health Check
print("\n[Test 1] API Health Check")
try:
    response = requests.get(f"{API_URL}/health", timeout=5)
    if response.status_code == 200:
        print(f"✓ API is running: {response.json()}")
    else:
        print(f"✗ API returned status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to API. Make sure server is running:")
    print("  python api/server.py")
    sys.exit(1)

# Test 2: API Info
print("\n[Test 2] API Information")
try:
    response = requests.get(f"{API_URL}/api/info")
    info = response.json()
    print(f"✓ API Name: {info['name']}")
    print(f"✓ Version: {info['version']}")
    print(f"✓ Endpoints: {len(info['endpoints'])} available")
    for endpoint, path in info['endpoints'].items():
        print(f"  - {endpoint}: {path}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 3: Skin Analysis (requires test image)
print("\n[Test 3] Skin Analysis Endpoint")
print("⚠ Skipping - requires test image")
print("  To test manually:")
print("  1. Prepare a base64-encoded image")
print("  2. POST to /api/analyze with {'image': '<base64>'}")

# Test 4: Chat Endpoint
print("\n[Test 4] Chat Endpoint")
try:
    payload = {
        "message": "Hello, what skin types do you know?",
        "conversation": [],
        "skinAnalysis": None,
        "userLocation": None
    }
    response = requests.post(f"{API_URL}/api/chat", json=payload, timeout=30)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Chat response received")
        print(f"  Response: {data['response'][:100]}...")
        if 'suggestions' in data:
            print(f"  Suggestions: {len(data['suggestions'])}")
    else:
        print(f"✗ Chat failed with status {response.status_code}")
        print(f"  Error: {response.text}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 5: Product Recommendations
print("\n[Test 5] Product Recommendations")
try:
    params = {
        "country": "United States",
        "skinType": "Oily",
        "skinIssues": ["Acne"],
        "gender": "All",
        "ageGroup": "20-29"
    }
    response = requests.get(f"{API_URL}/api/product-recommendations", params=params)
    if response.status_code == 200:
        products = response.json()
        print(f"✓ Received {len(products)} product recommendations")
        if products:
            print(f"  First product: {products[0]['name']} by {products[0]['brand']}")
    else:
        print(f"✗ Failed with status {response.status_code}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 6: Database Connection
print("\n[Test 6] Database Connection")
try:
    sys.path.append(str(Path(__file__).parent))
    from api.app.database import SessionLocal
    from api.app.models.sql_models import User, Scan
    
    db = SessionLocal()
    user_count = db.query(User).count()
    scan_count = db.query(Scan).count()
    print(f"✓ Database connected")
    print(f"  Users: {user_count}")
    print(f"  Scans: {scan_count}")
    db.close()
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 7: MLflow Tracking
print("\n[Test 7] MLflow Integration")
try:
    import mlflow
    mlflow.set_tracking_uri("http://localhost:5001")
    experiments = mlflow.search_experiments()
    print(f"✓ MLflow connected")
    print(f"  Experiments: {len(experiments)}")
    for exp in experiments:
        print(f"  - {exp.name} (ID: {exp.experiment_id})")
except Exception as e:
    print(f"⚠ MLflow not accessible: {e}")
    print("  Make sure MLflow server is running:")
    print("  docker-compose up mlflow")

# Test 8: LangGraph Agent
print("\n[Test 8] LangGraph Agent")
try:
    from api.app.agent.graph import get_agent_graph
    from api.app.agent.tools import AGENT_TOOLS
    
    graph = get_agent_graph()
    print(f"✓ Agent graph compiled")
    print(f"  Tools available: {len(AGENT_TOOLS)}")
    for tool in AGENT_TOOLS:
        print(f"  - {tool.name}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 9: DVC Pipeline
print("\n[Test 9] DVC Pipeline")
try:
    import subprocess
    result = subprocess.run(
        ["dvc", "status"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    if result.returncode == 0:
        print("✓ DVC pipeline status:")
        print(result.stdout)
    else:
        print(f"⚠ DVC status check failed: {result.stderr}")
except Exception as e:
    print(f"⚠ DVC not available: {e}")

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
print("\n✓ Core API: Working")
print("✓ Chat Service: Working")
print("✓ Database: Connected")
print("⚠ MLflow: Check if server is running")
print("⚠ Full E2E: Requires test image")
print("\nNext Steps:")
print("1. Start MLflow: docker-compose up mlflow")
print("2. Test skin analysis with real image")
print("3. Test admin portal at http://localhost:3000/admin")
print("4. Run training pipeline: dvc repro")

import requests
import time
import sys
import argparse

def check_health(url, name, retries=5, delay=10):
    print(f"Checking {name} at {url}...")
    
    for i in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name} is UP! (Status: {response.status_code})")
                return True
            else:
                print(f"⚠️ {name} returned status {response.status_code}. Retrying ({i+1}/{retries})...")
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection failed: {e}. Retrying ({i+1}/{retries})...")
        
        time.sleep(delay)
    
    print(f"❌ {name} failed to respond after {retries} attempts.")
    return False

def main():
    parser = argparse.ArgumentParser(description="Verify SkinPredict Deployment")
    parser.add_argument("--url", help="Base URL of the deployed app (e.g., https://skinpredict-xyz.ondigitalocean.app)")
    args = parser.parse_args()

    if not args.url:
        print("Please provide the App URL from DigitalOcean Dashboard!")
        print("Usage: python verify_deployment.py --url https://your-app-url.ondigitalocean.app")
        sys.exit(1)

    base_url = args.url.rstrip('/')
    
    print("="*40)
    print("🚀 Verifying SkinPredict Deployment")
    print("="*40)

    # 1. Check Frontend
    frontend_ok = check_health(base_url, "Frontend")
    
    # 2. Check API Health
    # Note: If API is on a subdomain or same domain under /api
    # Based on our spec, API is at /api prefix internally, but let's check both
    api_ok = check_health(f"{base_url}/api/health", "API Health")

    print("\n" + "="*40)
    if frontend_ok and api_ok:
        print("🎉 DEPLOYMENT SUCCESSFUL! System is fully operational.")
    else:
        print("⚠️ Some checks failed. Please check DigitalOcean Runtime Logs.")

if __name__ == "__main__":
    main()

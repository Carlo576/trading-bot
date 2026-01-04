# Api_test.py - UPDATED
import requests
import json
from datetime import datetime

def test_multiple_endpoints():
    """Test different MyFXBook API endpoints."""
    print("🧪 Testing Multiple MyFXBook Endpoints...")
    
    # Different endpoints to try
    endpoints = [
        "https://www.myfxbook.com/api/get-community-outlook.json",
        "https://www.myfxbook.com/api/get-outlook.json",
        "https://www.myfxbook.com/api/get-data-symbols.json",
        "https://www.myfxbook.com/forex-market/sentiment"  # Fallback to web scraping
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/html, */*',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    for i, url in enumerate(endpoints[:3], 1):  # Test API endpoints first
        print(f"\n{i}️⃣ Testing: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("✅ JSON response received!")
                    print("📋 Response:")
                    print("=" * 30)
                    print(json.dumps(data, indent=2))
                    print("=" * 30)
                    
                    # Check if this contains useful data
                    if not data.get('error'):
                        print("🎯 This endpoint works! No error detected.")
                        return data
                    else:
                        print(f"❌ API Error: {data.get('message', 'Unknown error')}")
                        
                except json.JSONDecodeError:
                    print("⚠️ Response is not JSON")
                    print(f"Response text: {response.text[:200]}...")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # If APIs fail, try web scraping approach
    print(f"\n4️⃣ Fallback: Web scraping sentiment page...")
    return test_web_scraping()

def test_web_scraping():
    """Test web scraping the sentiment page."""
    try:
        url = "https://www.myfxbook.com/forex-market/sentiment"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        print(f"📊 Web page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully loaded sentiment page!")
            
            # Look for percentage signs and currency mentions
            text = response.text
            
            # Count occurrences
            percent_count = text.count('%')
            print(f"📊 Found {percent_count} percentage signs")
            
            # Look for common currency pairs
            pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD']
            found_pairs = []
            
            for pair in pairs:
                if pair in text.upper():
                    found_pairs.append(pair)
            
            if found_pairs:
                print(f"💱 Found currency pairs: {found_pairs}")
                return {'method': 'scraping', 'pairs_found': found_pairs, 'page_size': len(text)}
            else:
                print("⚠️ No currency pairs found in obvious format")
                
            # Show a sample of the page content for analysis
            print(f"\n📄 Page sample (first 500 chars):")
            print(text[:500])
            
        return None
        
    except Exception as e:
        print(f"❌ Web scraping failed: {e}")
        return None

if __name__ == '__main__':
    result = test_multiple_endpoints()
    
    print("\n" + "="*50)
    if result:
        print("🎉 SUCCESS! Found a working method.")
        print(f"📊 Method: {result.get('method', 'API')}")
    else:
        print("❌ All methods failed. Need to investigate further.")
    print("="*50)

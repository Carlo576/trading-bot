# widget_test.py
import requests
import re
import json
from datetime import datetime

def test_myfxbook_widget():
    """Test the MyFXBook widget endpoint."""
    print(" 🎯 Testing MyFXBook Widget Endpoint...")
    
    # The widget JavaScript URL you found
    widget_url = "https://widgets.myfxbook.com/scripts/fxOutlook.js"
    
    # Parameters from the widget
    params = {
        'type': '1',
        'symbols': ',1,2,3,4,5,6,7,8,9,10,11,12,13,14,17,20,24,25,26,27,28,29,37,40,43,46,47,48,49,50,51,103,107,2115'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.myfxbook.com/'
    }
    
    try:
        print(f" 📡 Calling widget URL...")
        response = requests.get(widget_url, params=params, headers=headers, timeout=15)
        print(f" 📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(" ✅ Widget script loaded successfully!")
            
            # The response should be JavaScript containing data
            js_content = response.text
            print(f" 📄 Response length: {len(js_content)} characters")
            
            # Show first 500 characters to see structure
            print("\n 📋 JavaScript Content Preview:")
            print("=" * 50)
            print(js_content[:500])
            print("=" * 50)
            
            # Look for data patterns in the JavaScript
            if 'outlook' in js_content.lower():
                print(" 🎯 Found 'outlook' in response!")
                
            if '%' in js_content:
                print(" 📊 Found percentage signs - likely sentiment data!")
                
            # Try to extract JSON-like data from JavaScript
            json_data = extract_data_from_js(js_content)
            if json_data:
                print(" ✅ Successfully extracted sentiment data!")
                return json_data
            else:
                print(" ⚠️ Need to analyze JavaScript structure further")
                return {'raw_js': js_content[:1000]}  # Return sample for analysis
                
        else:
            print(f" ❌ Failed to load widget: {response.status_code}")
            return None
            
    except Exception as e:
        print(f" ❌ Error: {e}")
        return None

def extract_data_from_js(js_content):
    """Extract sentiment data from JavaScript content."""
    try:
        print(" 🔍 Analyzing JavaScript content for data...")
        
        # Look for common patterns in MyFXBook widget JavaScript
        patterns = [
            r'outlook\s*=\s*(\[.*?\])',  # outlook = [data]
            r'data\s*=\s*(\{.*?\})',     # data = {object}
            r'symbols\s*=\s*(\[.*?\])',  # symbols = [array]
            r'(\{.*?"symbol".*?\})',     # {symbol: data}
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content, re.DOTALL)
            if matches:
                print(f" 🎯 Found potential data with pattern: {pattern}")
                for match in matches[:3]:  # Check first 3 matches
                    try:
                        # Try to parse as JSON
                        data = json.loads(match)
                        print(" ✅ Successfully parsed JSON data!")
                        return data
                    except json.JSONDecodeError:
                        print(" ⚠️ Found data but not valid JSON")
                        continue
        
        # Look for percentage values with currency pairs
        percent_matches = re.findall(r'([A-Z]{6})["\s]*[,:][\s"]*(\d+(?:\.\d+)?)%?', js_content)
        if percent_matches:
            print(f" 📊 Found {len(percent_matches)} currency/percentage pairs")
            sentiment_data = {}
            for pair, percentage in percent_matches[:10]:  # First 10 matches
                if len(pair) == 6:  # EURUSD, GBPUSD, etc.
                    sentiment_data[pair] = float(percentage)
            
            if sentiment_data:
                return {
                    'extracted_pairs': sentiment_data,
                    'source': 'widget_pattern_match',
                    'timestamp': datetime.now().isoformat()
                }
        
        return None
        
    except Exception as e:
        print(f" ❌ Error extracting data: {e}")
        return None

if __name__ == '__main__':
    result = test_myfxbook_widget()
    
    print("\n" + "="*60)
    if result:
        print(" 🎉 WIDGET TEST RESULTS:")
        print(json.dumps(result, indent=2))
    else:
        print(" ❌ Widget test failed")
    print("="*60)

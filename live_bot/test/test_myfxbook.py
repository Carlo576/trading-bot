import requests
from urllib.parse import unquote
import os
from dotenv import load_dotenv

# Load secrets from .env file
load_dotenv()

# Get credentials from environment
MYFXBOOK_EMAIL = os.getenv('MYFXBOOK_EMAIL')
MYFXBOOK_PASSWORD = os.getenv('MYFXBOOK_PASSWORD')

# Safety check
if not MYFXBOOK_EMAIL or not MYFXBOOK_PASSWORD:
    print("❌ ERROR: MyFxBook credentials not found in .env file!")
    exit()

def test_myfxbook_login():
    """Test if we can login to MyFxBook API"""
    print("🔄 Testing MyFxBook API login...")
    
    # Step 1: Login to get session
    login_url = 'https://www.myfxbook.com/api/login.json'
    login_params = {
        'email': MYFXBOOK_EMAIL,
        'password': MYFXBOOK_PASSWORD
    }
    
    try:
        response = requests.get(login_url, params=login_params)
        data = response.json()
        
        # Check if login was successful
        if data.get('error'):
            print(f"❌ Login failed: {data.get('message')}")
            return None
        
        # Decode the session (fix URL encoding)
        session = unquote(data.get('session'))
        print(f"✅ Login successful!")
        print(f"📝 Session ID: {session[:20]}...")
        return session
        
    except Exception as e:
        print(f"❌ Error connecting to MyFxBook: {e}")
        return None

def test_get_sentiment(session):
    """Test getting community outlook data WITH VOLUME"""
    print("\n🔄 Testing sentiment data retrieval...")
    
    outlook_url = 'https://www.myfxbook.com/api/get-community-outlook.json'
    outlook_params = {'session': session}
    
    try:
        response = requests.get(outlook_url, params=outlook_params)
        data = response.json()
        
        if data.get('error'):
            print(f"❌ Failed to get sentiment: {data.get('message')}")
            return None
        
        print(f"✅ Sentiment data retrieved!")
        print(f"📊 Found {len(data.get('symbols', []))} currency pairs")
        
        # Show EURUSD as example WITH CORRECT VOLUME
        for symbol in data.get('symbols', []):
            if symbol['name'] == 'EURUSD':
                long_pct = symbol['longPercentage']
                short_pct = symbol['shortPercentage']
                long_volume = symbol.get('longVolume', 0)
                short_volume = symbol.get('shortVolume', 0)
                total_volume = long_volume + short_volume
                
                print(f"\n💡 EURUSD Example:")
                print(f"   Long: {long_pct}%")
                print(f"   Short: {short_pct}%")
                print(f"   📦 Long Volume: {long_volume:.2f} lots")
                print(f"   📦 Short Volume: {short_volume:.2f} lots")
                print(f"   📦 Total Volume: {total_volume:.2f} lots")
                
                # Check volume sufficiency
                if total_volume >= 100:
                    print(f"   ✅ Sufficient volume for analysis")
                else:
                    print(f"   ⚠️ Low volume - sentiment not reliable")
                
                break
        
        return data
        
    except Exception as e:
        print(f"❌ Error getting sentiment: {e}")
        return None

if __name__ == '__main__':
    print("=" * 50)
    print("MyFxBook API Test")
    print("=" * 50)
    
    # Test login
    session = test_myfxbook_login()
    
    if session:
        # Test getting sentiment data
        sentiment_data = test_get_sentiment(session)
        
        if sentiment_data:
            print("\n" + "=" * 50)
            print("🎉 ALL TESTS PASSED!")
            print("=" * 50)
        else:
            print("\n❌ Sentiment test failed")
    else:
        print("\n❌ Login test failed")

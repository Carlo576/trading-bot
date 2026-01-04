# myfxbook_api.py

import requests
from urllib.parse import unquote
import os
from dotenv import load_dotenv

load_dotenv()

class MyFxBookAPI:
    """Clean wrapper for MyFxBook API"""
    
    def __init__(self):
        self.email = os.getenv('MYFXBOOK_EMAIL')
        self.password = os.getenv('MYFXBOOK_PASSWORD')
        self.session = None
        
        if not self.email or not self.password:
            raise ValueError("❌ MyFxBook credentials not found in .env file!")
    
    def login(self):
        """Login and get session token"""
        login_url = 'https://www.myfxbook.com/api/login.json'
        login_params = {
            'email': self.email,
            'password': self.password
        }
        
        try:
            response = requests.get(login_url, params=login_params)
            data = response.json()
            
            if data.get('error'):
                print(f"❌ Login failed: {data.get('message')}")
                return False
            
            self.session = unquote(data.get('session'))
            return True
            
        except Exception as e:
            print(f"❌ Error logging in: {e}")
            return False
    
    def get_pair_sentiment(self, forex_pair):
        """
        Get sentiment data for a specific forex pair
        
        Args:
            forex_pair: 'EURUSD', 'GBPUSD', etc.
        
        Returns:
            {
                'longPercentage': 28,
                'shortPercentage': 72,
                'longVolume': 4421.08,
                'shortVolume': 11276.17
            }
            or None if not found
        """
        if not self.session:
            if not self.login():
                return None
        
        outlook_url = 'https://www.myfxbook.com/api/get-community-outlook.json'
        outlook_params = {'session': self.session}
        
        try:
            response = requests.get(outlook_url, params=outlook_params)
            data = response.json()
            
            if data.get('error'):
                print(f"❌ Failed to get sentiment: {data.get('message')}")
                return None
            
            # Find the specific pair
            for symbol in data.get('symbols', []):
                if symbol['name'] == forex_pair.upper():
                    return {
                        'longPercentage': symbol['longPercentage'],
                        'shortPercentage': symbol['shortPercentage'],
                        'longVolume': symbol.get('longVolume', 0),
                        'shortVolume': symbol.get('shortVolume', 0)
                    }
            
            print(f"⚠️ Pair {forex_pair} not found in MyFxBook data")
            return None
            
        except Exception as e:
            print(f"❌ Error getting sentiment: {e}")
            return None


# Test the wrapper
if __name__ == '__main__':
    print("=" * 50)
    print("Testing MyFxBook API Wrapper")
    print("=" * 50)
    
    api = MyFxBookAPI()
    
    # Test login
    if api.login():
        print("✅ Login successful!")
        
        # Test getting EURUSD sentiment
        eurusd = api.get_pair_sentiment('EURUSD')
        if eurusd:
            total_volume = eurusd['longVolume'] + eurusd['shortVolume']
            print(f"\n💡 EURUSD Sentiment:")
            print(f"   Long: {eurusd['longPercentage']}%")
            print(f"   Short: {eurusd['shortPercentage']}%")
            print(f"   Total Volume: {total_volume:.2f} lots")
            
            if total_volume >= 100:
                print(f"   ✅ Sufficient volume")
            else:
                print(f"   ⚠️ Low volume")
        
        # Test getting GBPUSD sentiment
        gbpusd = api.get_pair_sentiment('GBPUSD')
        if gbpusd:
            total_volume = gbpusd['longVolume'] + gbpusd['shortVolume']
            print(f"\n💡 GBPUSD Sentiment:")
            print(f"   Long: {gbpusd['longPercentage']}%")
            print(f"   Short: {gbpusd['shortPercentage']}%")
            print(f"   Total Volume: {total_volume:.2f} lots")
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 50)
    else:
        print("❌ Login failed")

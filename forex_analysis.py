# forex_analysis.py

def analyze_forex_signal(signal_action, forex_pair, myfxbook_data):
    """
    Analyze forex signal with volume and contrarian logic
    
    Args:
        signal_action: 'LONG', 'SHORT', 'BUY', 'SELL'
        forex_pair: 'EURUSD', 'GBPUSD', etc.
        myfxbook_data: {
            'longPercentage': 28,
            'shortPercentage': 72,
            'longVolume': 4421.08,
            'shortVolume': 11276.17
        }
    
    Returns:
        {
            'take_trade': True/False,
            'reason': 'explanation',
            'volume_sufficient': True/False,
            'strength': 'LOW_VOLUME' or 'WEAK' or 'GOOD' etc.
        }
    """
    
    long_pct = myfxbook_data['longPercentage']
    short_pct = myfxbook_data['shortPercentage']
    long_volume = myfxbook_data.get('longVolume', 0)
    short_volume = myfxbook_data.get('shortVolume', 0)
    total_volume = long_volume + short_volume
    
    # Step 1: Check volume sufficiency
    volume_sufficient = total_volume >= 100
    
    # Step 2: Determine our trade direction
    is_long_signal = signal_action.upper() in ['LONG', 'BUY']
    is_short_signal = signal_action.upper() in ['SHORT', 'SELL']
    
    if is_long_signal:
        our_direction = "LONG"
        retail_contrarian_pct = short_pct   # We want retail to be SHORT
        retail_direction = "SHORT"
    elif is_short_signal:
        our_direction = "SHORT"
        retail_contrarian_pct = long_pct    # We want retail to be LONG
        retail_direction = "LONG"
    else:
        return {
            'take_trade': False,
            'reason': f'Unknown signal: {signal_action}',
            'volume_sufficient': volume_sufficient,
            'strength': 'INVALID'
        }
    
    # Step 3: Decision logic based on volume
    if not volume_sufficient:
        # Low volume - show signal but don't use sentiment
        return {
            'take_trade': True,   # Show the trade
            'reason': f'Low volume ({total_volume:.2f} lots < 100). Technical signal only: {our_direction} {forex_pair}',
            'volume_sufficient': False,
            'strength': 'LOW_VOLUME ⚠️',
            'retail_sentiment': retail_contrarian_pct,
            'our_direction': our_direction,
            'retail_direction': retail_direction,
            'total_volume': total_volume
        }
    
    # Step 4: High volume - apply contrarian logic
    contrarian_threshold = 65
    contrarian_confirmed = retail_contrarian_pct >= contrarian_threshold
    
    # Determine strength levels for high volume
    if retail_contrarian_pct >= 85:
        strength = "EXCELLENT 🔥"
    elif retail_contrarian_pct >= 75:
        strength = "STRONG 💪"
    elif retail_contrarian_pct >= 65:
        strength = "GOOD ✅"
    else:
        strength = "WEAK ⚠️"
    
    if contrarian_confirmed:
        reason = f"Contrarian confirmed: {retail_contrarian_pct}% retail {retail_direction} vs our {our_direction}"
        take_trade = True
    else:
        reason = f"Contrarian rejected: Only {retail_contrarian_pct}% retail {retail_direction} (need ≥{contrarian_threshold}%)"
        take_trade = False
    
    return {
        'take_trade': take_trade,
        'reason': reason,
        'volume_sufficient': True,
        'strength': strength,
        'retail_sentiment': retail_contrarian_pct,
        'our_direction': our_direction,
        'retail_direction': retail_direction,
        'total_volume': total_volume
    }


# Test function
if __name__ == '__main__':
    print("Testing Forex Analysis...")
    
    # Test 1: High volume, good contrarian signal (REAL EURUSD DATA)
    test_data_1 = {
        'longPercentage': 28,
        'shortPercentage': 72,
        'longVolume': 4421.08,
        'shortVolume': 11276.17
    }
    result_1 = analyze_forex_signal('LONG', 'EURUSD', test_data_1)
    print(f"\nTest 1 - LONG EURUSD with high volume:")
    print(f"Take trade: {result_1['take_trade']}")
    print(f"Reason: {result_1['reason']}")
    print(f"Strength: {result_1['strength']}")
    print(f"Total Volume: {result_1['total_volume']:.2f} lots")
    
    # Test 2: Low volume
    test_data_2 = {
        'longPercentage': 45,
        'shortPercentage': 55,
        'longVolume': 30,
        'shortVolume': 50
    }
    result_2 = analyze_forex_signal('LONG', 'GBPUSD', test_data_2)
    print(f"\nTest 2 - LONG GBPUSD with low volume:")
    print(f"Take trade: {result_2['take_trade']}")
    print(f"Reason: {result_2['reason']}")
    print(f"Strength: {result_2['strength']}")
    print(f"Total Volume: {result_2['total_volume']:.2f} lots")
    
    # Test 3: High volume, weak contrarian signal
    test_data_3 = {
        'longPercentage': 45,
        'shortPercentage': 55,
        'longVolume': 1000,
        'shortVolume': 1200
    }
    result_3 = analyze_forex_signal('LONG', 'USDJPY', test_data_3)
    print(f"\nTest 3 - LONG USDJPY with weak contrarian:")
    print(f"Take trade: {result_3['take_trade']}")
    print(f"Reason: {result_3['reason']}")
    print(f"Strength: {result_3['strength']}")
    print(f"Total Volume: {result_3['total_volume']:.2f} lots")

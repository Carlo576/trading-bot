import         sys
import         os

#         A d d         live_bot         folder         to         Python         path
sys.path.append(os.path.dirname(__file__))

#         A d d         parent         folder         (trading-bot/)         to         path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
import asyncio
from telegram import Bot
from datetime import datetime

from myfxbook_api import MyFxBookAPI
from forex_analysis import analyze_forex_signal

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

PAIR_MAPPING = {
    'XAGUSD': 'XAGUSD',
    'XAUUSD': 'XAUUSD',
    'COPPER': 'COPPER',
    'EURUSD': 'EURUSD',
    'GBPUSD': 'GBPUSD',
    'AUDUSD': 'AUDUSD',
    'NZDUSD': 'NZDUSD',
    'USDCAD': 'USDCAD',
    'USDJPY': 'USDJPY',
    'USDCHF': 'USDCHF',
    'USDNOK': 'USDNOK',
    'USDSEK': 'USDSEK',
    'EURGBP': 'EURGBP',
    'EURJPY': 'EURJPY',
    'EURCAD': 'EURCAD',
    'EURAUD': 'EURAUD',
    'EURNZD': 'EURNZD',
    'EURCHF': 'EURCHF',
    'EURNOK': 'EURNOK',
    'EURSEK': 'EURSEK',
    'GBPJPY': 'GBPJPY',
    'GBPCAD': 'GBPCAD',
    'GBPAUD': 'GBPAUD',
    'GBPNZD': 'GBPNZD',
    'GBPCHF': 'GBPCHF',
    'GBPNOK': 'GBPNOK',
    'GBPSEK': 'GBPSEK',
    'AUDJPY': 'AUDJPY',
    'AUDNZD': 'AUDNZD',
    'AUDCAD': 'AUDCAD',
    'AUDCHF': 'AUDCHF',
    'NZDCAD': 'NZDCAD',
    'NZDCHF': 'NZDCHF',
    'NZDJPY': 'NZDJPY',
    'CADJPY': 'CADJPY',
    'CADCHF': 'CADCHF',
    'CHFJPY': 'CHFJPY',
}


def get_gmail_service():
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                creds = None
        
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                scopes=SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)


def get_unread_emails(service, query='is:unread'):
    try:
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=10
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("No unread emails found.")
            return []
        
        email_list = []
        for message in messages:
            msg = service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()
            email_list.append(msg)
        
        return email_list
        
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []


def parse_email(email):
    try:
        headers = email['payload']['headers']
        subject = ''
        sender = ''
        
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            if header['name'] == 'From':
                sender = header['value']
        
        snippet = email.get('snippet', '')
        
        return {
            'subject': subject,
            'sender': sender,
            'snippet': snippet,
            'id': email['id']
        }
        
    except Exception as e:
        print(f"Error parsing email: {e}")
        return None


def mark_email_as_read(service, email_id):
    """Mark an email as read in Gmail."""
    try:
        service.users().messages().modify(
            userId='me',
            id=email_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        print(f"Marked email {email_id} as read")
        return True
    except Exception as e:
        print(f"Error marking email as read: {e}")
        return False


def extract_forex_pair(text):
    text_upper = text.upper()
    for pair in PAIR_MAPPING.keys():
        if pair in text_upper:
            return pair
    return None


async def send_telegram_alert(signal):
    try:
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not token or not chat_id:
            print("Missing Telegram credentials in .env file")
            return
        
        bot = Bot(token=token)
        decision = signal['contrarian_decision']
        sentiment = signal['myfxbook_sentiment']
        
        if decision['volume_sufficient']:
            volume_status = f"{decision['total_volume']:.2f} lots"
        else:
            volume_status = f"{decision['total_volume']:.2f} lots (LOW VOLUME)"
        
        message = f"""TRADING SIGNAL APPROVED

Action: {decision['our_direction']} {signal['pair']}
Strength: {decision['strength']}

Analysis:
    TradingView: {signal['action']} {signal['pair']}
    Retail Sentiment: {decision['retail_sentiment']}% {decision['retail_direction']}
    Our Position: {decision['our_direction']} (contrarian)
    Volume: {volume_status}

Logic: {decision['reason']}

Original Alert: {signal['subject']}
Time: {signal['detected_at']}
"""
        
        await bot.send_message(chat_id=chat_id, text=message)
        print("Alert sent to Telegram")
        
    except Exception as e:
        print(f"Error sending to Telegram: {e}")


def detect_trading_signals(service, emails):
    """Detect and analyze trading signals with contrarian logic."""
    signals = []
    myfxbook = MyFxBookAPI()
    
    if not myfxbook.login():
        print("Failed to login to MyFxBook")
        return signals
    
    for email in emails:
        parsed = parse_email(email)
        if not parsed:
            continue
        
        email_id = parsed['id']
        
        if "alert:" not in parsed['subject'].lower():
            mark_email_as_read(service, email_id)
            continue
        
        subject = parsed['subject']
        words = subject.split()
        
        action = None
        pair = None
        
        for word in words:
            if word.upper() in ['BUY', 'SELL', 'SWING', 'LONG', 'SHORT']:
                action = word.upper()
            
            detected_pair = extract_forex_pair(word)
            if detected_pair:
                pair = detected_pair
        
        if not action or not pair:
            print(f"Could not extract action/pair from: {subject}")
            mark_email_as_read(service, email_id)
            continue
        
        print(f"\nTRADING SIGNAL DETECTED")
        print(f"Action: {action}")
        print(f"Pair: {pair}")
        print(f"Subject: {subject}")
        print("-" * 50)
        
        sentiment = myfxbook.get_pair_sentiment(pair)
        
        if not sentiment:
            print(f"Could not get sentiment for {pair}")
            mark_email_as_read(service, email_id)
            continue
        
        decision = analyze_forex_signal(action, pair, sentiment)
        
        if decision['take_trade']:
            signal = {
                'type': 'FOREX_SIGNAL',
                'sender': parsed['sender'],
                'subject': subject,
                'snippet': parsed['snippet'],
                'detected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'action': action,
                'pair': pair,
                'contrarian_decision': decision,
                'myfxbook_sentiment': sentiment
            }
            
            signals.append(signal)
            
            print(f"APPROVED: {decision['reason']}")
            print(f"Strength: {decision['strength']}")
            
            try:
                asyncio.run(send_telegram_alert(signal))
            except Exception as e:
                print(f"Error sending to Telegram: {e}")
        else:
            print(f"REJECTED: {decision['reason']}")
        
        mark_email_as_read(service, email_id)
        print("-" * 50)
    
    return signals


if __name__ == '__main__':
    print("Connecting to Gmail...")
    service = get_gmail_service()
    print("Connected to Gmail")
    
    print("\nFetching unread emails...")
    emails = get_unread_emails(service)
    print(f"\nFound {len(emails)} unread email(s)")
    
    signals = detect_trading_signals(service, emails)
    
    print(f"\n{len(signals)} signal(s) approved and sent to Telegram")

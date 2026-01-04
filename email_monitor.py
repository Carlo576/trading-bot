import                                                         os
import                                                         pickle
from                                                         google.auth.transport.requests                                                         import                                                         Request
from                                                         google_auth_oauthlib.flow                                                         import                                                         InstalledAppFlow
from                                                         googleapiclient.discovery                                                         import                                                         build
from                                                         dotenv                                                         import                                                         load_dotenv
import                                                         asyncio
from                                                         telegram                                                         import                                                         Bot

#                                                         Load                                                         environment                                                         variables
load_dotenv()

#                                                         Gmail                                                         API                                                         scopes
SCOPES                                                         =                                                         ['https://www.googleapis.com/auth/gmail.readonly']

def                                                         get_gmail_service():
    """Get                                                         Gmail                                                         API                                                         service                                                         with                                                         authentication."""
    creds                                                         =                                                         None

    #                                                         Check                                                         if                                                         token.pickle                                                         exists
    if                                                         os.path.exists('token.pickle'):
        with                                                         open('token.pickle',                                                         'rb')                                                         as                                                         token:
            creds                                                         =                                                         pickle.load(token)

    #                                                         If                                                         no                                                         valid                                                         credentials,                                                         authenticate
    if                                                         not                                                         creds                                                         or                                                         not                                                         creds.valid:
        if                                                         creds                                                         and                                                         creds.expired                                                         and                                                         creds.refresh_token:
            creds.refresh(Request())
        else:
            flow                                                         =                                                         InstalledAppFlow.from_client_secrets_file('credentials.json',                                                         SCOPES)
            creds                                                         =                                                         flow.run_local_server(port=0)

        #                                                         Save                                                         credentials                                                         for                                                         next                                                         run
        with                                                         open('token.pickle',                                                         'wb')                                                         as                                                         token:
            pickle.dump(creds,                                                         token)

    return                                                         build('gmail',                                                         'v1',                                                         credentials=creds)

def                                                         get_unread_emails(service,                                                         query='is:unread'):
    """Get                                                         unread                                                         emails                                                         from                                                         Gmail."""
    try:
        results                                                         =                                                         service.users().messages().list(userId='me',
                                                                        q=query,
                                                                        maxResults=10
                                                                        ).execute()
        messages                                                         =                                                         results.get('messages',                                                         [])

        if                                                         not                                                         messages:
            print("No                                                         unread                                                         emails                                                         found.")
            return                                                         []

        email_list                                                         =                                                         []
        for                                                         message                                                         in                                                         messages:
            msg                                                         =                                                         service.users().messages().get(userId='me',
                                                                 id=message['id'],
                                                                 format='full'
                                                                 ).execute()
            email_list.append(msg)

        return                                                         email_list

    except                                                         Exception                                                         as                                                         e:
        print(f"Error                                                         fetching                                                         emails:                                                         {e}")
        return                                                         []

def                                                         parse_email(email):
    """Parse                                                         email                                                         to                                                         extract                                                         subject                                                         and                                                         snippet."""
    try:
        headers                                                         =                                                         email['payload']['headers']
        subject                                                         =                                                         ''
        sender                                                         =                                                         ''

        for                                                         header                                                         in                                                         headers:
            if                                                         header['name']                                                         ==                                                         'Subject':
                subject                                                         =                                                         header['value']
            if                                                         header['name']                                                         ==                                                         'From':
                sender                                                         =                                                         header['value']

        snippet                                                         =                                                         email.get('snippet',                                                         '')

        return                                                         {
            'subject':                                                         subject,
            'sender':                                                         sender,
            'snippet':                                                         snippet,
            'id':                                                         email['id']
        }
    except                                                         Exception                                                         as                                                         e:
        print(f"Error                                                         parsing                                                         email:                                                         {e}")
        return                                                         None

async                                                         def                                                         send_telegram_alert(signal):
    """Send                                                         trading                                                         signal                                                         to                                                         Telegram."""
    print("🔧                                                         Inside                                                         send_telegram_alert                                                         function...")

    try:
        token                                                         =                                                         os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id                                                         =                                                         os.getenv('TELEGRAM_CHAT_ID')

        print(f"Token:                                                         {token[:20]                                                         if                                                         token                                                         else                                                         'None'}...")
        print(f"Chat                                                         ID:                                                         {chat_id}")

        if                                                         not                                                         token                                                         or                                                         not                                                         chat_id:
            print("❌                                                         Missing                                                         Telegram                                                         credentials                                                         in                                                         .env                                                         file!")
            return

        bot                                                         =                                                         Bot(token=token)

        #                                                         Format                                                         the                                                         message
        message                                                         =                                                         f"""
🚨                                                         TRADING                                                         SIGNAL                                                         DETECTED!

📊                                                         Action:                                                         {signal['action']}
💰                                                         Coin:                                                         {signal['coin']}
📧                                                         Subject:                                                         {signal['subject']}
📝                                                         Details:                                                         {signal['snippet'][:200]}

⏰                                                         Detected:                                                         {signal['detected_at']}
        """

        print("📨                                                         Sending                                                         message                                                         to                                                         Telegram...")
        #                                                         Send                                                         to                                                         Telegram
        await                                                         bot.send_message(chat_id=chat_id,                                                         text=message)
        print("✅                                                         Alert                                                         sent                                                         to                                                         Telegram!")

    except                                                         Exception                                                         as                                                         e:
        print(f"❌                                                         Error                                                         sending                                                         to                                                         Telegram:                                                         {e}")
        import                                                         traceback
        traceback.print_exc()

def                                                         detect_trading_signals(emails):
    """Detect                                                         and                                                         parse                                                         trading                                                         signals                                                         from                                                         emails."""
    signals                                                         =                                                         []

    for                                                         email                                                         in                                                         emails:
        parsed                                                         =                                                         parse_email(email)
        if                                                         not                                                         parsed:
            continue

        #                                                         Check                                                         if                                                         subject                                                         contains                                                         "Alert:"
        if                                                         "alert:"                                                         in                                                         parsed['subject'].lower():
            #                                                         Extract                                                         signal                                                         info
            subject                                                         =                                                         parsed['subject']
            words                                                         =                                                         subject.split()

            signal                                                         =                                                         {
                'type':                                                         'TRADING_SIGNAL',
                'sender':                                                         parsed['sender'],
                'subject':                                                         subject,
                'snippet':                                                         parsed['snippet'],
                'detected_at':                                                         'now',
                'action':                                                         None,
                'coin':                                                         None
            }

            #                                                         Try                                                         to                                                         extract                                                         action                                                         and                                                         coin
            for                                                         word                                                         in                                                         words:
                if                                                         word.upper()                                                         in                                                         ['BUY',                                                         'SELL',                                                         'SWING',                                                         'LONG',                                                         'SHORT']:
                    signal['action']                                                         =                                                         word.upper()

                #                                                         Common                                                         crypto                                                         symbols
                if                                                         word.upper()                                                         in                                                         ['BTC',                                                         'ETH',                                                         'ADA',                                                         'SOL',                                                         'DOT',                                                         'LINK',                                                         'XRP']:
                    signal['coin']                                                         =                                                         word.upper()

            signals.append(signal)
            print(f"\n🚨                                                         TRADING                                                         SIGNAL                                                         DETECTED!")
            print(f"Action:                                                         {signal['action']}")
            print(f"Coin:                                                         {signal['coin']}")
            print(f"Subject:                                                         {signal['subject']}")
            print("-"                                                         *                                                         50)

            #                                                         Send                                                         to                                                         Telegram                                                         with                                                         error                                                         handling
            try:
                print("📤                                                         Sending                                                         alert                                                         to                                                         Telegram...")
                asyncio.run(send_telegram_alert(signal))
            except                                                         Exception                                                         as                                                         e:
                print(f"❌                                                         ERROR                                                         sending                                                         to                                                         Telegram:                                                         {e}")
                import                                                         traceback
                traceback.print_exc()

    return                                                         signals

if                                                         __name__                                                         ==                                                         '__main__':
    print("Connecting                                                         to                                                         Gmail...")
    service                                                         =                                                         get_gmail_service()
    print("✅                                                         Connected                                                         to                                                         Gmail!")

    print("\nFetching                                                         unread                                                         emails...")
    emails                                                         =                                                         get_unread_emails(service)
    print(f"\nFound                                                         {len(emails)}                                                         unread                                                         email(s):\n")

    #                                                         Detect                                                         trading                                                         signals
    signals                                                         =                                                         detect_trading_signals(emails)

    #                                                         Show                                                         all                                                         emails                                                         for                                                         debugging
    for                                                         email                                                         in                                                         emails:
        parsed                                                         =                                                         parse_email(email)
        if                                                         parsed:
            print(f"From:                                                         {parsed['sender']}")
            print(f"Subject:                                                         {parsed['subject']}")
            print(f"Snippet:                                                         {parsed['snippet'][:100]}...")
            print("-"                                                         *                                                         50)

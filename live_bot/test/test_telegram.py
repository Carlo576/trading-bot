import                 os
from                 dotenv                 import                 load_dotenv
import                 asyncio
from                 telegram                 import                 Bot

load_dotenv()

async                 def                 test_telegram():
    token                 =                 os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id                 =                 os.getenv('TELEGRAM_CHAT_ID')
    
    print(f"Token:                 {token[:20]}...")                 #                 Show                 first                 20                 chars
    print(f"Chat                 ID:                 {chat_id}")
    
    if                 not                 token                 or                 not                 chat_id:
        print("❌                 Missing                 credentials!")
        return
    
    try:
        bot                 =                 Bot(token=token)
        message                 =                 "🎉                 Test                 message                 from                 your                 trading                 bot!"
        
        await                 bot.send_message(chat_id=chat_id,                 text=message)
        print("✅                 Message                 sent                 successfully!")
        
    except                 Exception                 as                 e:
        print(f"❌                 Error:                 {e}")

if                 __name__                 ==                 '__main__':
    asyncio.run(test_telegram())

import re
import os 
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BankUssdAirtimeCode = {
    "gtbank": "*737*",
    "access": "*901*",
    "zenith": "*966*",
    "uba": "*919*",
    "firstbank": "*894*"
}

BankUssdTransfercode = {
    "gtbank": {"same_bank": "*737*1*", "other_bank": "*737*2*"},  
    "access": {"same_bank": "*901*1*", "other_bank": "*901*2*"},
    "zenith": {"same_bank": "*966*1*", "other_bank": "*966*2*"},
    "uba": {"same_bank": "*919*3*", "other_bank": "*919*4*"},
    "firstbank": {"same_bank": "*894*1*", "other_bank": "*894*2*"} 
}

BANK_SELECTION, AMOUNT_INPUT, RECIPIENT_CHOICE, RECIPIENT_PHONE, \
TRANSFER_TYPE, ACCOUNT_NUMBER, TRANSFER_AMOUNT, DESTINATION_BANK = range(8)

class UserSession:
    def __init__(self):
        self.user_data = {}
    
    def set(self, user_id: int, key: str, value: Any):
        if user_id not in self.user_data:
            self.user_data[user_id] = {}
        self.user_data[user_id][key] = value
    
    def get(self, user_id: int, key: str, default=None):
        if user_id in self.user_data and key in self.user_data[user_id]:
            return self.user_data[user_id][key]
        return default
    
    def clear(self, user_id: int):
        if user_id in self.user_data:
            del self.user_data[user_id]

user_sessions = UserSession()

def AirtimePurchase(bank: str, amount: str, phone_number: Optional[str] = None) -> str:
    """Generate USSD code for airtime purchase"""
    bank = bank.lower()
    if bank not in BankUssdAirtimeCode:
        return "Your bank is not included in the database"
    
    if phone_number is None:
        return f"{BankUssdAirtimeCode[bank]}{amount}#"
    else:
        return f"{BankUssdAirtimeCode[bank]}{amount}*{phone_number}#"

def MoneyTransfer(bank: str, account_number: str, amount: str, destination_bank: str) -> str:
    """Generate USSD code for money transfer"""
    bank = bank.lower()
    if bank not in BankUssdTransfercode:
        return "Your bank is not in the database"
    
    if destination_bank == "same_bank":
        return f"{BankUssdTransfercode[bank]['same_bank']}{account_number}*{amount}#"
    elif destination_bank == "other_bank":
        return f"{BankUssdTransfercode[bank]['other_bank']}{account_number}*{amount}#"
    else:
        return "Invalid transfer type"

def setup_chatbot() -> Optional[LLMChain]:
    """Initialize the LangChain chatbot with error handling"""
    try:
        load_dotenv()
        
        DEEPSEEK_API = os.getenv("DeepSeekApi")
        if not DEEPSEEK_API:
            print("❌ DeepSeekApi not found in environment variables")
            print("Add to .env: DeepSeekApi=your_openrouter_api_key")
            return None
        
        print("🔄 Initializing LangChain with DeepSeek...")
        
    
        
        llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            openai_api_key=DEEPSEEK_API,
            model="deepseek/deepseek-chat",  
            temperature=0.7,
        )
        1
        # Test the connection
        print("✅ LangChain configured. Testing connection...")
        
        memory = ConversationBufferMemory()
        
        prompt = PromptTemplate(
            input_variables=["history", "input"],
            template="""You are a helpful banking assistant for Nigerian banks. 
            Help users with banking questions about airtime purchases, money transfers, 
            account management, and general banking inquiries.
            
            Keep responses clear, concise, and helpful.
            
            Chat history:
            {history}
            
            Human: {input}
            AI: """
        )
        
        chain = LLMChain(llm=llm, prompt=prompt, memory=memory, verbose=False)
        
        # Test with a simple message
        test_response = chain.run(input="Hello")
        print(f"✅ LangChain test successful: {test_response[:50]}...")
        
        return chain
        
    except Exception as e:
        print(f"❌ Failed to initialize LangChain: {e}")
        print("⚠️ Bot will run without AI capabilities")
        return None
try:
    chatbot_chain = setup_chatbot()
except Exception as e:
    print(f"⚠️ Could not initialize AI: {e}")
    chatbot_chain = None

    

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    welcome_text = """
    🏦 Welcome to Banking Assistant Bot!
    
    I can help you with:
    • 💳 Airtime purchase
    • 💰 Money transfers
    • ❓ Banking questions
    
    Available commands:
    /airtime - Buy airtime
    /transfer - Transfer money
    /help - Show this help message
    /cancel - Cancel current operation
    
    Just type your banking questions directly!
    """
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message."""
    help_text = """
    🤖 How to use this bot:
    
    1. For Airtime Purchase:
       - Type /airtime
       - Follow the step-by-step instructions
    
    2. For Money Transfer:
       - Type /transfer
       - Follow the step-by-step instructions
    
    3. For Banking Questions:
       - Just type your question directly!
    
    Commands:
    /start - Start the bot
    /airtime - Buy airtime
    /transfer - Send money
    /cancel - Cancel current operation
    /help - Show this message
    """
    await update.message.reply_text(help_text)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel and end the conversation."""
    user_id = update.effective_user.id
    user_sessions.clear(user_id)
    await update.message.reply_text(
        "Operation cancelled. You can start over with /airtime or /transfer."
    )
    return ConversationHandler.END

async def airtime_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the airtime purchase conversation."""
    user_id = update.effective_user.id
    user_sessions.clear(user_id)  # Clear any previous session
    
    keyboard = [["GTBank", "Access Bank"], ["Zenith Bank", "UBA"], ["First Bank"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        
        "Please select your bank:",
        reply_markup=reply_markup
    )
    return BANK_SELECTION

async def bank_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store selected bank and ask for amount."""
    user_id = update.effective_user.id
    bank = update.message.text.lower().replace(" ", "")
    
    # Map display names to keys
    bank_mapping = {
        "gtbank": "gtbank",
        "accessbank": "access",
        "zenithbank": "zenith",
        "uba": "uba",
        "firstbank": "firstbank"
    }
    
    bank_key = bank_mapping.get(bank)
    if not bank_key:
        await update.message.reply_text("Invalid bank selection. Please try again with /airtime")
        return ConversationHandler.END
    
    user_sessions.set(user_id, "bank", bank_key)
    await update.message.reply_text(
        f"Selected: {update.message.text}\n\n"
        "How much airtime would you like to purchase?\n"
        "Example: 500, 1000, 2000"
    )
    return AMOUNT_INPUT

async def amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store amount and ask who it's for."""
    user_id = update.effective_user.id
    amount = update.message.text.strip()
    
    # Validate amount
    if not amount.isdigit():
        await update.message.reply_text("Please enter a valid amount (numbers only). Try again with /airtime")
        return ConversationHandler.END
    
    user_sessions.set(user_id, "amount", amount)
    
    keyboard = [["For myself (Self)", "For someone else"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"Amount: ₦{amount}\n\n"
        "Who is this airtime for?",
        reply_markup=reply_markup
    )
    return RECIPIENT_CHOICE

async def recipient_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle recipient choice."""
    user_id = update.effective_user.id
    choice = update.message.text.lower()
    
    if "myself" in choice or "self" in choice:
        # Generate USSD code for self
        bank = user_sessions.get(user_id, "bank")
        amount = user_sessions.get(user_id, "amount")
        
        if not bank or not amount:
            await update.message.reply_text("Session error. Please start over with /airtime")
            return ConversationHandler.END
        
        ussd_code = AirtimePurchase(bank, amount)
        user_sessions.clear(user_id)
        
        await update.message.reply_text(

            f"```\n{ussd_code}\n```\n"
            f"Copy and dial this code on your phone.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    
    elif "someone else" in choice or "else" in choice:
        await update.message.reply_text(
            "Please enter the recipient's phone number:\n"
            "Example: 08012345678"
        )
        return RECIPIENT_PHONE
    
    else:
        await update.message.reply_text("Invalid choice. Please try again with /airtime")
        return ConversationHandler.END

async def recipient_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store recipient phone and generate USSD code."""
    user_id = update.effective_user.id
    phone = update.message.text.strip()
    
    # Validate phone number
    if not re.match(r'^0[7-9][0-1]\d{8}$', phone):
        await update.message.reply_text(
            "Invalid phone number format. Please enter a valid Nigerian number.\n"
            "Example: 08012345678\n\n"
            "Try again with /airtime"
        )
        return ConversationHandler.END
    
    bank = user_sessions.get(user_id, "bank")
    amount = user_sessions.get(user_id, "amount")
    
    if not bank or not amount:
        await update.message.reply_text("Session error. Please start over with /airtime")
        return ConversationHandler.END
    
    ussd_code = AirtimePurchase(bank, amount, phone)
    user_sessions.clear(user_id)
    
    await update.message.reply_text(

        f"```\n{ussd_code}\n```\n"
        f"Copy and dial this code on your phone.",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

async def transfer_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the money transfer conversation."""
    user_id = update.effective_user.id
    user_sessions.clear(user_id)
    
    keyboard = [["GTBank", "Access Bank"], ["Zenith Bank", "UBA"], ["First Bank"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "💰 Money Transfer\n\n"
        "Please select your bank:",
        reply_markup=reply_markup
    )
    return BANK_SELECTION

async def transfer_bank_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store bank for transfer and ask for transfer type."""
    user_id = update.effective_user.id
    bank = update.message.text.lower().replace(" ", "")
    
    bank_mapping = {
        "gtbank": "gtbank",
        "accessbank": "access",
        "zenithbank": "zenith",
        "uba": "uba",
        "firstbank": "firstbank"
    }
    
    bank_key = bank_mapping.get(bank)
    if not bank_key:
        await update.message.reply_text("Invalid bank selection. Please try again with /transfer")
        return ConversationHandler.END
    
    user_sessions.set(user_id, "transfer_bank", bank_key)
    
    keyboard = [["Same Bank Transfer", "Other Bank Transfer"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"Selected: {update.message.text}\n\n"
        "What type of transfer?",
        reply_markup=reply_markup
    )
    return TRANSFER_TYPE

async def transfer_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store transfer type and ask for account number."""
    user_id = update.effective_user.id
    transfer_type = update.message.text.lower()
    
    if "same bank" in transfer_type:
        user_sessions.set(user_id, "transfer_type", "same_bank")
    elif "other bank" in transfer_type:
        user_sessions.set(user_id, "transfer_type", "other_bank")
    else:
        await update.message.reply_text("Invalid selection. Please try again with /transfer")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "Please enter the recipient's account number:"
    )
    return ACCOUNT_NUMBER

async def account_number_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store account number and ask for amount."""
    user_id = update.effective_user.id
    account_number = update.message.text.strip()
    
    # Validate account number
    if not account_number.isdigit() or len(account_number) < 10:
        await update.message.reply_text(
            "Invalid account number. Please enter a valid 10-digit account number.\n\n"
            "Try again with /transfer"
        )
        return ConversationHandler.END
    
    user_sessions.set(user_id, "account_number", account_number)
    
    await update.message.reply_text(
        f"Account: {account_number}\n\n"
        "How much would you like to transfer?\n"
        "Example: 1000, 5000, 10000"
    )
    return TRANSFER_AMOUNT

async def transfer_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate and display USSD code for transfer."""
    user_id = update.effective_user.id
    
    bank = user_sessions.get(user_id, "transfer_bank")
    transfer_type = user_sessions.get(user_id, "transfer_type")
    account = user_sessions.get(user_id, "account_number")
    amount = update.message.text.strip()
    
    # Validate amount
    if not amount.isdigit():
        await update.message.reply_text(
            "Invalid amount. Please enter numbers only.\n\n"
            "Try again with /transfer"
        )
        return ConversationHandler.END
    
    # Generate USSD code
    ussd_code = MoneyTransfer(bank, account, amount, transfer_type)
    user_sessions.clear(user_id)
    
    await update.message.reply_text(
      
        f"```\n{ussd_code}\n```\n"
        f"Copy and dial this code on your phone.",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages with the LangChain chatbot."""
    user_message = update.message.text
    print(f"📩 User message: {user_message}")
    
    # Check for banking intents
    if re.search(r'\b(airtime|credit|data|top.up|recharge)\b', user_message.lower()):
        await update.message.reply_text(
            "💳 It looks like you want to buy airtime!\n\n"
            "Use /airtime to start the purchase process."
        )
        return
    
    if re.search(r'\b(transfer|send.money|wire|send.funds)\b', user_message.lower()):
        await update.message.reply_text(
            "💰 It looks like you want to transfer money!\n\n"
            "Use /transfer to start the transfer process."
        )
        return
    
    # Check if chatbot is available
    if not chatbot_chain:
        await update.message.reply_text(
            "🤖 I can help you with banking services!\n\n"
            "• Buy airtime: /airtime\n"
            "• Transfer money: /transfer\n"
            "• For banking questions, I'm currently limited to commands.\n"
            "Need help? Type /help"
        )
        return
    
    # Use LangChain for general banking questions
    try:
        print("🤖 Processing with LangChain...")
        response = chatbot_chain.run(input=user_message)
        print(f"✅ Response generated: {response[:100]}...")
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Error in chatbot: {e}")
        print(f"❌ LangChain error details: {e}")
        
        # Fallback response
        await update.message.reply_text(
            "🤖 Banking Assistant\n\n"
            "I can help you with:\n"
            "• 💳 Buying airtime - type /airtime\n"
            "• 💰 Transferring money - type /transfer\n"
            "• 📋 Banking information - try these commands\n\n"
            "For now, my AI features are temporarily unavailable."
        )

def main():
    """Start the bot."""
    # Load environment variables
    load_dotenv()
    
    # Get Telegram Bot Token from environment
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables!")
        print("Please add it to your .env file:")
        
        return
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Set up Conversation Handlers
    # Airtime Conversation Handler
    airtime_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('airtime', airtime_start)],
        states={
            BANK_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, bank_selected)],
            AMOUNT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_received)],
            RECIPIENT_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, recipient_choice)],
            RECIPIENT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, recipient_phone)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Transfer Conversation Handler
    transfer_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('transfer', transfer_start)],
        states={
            BANK_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, transfer_bank_selected)],
            TRANSFER_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, transfer_type_selected)],
            ACCOUNT_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, account_number_received)],
            TRANSFER_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, transfer_amount_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(airtime_conv_handler)
    application.add_handler(transfer_conv_handler)
    
    # Add message handler for regular messages (MUST BE LAST)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    print("🤖 Banking Assistant Bot is starting...")
    print("Press Ctrl+C to stop")
    
    # Run the bot until Ctrl+C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
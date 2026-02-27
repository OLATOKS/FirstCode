import re
import os 
import json 
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from logging.handlers import RotatingFileHandler
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Set up a formatter to make the logs easy to read
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a rotating file handler (keeps the file from getting too big)
file_handler = RotatingFileHandler(
    'bot_activity.log', maxBytes=5 * 1024 * 1024, backupCount=2 # Max 5MB per file, keep 2 backups
)
file_handler.setFormatter(log_formatter)

# Create a console handler so you still see it in the terminal
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# Configure the root logger
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])
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
TRANSFER_TYPE, ACCOUNT_NUMBER, TRANSFER_AMOUNT, \
CONFIRM_SAVE, GET_BENEFICIARY_NAME, SHORTCUT_AMOUNT = range(10)

# CLICKABLE LINK HELPER ---
def make_ussd_link(ussd):
    """Formats USSD as a clickable phone link"""
    safe_ussd = ussd.replace("#", "%23")
    return f"tel:{safe_ussd}"

# BENEFICIARY STORAGE 
class BeneficiaryManager:
    def __init__(self, filename="beneficiaries.json"):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f: json.dump({}, f)

    def save(self, user_id, name,service_type, data):
        all_data = self.load_all()
        u_id = str(user_id)
        name = name.lower()

        if u_id not in all_data: 
            all_data[u_id] = {}
        if name not in all_data[u_id]:
            all_data[u_id][name] = {"airtime": None, "transfer": None}

        all_data[u_id][name][service_type] = data

        with open(self.filename, 'w') as f:
            json.dump(all_data, f, indent=4)

    def load_all(self):
        try:
            with open(self.filename, 'r') as f: return json.load(f)
        except: return {}

    def get_user_list(self, user_id):
        return self.load_all().get(str(user_id), {})
    
    def delete(self, user_id, name):
        all_data = self.load_all()
        u_id = str(user_id)
        name = name.lower()
        if u_id in all_data and name in all_data[u_id]:
            del all_data[u_id][name]
            with open(self.filename, 'w') as f:
                json.dump(all_data, f, indent=4)
            return True
        return False

beneficiary_mgr = BeneficiaryManager()


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

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Returns the chat history for a specific user session."""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


def setup_chatbot():
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
        
        # Test the connection
        print("✅ LangChain configured. Testing connection...")
        
       # new update langchain Prompt Template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a banking assistant. 
            IMPORTANT: Do NOT give USSD codes or step-by-step transfer instructions. 
            bot handles transactions via /airtime and /transfer.
    
            If the user asks to send money or buy airtime, simply tell them:
            "I can help with that! Please use /transfer or /airtime to begin."
    
            Only answer general questions like "What is a BVN?" or "How do I keep my account safe?\""""),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        # Modern LCEL Chain Pipe
        chain = prompt | llm

        # the memory with the new module 
        with_message_history = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

        # Test the connection
        print("Testing connection...")
        test_response = with_message_history.invoke(
            {"input": "Hello"},
            config={"configurable": {"session_id": "test_session"}}
        )
        print(f"✅ LangChain test successful: {test_response.content[:50]}...")
        
        return with_message_history
        
    except Exception as e:
        print(f"❌ Failed to initialize LangChain: {e}")
        print("⚠️ Bot will run without AI capabilities")
        return None
try:
    chatbot_chain = setup_chatbot()
except Exception as e:
    print(f"⚠️ Could not initialize AI: {e}")
    chatbot_chain = None

 # REUSABLE FINAL STEP (The "Connected" Link Logic) 
async def show_ussd_and_prompt_save(update: Update, ussd_code: str):
    uid = update.effective_user.id
    # Use the make_ussd_link here!
    dial_link = make_ussd_link(ussd_code)
    
    await update.message.reply_text(
        f"Your USSD Code is:"
        f"`{ussd_code}`\n\n"
        f"📲 [Click here to Dial]({dial_link})",
        parse_mode="Markdown"
    )
    
    keyboard = [["Yes, Save Beneficiary", "No, thanks"]]
    await update.message.reply_text("Would you like to save this person for future shortcuts?", 
                                   reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    return CONFIRM_SAVE   

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
    /manage - View or delete saved people 
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
    
    4. To see list of beneficaries and also delete from list
       - type /manage 
    
    Commands:
    /start - Start the bot
    /airtime - Buy airtime
    /transfer - Send money
    /cancel - Cancel current operation
    /help - Show this message
    /manage - to show list of benefiacry 
    """
    await update.message.reply_text(help_text)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel and end the conversation."""
    user_id = update.effective_user.id
    user_sessions.clear(user_id)
    await update.message.reply_text(
        "Operation cancelled. You can start over with /airtime or /transfer."
    )
    await send_ready_prompt(update)
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
    bank = update.message.text.lower().replace(" ", "").replace("bank", "")
    
    print(f"🏦 User {user_id} selected bank: {bank}")
    
    # Map display names to keys
    bank_mapping = {
        "gt": "gtbank",
        "gtb": "gtbank",
        "gtbank": "gtbank",
        "access": "access",
        "zenith": "zenith",
        "uba": "uba",
        "first": "firstbank",
        "firstbank": "firstbank"
    }
    
    bank_key = bank_mapping.get(bank)
    if not bank_key:
        await update.message.reply_text("I didn't recognize that bank. Please tap one of the buttons below.")
        return BANK_SELECTION
    
    
    user_sessions.set(user_id, "bank", bank_key)
    await update.message.reply_text(
        
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
    
    user_sessions.set(user_id, "phone", phone) # Save phone to session for saving later
    bank = user_sessions.get(user_id, "bank")
    amount = user_sessions.get(user_id, "amount")
    
    if not bank or not amount:
        await update.message.reply_text("Session error. Please start over with /airtime")
        return ConversationHandler.END
    
    ussd_code = AirtimePurchase(bank, amount, phone)
    # This triggers the clickable link and the "Save?" prompt
    return await show_ussd_and_prompt_save(update, ussd_code)
    

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
    amount: str = update.message.text.strip()

    # Validate amount
    if not amount.isdigit():
        await update.message.reply_text(
            "Invalid amount. Please enter numbers only.\n\n"
            "Try again with /transfer"
        )
        return ConversationHandler.END

    bank = user_sessions.get(user_id, "transfer_bank")
    transfer_type = user_sessions.get(user_id, "transfer_type")
    account = user_sessions.get(user_id, "account_number")
    user_sessions.set(user_id, "amount", amount)

    ussd_code = MoneyTransfer(bank, account, amount, transfer_type)
    # This triggers the clickable link and the "Save?" prompt
    return await show_ussd_and_prompt_save(update, ussd_code)
    

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages with the LangChain chatbot."""
    user_message = update.message.text.lower()
    user_id = update.effective_user.id
    logger.info(f"📩 User message: {user_message}")

    is_airtime_request = any(word in user_message for word in ["airtime", "credit", "top up", "recharge"])
    is_transfer_request = any(word in user_message for word in ["transfer", "send", "pay", "wire"])

    if user_message.startswith('/'):
        return
    
    # Check if they are talking about a saved beneficiary first
    beneficiaries = beneficiary_mgr.get_user_list(user_id)
    for name, services in beneficiaries.items():
        if name in user_message:
            if is_airtime_request:
                if services.get("airtime"):
                    user_sessions.set(user_id, "active_shortcut", services["airtime"])
                    user_sessions.set(user_id, "shortcut_type", "airtime") # Track intent!
                    await update.message.reply_text(f"🎯 Airtime for **{name.capitalize()}**! Amount?")
                    return SHORTCUT_AMOUNT
                else:
                    await update.message.reply_text(f"I have {name.capitalize()}'s transfer info, but no phone number for airtime.")
                    return ConversationHandler.END

            elif is_transfer_request:
                if services.get("transfer"):
                    user_sessions.set(user_id, "active_shortcut", services["transfer"])
                    user_sessions.set(user_id, "shortcut_type", "transfer") # Track intent!
                    await update.message.reply_text(f"🎯 Transfer to **{name.capitalize()}**! Amount?")
                    return SHORTCUT_AMOUNT
                else:
                    await update.message.reply_text(f"I have {name.capitalize()}'s phone number, but no bank details for a transfer.")
                    return ConversationHandler.END
    
    # Check for banking intents
    if re.search(r'\b(airtime|credit|data|top.up|recharge)\b', user_message.lower()):
        await update.message.reply_text(
            "💳 It looks like you want to buy airtime!\n\n"
            "Use /airtime to start the purchase process."
        )
        return ConversationHandler.END
    
    if re.search(r'\b(transfer|send.money|wire|send.funds)\b', user_message.lower()):
        await update.message.reply_text(
            "💰 It looks like you want to transfer money!\n\n"
            "Use /transfer to start the transfer process."
        )
        return ConversationHandler.END
    
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

        # Use .invoke() and pass the user's ID so it remembers their specific conversation
        response = chatbot_chain.invoke(
            {"input": user_message},
            config={"configurable": {"session_id": str(user_id)}}
        )

        # Extract the text from the AI
        bot_reply = response.content

        # Log the response so you can see it on Render
        logger.info(f"🤖 Bot response: {bot_reply}")

        # Send it back to the Telegram user
        await update.message.reply_text(bot_reply)

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
       
    
async def handle_save_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "yes" in update.message.text.lower():
        await update.message.reply_text("What name should I save this as? (e.g., Lekan)", reply_markup=ReplyKeyboardRemove())
        return GET_BENEFICIARY_NAME
    await update.message.reply_text("Transaction finished!", reply_markup=ReplyKeyboardRemove())
    user_sessions.clear(update.effective_user.id)
    return ConversationHandler.END

async def handle_save_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    name = update.message.text.strip().lower()
    

    # Determine what we are saving right now
    if user_sessions.get(uid, "bank") and user_sessions.get(uid, "phone"):
        service_type = "airtime"
        data = {
            "bank": user_sessions.get(uid, "bank"),
            "phone": user_sessions.get(uid, "phone")
        }
    else:
        service_type = "transfer"
        data = {
            "bank": user_sessions.get(uid, "transfer_bank"),
            "account_number": user_sessions.get(uid, "account_number"),
            "transfer_type": user_sessions.get(uid, "transfer_type")
        }
    beneficiary_mgr.save(uid, name, service_type, data)
    
    await update.message.reply_text(
        f"✅ **{name.capitalize()} saved!**\n\n"
        f"You can now say 'Transfer to {name}' anytime.\n"
        f"💡 *Tip: Type /manage to see your list or delete names.*",
        parse_mode="Markdown"
    )
    await send_ready_prompt(update)
    user_sessions.clear(uid)
    return ConversationHandler.END
 
async def shortcut_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    amount = update.message.text.strip()

    if not amount.isdigit():
        await update.message.reply_text(
            "⚠️ **Numbers only, please!**\n"
            "I can't process words as an amount. How much would you like to send? (e.g., 2000)",
            parse_mode="Markdown"
        )
        return SHORTCUT_AMOUNT # Keep them in this state until they give a number

    data = user_sessions.get(uid, "active_shortcut")
    s_type = user_sessions.get(uid, "shortcut_type") # This is key!
    
    if s_type == 'airtime':
        ussd = AirtimePurchase(data['bank'], amount, data['phone'])
    else:
        ussd = MoneyTransfer(data['bank'], data['account_number'], amount, data['transfer_type'])
    
    dial_link = make_ussd_link(ussd)
    await update.message.reply_text(
        f"✅ **USSD Ready!**\n\n"
        f"Tap to copy:\n`{ussd}`\n\n"
        f"📲 [Attempt to Dial]({dial_link})",
        parse_mode="Markdown"
    )
    user_sessions.clear(uid)
    return ConversationHandler.END

async def manage_beneficiaries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    beneficiaries = beneficiary_mgr.get_user_list(uid)
    
    if not beneficiaries:
        await update.message.reply_text("You don't have any saved beneficiaries yet.")
        return

    message = "📋 **Your Saved Beneficiaries:**\n\n"
    for name, services in beneficiaries.items():
        details = []
        if services.get("airtime"): details.append("📱 Airtime")
        if services.get("transfer"): details.append("💰 Transfer")
        message += f"• **{name.capitalize()}** ({', '.join(details)})\n"
    
    message += "\nTo delete someone, type: `delete [name]` (e.g., `delete babe`)"
    await update.message.reply_text(message, parse_mode="Markdown")

async def handle_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()
    if user_message.startswith("delete "):
        name_to_delete = user_message.replace("delete ", "").strip()
        uid = update.effective_user.id
        
        if beneficiary_mgr.delete(uid, name_to_delete):
            await update.message.reply_text(f"🗑️ Deleted **{name_to_delete.capitalize()}** from your list.", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❓ I couldn't find anyone named '{name_to_delete}'")

async def send_ready_prompt(update: Update):
    """Call this whenever a transaction or cancel ends."""
    text = (
        "✅ **Task complete.**\n\n"
        "How can I help you next?\n"
        "• Type a question (e.g., 'What is a BVN?')\n"
        "• Use a shortcut (e.g., 'Transfer to Bro')\n"
        "• Use a command: /airtime, /transfer, or /manage"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

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
    
      # --- RENDER WEB SERVER START ---

    class HealthCheckHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is Healthy!")

    def run_health_server():
    # Render provides the port in an environment variable called 'PORT'
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        server.serve_forever()

    # Start the web server in a background thread
    threading.Thread(target=run_health_server, daemon=True).start()
    # render ends here 
    
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
            # ADD THESE:
            CONFIRM_SAVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_save_decision)],
            GET_BENEFICIARY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_save_name)],
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
            # These MUST be here for transfers to save beneficiaries too!
            CONFIRM_SAVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_save_decision)],
            GET_BENEFICIARY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_save_name)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    shortcut_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        states={
            SHORTCUT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, shortcut_amount_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=False

    )
   
    
    
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(airtime_conv_handler) # High priority
    application.add_handler(transfer_conv_handler) # High priority
    application.add_handler(MessageHandler(filters.Regex(r'^delete\s.+'), handle_delete))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(shortcut_handler)      # Medium priority (handles AI + Shortcuts)
    application.add_handler(CommandHandler("manage", manage_beneficiaries)) # Add a message handler specifically for the 'delete' keyword
    


    
    # Start the bot
    print("🤖 Banking Assistant Bot is starting...")
    print("Press Ctrl+C to stop")
    
    # Run the bot until Ctrl+C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
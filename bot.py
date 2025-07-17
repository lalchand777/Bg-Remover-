import os
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# Configuration
BOT_TOKEN = "8101659803:AAE-sfiJslz42k9w8h8VUpe1lJFPW57aQG0"
REMOVEBG_API_KEY = "5CpdEqT1KkdSrQR2pwRxQVqm"
CHANNEL_LINK = "https://t.me/imagebgremover"
CHANNEL_USERNAME = "@imagebgremover"

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    try:
        chat_member = context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            update.message.reply_text("🌟 Welcome! Send me any image to remove its background.")
        else:
            show_join_button(update)
    except Exception as e:
        update.message.reply_text("⚠️ Error checking channel membership. Please try again.")

def show_join_button(update: Update):
    keyboard = [[InlineKeyboardButton("👉 Join Channel", url=CHANNEL_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "📢 Please join our channel first to use this bot:",
        reply_markup=reply_markup
    )

def handle_join_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    try:
        chat_member = context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            query.answer("✅ Access granted! Send me an image now.")
            query.edit_message_text("🎉 Thank you for joining! Send me any image to remove its background.")
        else:
            query.answer("❌ You haven't joined yet!", show_alert=True)
    except Exception as e:
        query.answer("⚠️ Verification failed. Try again.", show_alert=True)

def handle_image(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    try:
        chat_member = context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if chat_member.status not in ['member', 'administrator', 'creator']:
            show_join_button(update)
            return
            
        photo = update.message.photo[-1]
        file = context.bot.get_file(photo.file_id)
        
        update.message.reply_text("🔄 Processing your image...")
        
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': requests.get(file.file_path).content},
            data={'size': 'auto'},
            headers={'X-Api-Key': REMOVEBG_API_KEY},
        )
        
        if response.status_code == 200:
            update.message.reply_photo(
                photo=response.content,
                caption="✅ Background removed successfully!"
            )
        else:
            update.message.reply_text(f"❌ Error: {response.text}")
            
    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {str(e)}")

def main():
    # Replit webhook setup
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(handle_join_callback))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))
    
    # Webhook configuration for Replit
    repl_url = os.getenv('REPLIT_URL')  # Get your Replit project URL
    if repl_url:
        updater.start_webhook(
            listen="0.0.0.0",
            port=8080,
            url_path=BOT_TOKEN,
            webhook_url=f"{repl_url}/{BOT_TOKEN}"
        )
    else:
        updater.start_polling()
    
    updater.idle()

if __name__ == '__main__':
    main()

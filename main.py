import os
import re
import telebot
import qrcode
from io import BytesIO

# Fetch the bot token from Railway Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN provided. Please set it in Railway environment variables.")

bot = telebot.TeleBot(BOT_TOKEN)

def format_url(text):
    """
    Formats the text to ensure it acts as a clickable link when scanned.
    Adds https:// if the user just sends 'example.com'
    """
    text = text.strip()
    if text.startswith(('http://', 'https://')):
        return text
    # Regex to check if the text looks like a domain (e.g., domain.com, sub.domain.org/path)
    if re.match(r'^([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/.*)?$', text):
        return f"https://{text}"
    return text # Returns plain text if it's not a URL

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 Welcome! I am a QR Code Generator Bot.\n\n"
        "Send me any link (e.g., `https://google.com`, `http://example.com`, or just `example.com`) "
        "and I will instantly reply with a QR code."
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def generate_qr(message):
    try:
        # Format the URL properly
        data_to_encode = format_url(message.text)
        
        # Create QR code object
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data_to_encode)
        qr.make(fit=True)

        # Generate image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save image to memory (BytesIO) instead of the hard drive
        bio = BytesIO()
        bio.name = 'qrcode.png'
        img.save(bio, 'PNG')
        bio.seek(0)
        
        # Send the photo back to the user
        bot.send_photo(
            message.chat.id, 
            photo=bio, 
            caption=f"Here is your QR Code for:\n{data_to_encode}"
        )
        
    except Exception as e:
        bot.reply_to(message, "❌ Sorry, something went wrong while generating the QR code.")
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()

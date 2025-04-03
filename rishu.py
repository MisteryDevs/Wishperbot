from pyrogram import Client, filters from pyrogram.types import ( InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton, Message ) import random from flask import Flask from threading import Thread from config import API_ID, API_HASH, BOT_TOKEN

app = Client( "WhisperBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN )

flask_app = Flask(name)

RANDOM_IMAGES = [ "https://files.catbox.moe/enzetg.jpg", "https://files.catbox.moe/lc46od.jpg", "https://files.catbox.moe/ee82s3.jpg", "https://files.catbox.moe/jygtws.jpg", "https://files.catbox.moe/gflfk1.jpg", "https://files.catbox.moe/6ppfre.jpg", "https://files.catbox.moe/sdtyi7.jpg", "https://files.catbox.moe/izkc8z.jpg" ]

whisper_db = {}

async def get_bot_username(): me = await app.get_me() return me.username

@app.on_message(filters.command("start") & filters.private) async def start_message(_, message: Message): bot_username = await get_bot_username() welcome_text = ( "✨ Welcome to Whisper Bot! ✨\n\n" "🌟 About This Bot:\n" "This bot allows you to send secret whispers to other users." ) random_image = random.choice(RANDOM_IMAGES) await message.reply_photo( photo=random_image, caption=welcome_text, reply_markup=InlineKeyboardMarkup( [[InlineKeyboardButton("💒 Start Whisper", switch_inline_query="")]] ) )

@app.on_inline_query() async def bot_inline(_, inline_query): string = inline_query.query.lower() if string.strip() == "": bot_username = await get_bot_username() answers = [ InlineQueryResultArticle( title="💒 Whisper", description=f"@{bot_username} [USERNAME | ID] [TEXT]", input_message_content=InputTextMessageContent( f"📍Usage:\n\n@{bot_username} (USERNAME or ID) (Your Message)" ), reply_markup=InlineKeyboardMarkup( [[InlineKeyboardButton("💒 Start Whisper", switch_inline_query="")]] ) ) ] await inline_query.answer(answers)

@flask_app.route('/') def home(): return "Whisper Bot is Running!"

def run_flask(): flask_app.run(host='0.0.0.0', port=8080)

if name == "main": Thread(target=run_flask).start() app.run()


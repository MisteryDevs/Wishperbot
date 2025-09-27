from pyrogram import Client, filters
from pyrogram.types import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton, Message
)
from pymongo import MongoClient
from pyrogram.errors import UserNotParticipant
import random 
import asyncio
import os
from flask import Flask 
from threading import Thread 

from config import API_ID, API_HASH, BOT_TOKEN

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "whisperbot")
users_col = db["users"]

client = MongoClient(MONGO_URI)

OWNER_ID = int(os.getenv("OWNER_ID", 5738579437))

FORCE_JOIN1 = os.getenv("FORCE_JOIN1")
FORCE_JOIN2 = os.getenv("FORCE_JOIN2")

app = Client( "WhisperBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN )

flask_app = Flask(__name__)


whisper_db = {}

async def get_bot_username():
    me = await app.get_me()
    return me.username

async def is_admin(client, chat_id, user_id):
    async for member in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if member.user.id == user_id:
            return True
    return False

# New User Notification
STICKERS = [
    "CAACAgUAAxkBAAENygdnrrSuukBGTLd_k2q-kPf80pPMqgAClw0AAmdr-Fcu4b8ZzcizqDYE",
    "CAACAgUAAxkBAAENygtnrrVXr5zEE-h_eiG8lRUkRkMwfwACExMAAjRk6VbUUzZjByHDfzYE",
    "CAACAgUAAxkBAAEN5DBnvSPr9qQMqsdEnDDRP-imKi5dQQACLhMAAuC0gFVXNUFTYLnPgzYE",

"CAACAgUAAxkBAAEN5DFnvSPrXLlJIqpci9G9DLlYo-N9sQAC7xYAAmNogVVdydtoPbvZ3DYE",

"CAACAgUAAxkBAAEN5DJnvSPrBKiEnBsXYV-cPA0NNFPWxAAC9xEAAleLgFUHZXfeMQ2XIjYE",

"CAACAgUAAxkBAAEN5DtnvSjlPXpQ9p4e7NnjcQ8u9D02ZgACmxQAAq38gVVMR2r-x8yK7jYE",

"CAACAgUAAxkBAAEN5D1nvSjrBVYlBio74f8n2CDj_I0sEwACixYAAotv6VVIuORutfwQczYE",

"CAACAgUAAxkBAAEN5D9nvSjuUsbAf8LQ1KaU5PsfR3CJcwACmhEAAqFq6FUaXZOdkV85bDYE",

"CAACAgUAAxkBAAEN5EFnvSj0My9zoTWkmtIiL8D6vOReAAO_EQACvC_pVfIqri8bdMRBNgQ",

"CAACAgUAAxkBAAEN5ENnvSj6VnxialvLOmfRL7yZx-Q9HgACbhQAAhfA8FWBN9ZyZA5LuTYE",

"CAACAgUAAxkBAAEN5EVnvSkQhPZHx-aPu_79kWLtFKCnYwACAREAArvxgVUYx9DFORkVmjYE",

"CAACAgUAAxkBAAEN5EdnvSkak4zQxNnvMO76ZVlsXQhz7AACJhQAAoWcgVVYjdtsjmF0czYE"
]

# Random Images
RANDOM_IMAGES = [
            "https://graph.org/file/f76fd86d1936d45a63c64.jpg",
        "https://graph.org/file/69ba894371860cd22d92e.jpg",
        "https://graph.org/file/67fde88d8c3aa8327d363.jpg",
        "https://graph.org/file/3a400f1f32fc381913061.jpg",
        "https://graph.org/file/a0893f3a1e6777f6de821.jpg",
        "https://graph.org/file/5a285fc0124657c7b7a0b.jpg",
        "https://graph.org/file/25e215c4602b241b66829.jpg",
        "https://graph.org/file/a13e9733afdad69720d67.jpg",
        "https://graph.org/file/692e89f8fe20554e7a139.jpg",
        "https://graph.org/file/db277a7810a3f65d92f22.jpg",
        "https://graph.org/file/a00f89c5aa75735896e0f.jpg",
        "https://graph.org/file/f86b71018196c5cfe7344.jpg",
        "https://graph.org/file/a3db9af88f25bb1b99325.jpg",
        "https://graph.org/file/5b344a55f3d5199b63fa5.jpg",
        "https://graph.org/file/84de4b440300297a8ecb3.jpg",
        "https://graph.org/file/84e84ff778b045879d24f.jpg",
        "https://graph.org/file/a4a8f0e5c0e6b18249ffc.jpg",
        "https://graph.org/file/ed92cada78099c9c3a4f7.jpg",
        "https://graph.org/file/d6360613d0fa7a9d2f90b.jpg",
        "https://graph.org/file/37248e7bdff70c662a702.jpg",
        "https://graph.org/file/0bfe29d15e918917d1305.jpg",
        "https://graph.org/file/16b1a2828cc507f8048bd.jpg",
        "https://graph.org/file/e6b01f23f2871e128dad8.jpg",
        "https://graph.org/file/cacbdddee77784d9ed2b7.jpg",
        "https://graph.org/file/ddc5d6ec1c33276507b19.jpg",
        "https://graph.org/file/39d7277189360d2c85b62.jpg",
        "https://graph.org/file/5846b9214eaf12c3ed100.jpg",
        "https://graph.org/file/ad4f9beb4d526e6615e18.jpg",
        "https://graph.org/file/3514efaabe774e4f181f2.jpg",
]

async def check_force_join(user_id):
    """Check if the user is a member of both required channels."""
    try:
        await app.get_chat_member(FORCE_JOIN1, user_id)
        await app.get_chat_member(FORCE_JOIN2, user_id)
        return True
    except UserNotParticipant:
        return False
    except RPCError as e:
        logging.warning(f"Error checking force join for {user_id}: {e}")
        return False

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    user = message.from_user
    user_id = user.id
    username = f"@{user.username}" if user.username else "No Username"

    # Force join check
    if not await check_force_join(user_id):
        return await message.reply_text(
            "**❌ You must join our channels first!**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🍬 Join 🍬", url=f"https://t.me/{FORCE_JOIN1}")],
                [InlineKeyboardButton("🍬 Join 🍬", url=f"https://t.me/{FORCE_JOIN2}")]
            ])
        )

    # Start Progress Animation
    baby = await message.reply_text("[□□□□□□□□□□] 0%")
    progress = [
        "[■□□□□□□□□□] 10%", "[■■□□□□□□□□] 20%", "[■■■□□□□□□□] 30%",
        "[■■■■□□□□□□] 40%", "[■■■■■□□□□□] 50%", "[■■■■■■□□□□] 60%",
        "[■■■■■■■□□□] 70%", "[■■■■■■■■□□] 80%", "[■■■■■■■■■□] 90%",
        "[■■■■■■■■■■] 100%"
    ]
    for step in progress:
        await baby.edit_text(f"**{step}**")
        await asyncio.sleep(0.2)

    await baby.edit_text("**❖ Jᴀʏ Sʜʀᴇᴇ Rᴀᴍ 🚩...**")
    await asyncio.sleep(2)

    # Send a Random Sticker
    try:
        random_sticker = random.choice(STICKERS)
        sticker_msg = await message.reply_sticker(random_sticker)
        await asyncio.sleep(2)
        await sticker_msg.delete()
    except Exception as e:
        print(f"Sticker send failed: {e}")

    await asyncio.sleep(1)

    # Delete progress message
    try:
        await baby.delete()
    except Exception as e:
        print(f"Failed to delete progress message: {e}")

    # MongoDB Check & Insert New User
    try:
        existing_user = users_col.find_one({"_id": user_id})
        if not existing_user:
            users_col.insert_one({"_id": user_id, "username": user.username})
            total_users = users_col.count_documents({})
            # Send Notification to Owner
            await app.send_message(
                OWNER_ID, 
                f"**New User Alert!**\n👤 **User:** {user.mention}\n"
                f"🆔 **ID:** `{user_id}`\n📛 **Username:** {username}\n"
                f"📊 **Total Users:** `{total_users}`"
            )
    except Exception as e:
        print(f"MongoDB Error: {e}")

    # Send a Random Image
    random_image = random.choice(RANDOM_IMAGES)
    await message.reply_photo(
        photo=random_image,
        caption=f"""**┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼──────•
┆✦ » ʜᴇʏ {user.mention}
└──────────────────────•

✦ »  ɪ'ᴍ ᴀ ᴀᴅᴠᴀɴᴄᴇ ᴡɪsʜᴘᴇʀ ᴍᴇssᴀɢᴇ ʙᴏᴛ .

✦ » ғᴀsᴛ ᴀɴᴅ sᴇᴄᴜʀᴇ ᴡɪsʜᴘᴇʀ ᴍᴇssᴀɢᴇ ʙᴏᴛ ᴡɪᴛʜ ɴᴏ ᴀᴅs

✦ » ᴜsᴇ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ sᴇᴇ ᴍʏ ᴘᴏᴡᴇʀ.

•──────────────────────•
❖ 𝐏ᴏᴡᴇʀᴇᴅ ʙʏ  ➪  [˹ ʀɪsʜυ ʙσᴛ ˼](https://t.me/Ur_rishu_143)
•──────────────────────•**""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙", url=f"https://t.me/{client.me.username}?startgroup=true")],
            [InlineKeyboardButton("˹ sυᴘᴘσʀᴛ ˼", url="http://t.me/Ur_support07"),
             InlineKeyboardButton("˹ υᴘᴅᴧᴛєs ˼", url="http://t.me/ur_rishu_143")],
            [InlineKeyboardButton("˹ ᴧʟʟ ʙσᴛ's ˼", url="https://t.me/Vip_robotz"),
             InlineKeyboardButton("˹ ᴄʜᴀᴛʙᴏᴛ ˼", url="https://t.me/DikshaChatBot")],
            [InlineKeyboardButton("💒 sᴛᴀʀᴛ ᴡʜɪsᴘᴇʀ", switch_inline_query="")]
        ])
    )

async def _whisper(_, inline_query):
    data = inline_query.query
    results = []
    bot_username = await get_bot_username()  # Fetch the bot's username

    if len(data.split()) < 2:
        mm = [
            InlineQueryResultArticle(
                title="💒 ᴡʜɪsᴘᴇʀ",
                description=f"@{bot_username} [ USERNAME | ID ] [ TEXT ]",
                input_message_content=InputTextMessageContent(f"💒 Usage:\n\n@{bot_username} [ USERNAME | ID ] [ TEXT ]"),
                thumb_url="https://graph.org/file/19df4696f3bc720d48f1e-398099f9d613749dd1.jpg",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("💒 sᴛᴀʀᴛ ᴡʜɪsᴘᴇʀ", switch_inline_query="")]]
                )
            )
        ]
    else:
        try:
            user_id = data.split()[0]
            msg = data.split(None, 1)[1]
        except IndexError as e:
            pass

        try:
            user = await app.get_users(user_id)
        except:
            mm = [
                InlineQueryResultArticle(
                    title="💒 ᴡʜɪsᴘᴇʀ",
                    description="ɪɴᴠᴀʟɪᴅ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ!",
                    input_message_content=InputTextMessageContent("ɪɴᴠᴀʟɪᴅ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ!"),
                    thumb_url="https://graph.org/file/19df4696f3bc720d48f1e-398099f9d613749dd1.jpg",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("💒 sᴛᴀʀᴛ ᴡʜɪsᴘᴇʀ", switch_inline_query="")]]
                    )
                )
            ]

        try:
            whisper_btn = InlineKeyboardMarkup([[InlineKeyboardButton("💒 ᴡʜɪsᴘᴇʀ", callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}")]])
            one_time_whisper_btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔩 ᴏɴᴇ-ᴛɪᴍᴇ ᴡʜɪsᴘᴇʀ", callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}_one")]])
            mm = [
                InlineQueryResultArticle(
                    title="💒 �ᴡʜɪsᴘᴇʀ",
                    description=f"sᴇɴᴅ ᴀ ᴡʜɪsᴘᴇʀ ᴛᴏ @{user.username}" if user.username else f"sᴇɴᴅ ᴀ ᴡʜɪsᴘᴇʀ ᴛᴏ {user.first_name}",
                    input_message_content=InputTextMessageContent(f"💒 ʏᴏᴜ ᴀʀᴇ sᴇɴᴅɪɴɢ ᴀ ᴡʜɪsᴘᴇʀ ᴛᴏ @{user.username}" if user.username else f"sᴇɴᴅ ᴀ ᴡʜɪsᴘᴇʀ ᴛᴏ {user.first_name}.\n\nᴛʏᴘᴇ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ/sᴇɴᴛᴇɴᴄᴇ."),
                    thumb_url="https://graph.org/file/19df4696f3bc720d48f1e-398099f9d613749dd1.jpg",
                    reply_markup=whisper_btn
                ),
                InlineQueryResultArticle(
                    title="🔩 ᴏɴᴇ-ᴛɪᴍᴇ ᴡʜɪsᴘᴇʀ",
                    description=f"sᴇɴᴅ ᴀ ᴡʜɪsᴘᴇʀ ᴛᴏ @{user.username}" if user.username else f"sᴇɴᴅ ᴀ ᴡʜɪsᴘᴇʀ ᴛᴏ {user.first_name}",
                    input_message_content=InputTextMessageContent(f"🔩 ʏᴏᴜ ᴀʀᴇ sᴇɴᴅɪɴɢ ᴀ ᴏɴᴇ-ᴛɪᴍᴇ ᴡʜɪsᴘᴇʀ ᴛᴏ @{user.username}" if user.username else f"sᴇɴᴅ ᴀ ᴡʜɪsᴘᴇʀ ᴛᴏ {user.first_name}.\n\nᴛʏᴘᴇ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ/sᴇɴᴛᴇɴᴄᴇ."),
                    thumb_url="https://graph.org/file/19df4696f3bc720d48f1e-398099f9d613749dd1.jpg",
                    reply_markup=one_time_whisper_btn
                )
            ]
        except:
            pass

        try:
            whisper_db[f"{inline_query.from_user.id}_{user.id}"] = msg
        except:
            pass

    results.append(mm)
    return results


@app.on_callback_query(filters.regex(pattern=r"fdaywhisper_(.*)"))
async def whispes_cb(_, query):
    data = query.data.split("_")
    from_user = int(data[1])
    to_user = int(data[2])
    user_id = query.from_user.id

    if user_id not in [from_user, to_user, 5738579437]:
        try:
            await app.send_message(from_user, f"{query.from_user.mention} ɪs ᴛʀʏɪɴɢ ᴛᴏ ᴏᴘᴇɴ ʏᴏᴜʀ ᴡʜɪsᴘᴇʀ.")
        except:
            pass

        return await query.answer("ᴛʜɪs ᴡʜɪsᴘᴇʀ ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ 🚧", show_alert=True)

    search_msg = f"{from_user}_{to_user}"

    try:
        msg = whisper_db[search_msg]
    except:
        msg = "🚫 ᴇʀʀᴏʀ!\n\nᴡʜɪsᴘᴇʀ ʜᴀs ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ!"

    SWITCH = InlineKeyboardMarkup([[InlineKeyboardButton("ɢᴏ ɪɴʟɪɴᴇ 🪝", switch_inline_query="")]])

    await query.answer(msg, show_alert=True)

    if len(data) > 3 and data[3] == "one":
        if user_id == to_user:
            await query.edit_message_text("📬 ᴡʜɪsᴘᴇʀ ʜᴀs ʙᴇᴇɴ ʀᴇᴀᴅ!\n\nᴘʀᴇss ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ sᴇɴᴅ ᴀ ᴡʜɪsᴘᴇʀ!", reply_markup=SWITCH)


async def in_help():
    bot_username = await get_bot_username()  # Fetch the bot's username
    answers = [
        InlineQueryResultArticle(
            title="💒 ᴡʜɪsᴘᴇʀ",
            description=f"@{bot_username} [USERNAME | ID] [TEXT]",
            input_message_content=InputTextMessageContent(f"**📍ᴜsᴀɢᴇ:**\n\n@{bot_username} (ᴛᴀʀɢᴇᴛ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ) (ʏᴏᴜʀ ᴍᴇssᴀɢᴇ).\n\n**ᴇxᴀᴍᴘʟᴇ:**\n@{bot_username} @username I Love You"),
            thumb_url="https://graph.org/file/19df4696f3bc720d48f1e-398099f9d613749dd1.jpg",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("💒 sᴛᴀʀᴛ ᴡʜɪsᴘᴇʀ", switch_inline_query="")]]
            )
        )
    ]
    return answers


@app.on_inline_query()
async def bot_inline(_, inline_query):
    string = inline_query.query.lower()

    if string.strip() == "":
        answers = await in_help()
        await inline_query.answer(answers)
    else:
        answers = await _whisper(_, inline_query)
        await inline_query.answer(answers[-1], cache_time=0)

@flask_app.route('/')
def home():
    return "Whisper Bot is Running!"

def run_flask(): flask_app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    app.run()


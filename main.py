import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from yt_dlp import YoutubeDL

print("\n" + "="*50)
print("🔐 ENTER YOUR CREDENTIALS")
print("="*50)

API_ID = int(input("API_ID: "))
API_HASH = input("API_HASH: ")
BOT_TOKEN = input("BOT_TOKEN: ")
SESSION = input("SESSION: ")

bot = Client("MusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("UserBot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
vc = PyTgCalls(userbot)

song_queue = {}

def get_queue(chat_id):
    if chat_id not in song_queue:
        song_queue[chat_id] = []
    return song_queue[chat_id]

@bot.on_message(filters.command("start"))
async def start_cmd(_, message):
    await message.reply_text(
        "🎵 **MUSIC BOT**\n\n"
        "/play <song> - Play music\n"
        "/stop - Stop playing\n"
        "/skip - Skip song\n"
        "/queue - Show queue\n"
        "/pause - Pause song\n"
        "/resume - Resume song\n\n"
        "💡 Example: `/play Dil Bechara`"
    )

@bot.on_message(filters.command("play"))
async def play_cmd(_, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: `/play song name`")
    
    query = " ".join(message.command[1:])
    msg = await message.reply_text("🔍 **Searching...**")
    
    try:
        ydl_opts = {"format": "bestaudio", "quiet": True}
        
        with YoutubeDL(ydl_opts) as ydl:
            if "youtube.com" in query or "youtu.be" in query:
                info = ydl.extract_info(query, download=False)
                title = info.get("title", "Unknown")
                url = info.get("url")
            else:
                search = ydl.extract_info(f"ytsearch:{query}", download=False)
                info = search["entries"][0]
                title = info.get("title", "Unknown")
                url = info.get("url")
        
        chat_id = message.chat.id
        queue = get_queue(chat_id)
        
        if len(queue) > 0:
            queue.append({"title": title, "url": url})
            await msg.edit_text(f"✅ **Added to queue**\n\n📌 {title}\n📍 Position: {len(queue)}")
        else:
            await vc.join_group_call(chat_id, AudioPiped(url))
            await msg.edit_text(f"▶️ **Now Playing**\n\n📌 {title}")
            
    except Exception as e:
        await msg.edit_text(f"❌ **Error:** {str(e)[:100]}")

@bot.on_message(filters.command("stop"))
async def stop_cmd(_, message):
    try:
        await vc.leave_group_call(message.chat.id)
        song_queue[message.chat.id] = []
        await message.reply_text("⏹️ **Stopped and left voice chat**")
    except Exception as e:
        await message.reply_text(f"❌ **Error:** {str(e)[:100]}")

@bot.on_message(filters.command("skip"))
async def skip_cmd(_, message):
    queue = get_queue(message.chat.id)
    
    if len(queue) > 0:
        next_song = queue.pop(0)
        await vc.change_stream(message.chat.id, AudioPiped(next_song["url"]))
        await message.reply_text(f"⏭️ **Skipped**\n\n▶️ **Now Playing:**\n{next_song['title']}")
    else:
        await vc.leave_group_call(message.chat.id)
        await message.reply_text("⏭️ **Queue empty! Left voice chat**")

@bot.on_message(filters.command("queue"))
async def queue_cmd(_, message):
    queue = get_queue(message.chat.id)
    
    if len(queue) == 0:
        await message.reply_text("📋 **Queue is empty**")
    else:
        text = "📋 **Song Queue**\n━━━━━━━━━━━━━━━\n"
        for i, song in enumerate(queue[:10], 1):
            text += f"{i}. {song['title'][:40]}\n"
        await message.reply_text(text)

@bot.on_message(filters.command("pause"))
async def pause_cmd(_, message):
    try:
        await vc.pause_stream(message.chat.id)
        await message.reply_text("⏸️ **Paused**\nUse `/resume` to continue")
    except Exception as e:
        await message.reply_text(f"❌ **Error:** {str(e)[:100]}")

@bot.on_message(filters.command("resume"))
async def resume_cmd(_, message):
    try:
        await vc.resume_stream(message.chat.id)
        await message.reply_text("▶️ **Resumed**")
    except Exception as e:
        await message.reply_text(f"❌ **Error:** {str(e)[:100]}")

@bot.on_message(filters.command("ping"))
async def ping_cmd(_, message):
    await message.reply_text("🏓 **Pong! Bot is alive**")

async def main():
    print("\n" + "="*50)
    print("🚀 STARTING MUSIC BOT...")
    print("="*50)
    
    print("\n📱 Starting Userbot...")
    await userbot.start()
    print("✅ Userbot started")
    
    print("\n🎤 Starting Voice Client...")
    await vc.start()
    print("✅ Voice client started")
    
    print("\n🤖 Starting Bot...")
    await bot.start()
    print("✅ Bot started")
    
    print("\n" + "="*50)
    print("✅ BOT IS LIVE!")
    print("="*50)
    print("\n📝 Commands to test on Telegram:")
    print("   /start - Check bot")
    print("   /play song_name - Play music")
    print("   /stop - Stop music")
    print("   /skip - Skip song")
    print("   /queue - Show queue")
    print("   /pause - Pause")
    print("   /resume - Resume")
    print("="*50 + "\n")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

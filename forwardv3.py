import discord
from telegram import Bot
from telegram.error import TelegramError
import asyncio
import os
import aiohttp

# Token bot Discord dan Telegram
DISCORD_TOKEN = "MTMwNDAzNTM2NDU3ODUyOTM0MQ.GgbBZC.lgVmwWNABj8r0T8dHd2DADGnRe9c_PS00GLqW4"
TELEGRAM_TOKEN = "7705031894:AAGBY7cliOPmzsgFH3XnAE5RarXrvnfEfrM"
TELEGRAM_CHAT_ID = "-926505515"

# Inisialisasi bot Telegram
telegram_bot = Bot(token=TELEGRAM_TOKEN)

# Inisialisasi bot Discord
class MyDiscordClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}!')

    async def on_message(self, message):
        # Jangan forward pesan yang dikirim oleh bot sendiri
        if message.author == self.user:
            return

        # Cek apakah pesan memiliki konten teks atau attachment
        if message.content:
            content = f"Pesan dari Discord:\n\nPengirim: {message.author.name}#{message.author.discriminator}\nIsi: {message.content}"
            await self.send_to_telegram(content)
        elif message.attachments:
            for attachment in message.attachments:
                # Unduh file dan kirim ke Telegram
                await self.download_and_send_file(attachment.url, attachment.filename, attachment.content_type, message.author.name)

    async def send_to_telegram(self, text):
        try:
            await telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
            print("Pesan berhasil diteruskan ke Telegram")
        except TelegramError as e:
            print(f"Error saat mengirim ke Telegram: {e}")

    async def download_and_send_file(self, url, filename, content_type, sender_name):
        # Unduh file
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(filename, 'wb') as f:
                        f.write(await response.read())
                    
                    # Kirim file berdasarkan tipe kontennya
                    try:
                        caption = f"File dari {sender_name} di Discord"
                        if content_type:
                            if 'image' in content_type:
                                # Kirim sebagai foto
                                try:
                                    with open(filename, 'rb') as f:
                                        await telegram_bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=f, caption=caption)
                                    print(f"Gambar '{filename}' berhasil dikirim ke Telegram sebagai foto")
                                except TelegramError as e:
                                    if "Photo_invalid_dimensions" in str(e):
                                        # Jika gagal, kirim sebagai dokumen
                                        with open(filename, 'rb') as f:
                                            await telegram_bot.send_document(chat_id=TELEGRAM_CHAT_ID, document=f, caption=caption)
                                        print(f"Gambar '{filename}' dikirim sebagai dokumen karena dimensinya terlalu besar")
                                    else:
                                        print(f"Error saat mengirim gambar ke Telegram: {e}")
                            elif 'video' in content_type:
                                # Kirim sebagai video
                                with open(filename, 'rb') as f:
                                    await telegram_bot.send_video(chat_id=TELEGRAM_CHAT_ID, video=f, caption=caption)
                                print(f"Video '{filename}' berhasil dikirim ke Telegram")
                            elif 'document' in content_type or 'application' in content_type:
                                # Kirim sebagai dokumen
                                with open(filename, 'rb') as f:
                                    await telegram_bot.send_document(chat_id=TELEGRAM_CHAT_ID, document=f, caption=caption)
                                print(f"Dokumen '{filename}' berhasil dikirim ke Telegram")
                            else:
                                # Kirim file yang tidak dikenali sebagai dokumen
                                with open(filename, 'rb') as f:
                                    await telegram_bot.send_document(chat_id=TELEGRAM_CHAT_ID, document=f, caption=caption)
                                print(f"File '{filename}' dengan tipe tidak dikenali dikirim sebagai dokumen")
                        else:
                        # Jika content_type adalah None, kirim sebagai dokumen
                            with open(filename, 'rb') as f:
                                await telegram_bot.send_document(chat_id=TELEGRAM_CHAT_ID, document=f, caption=caption)
                            print(f"File '{filename}' dikirim sebagai dokumen karena content_type adalah None")
        

                    except TelegramError as e:
                        print(f"Error saat mengirim file ke Telegram: {e}")
                else:
                    print(f"Gagal mengunduh file dari Discord, status: {response.status}")

        # Hapus file setelah dikirim
        if os.path.exists(filename):
            os.remove(filename)

# Jalankan bot Discord
intents = discord.Intents.default()
intents.message_content = True  # Pastikan intents untuk message_content diaktifkan
client = MyDiscordClient(intents=intents)
client.run(DISCORD_TOKEN)

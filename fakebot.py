#!/usr/bin/env python3
"""
Bolt SMS - সিম্পল OTP জেনারেটর বট (২টি বাটন সহ)
- Main Channel এবং Number Bot বাটন থাকবে
- সব কনফিগারেশন স্ক্রিপ্টের ভিতরেই সেট করা আছে
"""

import os
import json
import logging
import random
import asyncio
from datetime import datetime, timedelta
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

# ========== কনফিগারেশন (হার্ডকোড করা) ==========
TELEGRAM_BOT_TOKEN = "8209694083:AAFw8YQqpoPy_XW8s4EP7JGn2MX1GYL5ZOY"
GROUP_CHAT_ID = "-1001153782407"

# বাটনের লিংক
MAIN_CHANNEL_LINK = "https://t.me/updaterange"
NUMBER_BOT_LINK = "https://t.me/Updateotpnew_bot"

# অটো ডিলিট কনফিগারেশন
AUTO_DELETE_MINUTES = 30
CLEANUP_INTERVAL_MINUTES = 30

# ========== ফিল্টার কনফিগারেশন ==========
COUNTRIES = [
    {'code': '358', 'name': 'Finland', 'flag': '🇫🇮'},
    {'code': '977', 'name': 'Nepal', 'flag': '🇳🇵'},
    {'code': '263', 'name': 'Zimbabwe', 'flag': '🇿🇼'},
    {'code': '218', 'name': 'Libya', 'flag': '🇱🇾'},
    {'code': '234', 'name': 'Nigeria', 'flag': '🇳🇬'},
    {'code': '44', 'name': 'United Kingdom', 'flag': '🇬🇧'},
    {'code': '380', 'name': 'Ukraine', 'flag': '🇺🇦'},
]

# প্ল্যাটফর্ম ও আইকন
PLATFORMS = {
    'tiktok': {'icon': '🎬', 'name': 'TIKTOK'},
    'microsoft': {'icon': '💻', 'name': 'MICROSOFT'},
    'signal': {'icon': '🔒', 'name': 'SIGNAL'},
    'apple': {'icon': '🍎', 'name': 'APPLE'},
    'icloud': {'icon': '☁️', 'name': 'ICLOUD'},
    'twitch': {'icon': '🎮', 'name': 'TWITCH'},
    'truecaller': {'icon': '📞', 'name': 'TRUECALLER'},
    'chameet': {'icon': '🐫', 'name': 'CHAMEET'},
    'viber': {'icon': '💜', 'name': 'VIBER'},
    'snapchat': {'icon': '👻', 'name': 'SNAPCHAT'},
    'twilio': {'icon': '📡', 'name': 'TWILIO'},
}

# OTP কনফিগারেশন
DELAY_MIN = 5
DELAY_MAX = 10
GENERATION_INTERVAL = 8
PHONE_PREFIX_LEN = 4
PHONE_SUFFIX_LEN = 5

# =================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RandomOTPGenerator:
    """র‍্যান্ডম OTP জেনারেটর ক্লাস"""
    
    @staticmethod
    def generate_phone_number(country_code):
        lengths = {
            '358': 9, '977': 10, '263': 9,
            '218': 9, '234': 10, '44': 10, '380': 9,
        }
        length = lengths.get(country_code, 9)
        number = ''.join([str(random.randint(0, 9)) for _ in range(length)])
        return f"{country_code}{number}"
    
    @staticmethod
    def mask_phone_number(phone_number):
        phone_str = str(phone_number)
        total_len = len(phone_str)
        
        if total_len > (PHONE_PREFIX_LEN + PHONE_SUFFIX_LEN):
            prefix = phone_str[:PHONE_PREFIX_LEN]
            suffix = phone_str[-PHONE_SUFFIX_LEN:]
            masked = prefix + "***" + suffix
        else:
            masked = phone_str[:2] + "***" + phone_str[-2:]
        
        return masked
    
    @staticmethod
    def generate_otp_code():
        length = random.choice([4, 5, 6])
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])
    
    @staticmethod
    def generate_message(platform, otp_code):
        messages = {
            'tiktok': f"TikTok: Your verification code is {otp_code}",
            'microsoft': f"Microsoft account verification code: {otp_code}",
            'signal': f"Signal: Your code is {otp_code}",
            'apple': f"Apple ID code: {otp_code}",
            'icloud': f"iCloud verification code: {otp_code}",
            'twitch': f"Twitch: Use code {otp_code} to verify your account",
            'truecaller': f"Truecaller code: {otp_code}",
            'chameet': f"Chameet: Your verification code is {otp_code}. Welcome to Chameet!",
            'viber': f"Viber code: {otp_code}. Use this to verify your Viber account.",
            'snapchat': f"Snapchat: Your verification code is {otp_code}. Don't share it!",
            'twilio': f"Twilio: Your verification code is {otp_code}. Valid for 10 minutes.",
        }
        return messages.get(platform.lower(), f"Your verification code is: {otp_code}")
    
    @staticmethod
    def generate_random_time():
        hour = random.randint(0, 11)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        ampm = random.choice(['AM', 'PM'])
        display_hour = 12 if hour == 0 else hour
        return f"{display_hour}:{minute:02d}:{second:02d} {ampm}"
    
    @staticmethod
    def generate_fake_otp_data():
        country = random.choice(COUNTRIES)
        platform_name = random.choice(list(PLATFORMS.keys()))
        platform = PLATFORMS[platform_name]
        
        full_phone = RandomOTPGenerator.generate_phone_number(country['code'])
        masked_phone = RandomOTPGenerator.mask_phone_number(full_phone)
        otp_code = RandomOTPGenerator.generate_otp_code()
        message = RandomOTPGenerator.generate_message(platform_name, otp_code)
        time_str = RandomOTPGenerator.generate_random_time()
        
        return {
            'time': time_str,
            'full_phone': full_phone,
            'masked_phone': masked_phone,
            'country': country,
            'platform_name': platform_name,
            'platform': platform,
            'otp': otp_code,
            'message': message
        }


class OTPBot:
    def __init__(self):
        self.processed_otps = self._load_processed_otps()
        self.sent_messages = self._load_messages()
        self.total_otps_sent = 0
        self.is_monitoring = True
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.generator = RandomOTPGenerator()
        
        logger.info("🤖 Simple OTP Generator Bot Initialized (with 2 buttons)")
    
    def _load_processed_otps(self):
        try:
            if os.path.exists('processed_otps.json'):
                with open('processed_otps.json', 'r') as f:
                    data = json.load(f)
                cutoff = datetime.now() - timedelta(hours=24)
                return {k for k, v in data.items() if datetime.fromisoformat(v) > cutoff}
        except:
            pass
        return set()
    
    def _save_processed_otps(self):
        try:
            data = {otp_id: datetime.now().isoformat() for otp_id in self.processed_otps}
            with open('processed_otps.json', 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def _load_messages(self):
        try:
            if os.path.exists('sent_messages.json'):
                with open('sent_messages.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def _save_messages(self):
        try:
            with open('sent_messages.json', 'w') as f:
                json.dump(self.sent_messages, f)
        except:
            pass
    
    async def delete_old_messages(self):
        """৩০ মিনিটের বেশি পুরনো মেসেজ ডিলিট করুন"""
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=AUTO_DELETE_MINUTES)
        
        to_delete = []
        remaining = []
        
        for msg in self.sent_messages:
            msg_time = datetime.fromisoformat(msg['timestamp'])
            if msg_time < cutoff_time:
                to_delete.append(msg)
            else:
                remaining.append(msg)
        
        deleted_count = 0
        for msg in to_delete:
            try:
                await self.bot.delete_message(
                    chat_id=GROUP_CHAT_ID,
                    message_id=msg['message_id']
                )
                deleted_count += 1
                logger.info(f"🗑️ Deleted old OTP: {msg['message_id']}")
                await asyncio.sleep(0.5)
            except TelegramError as e:
                logger.warning(f"Could not delete: {e}")
        
        self.sent_messages = remaining
        self._save_messages()
        
        if deleted_count > 0:
            logger.info(f"✅ Deleted {deleted_count} old messages")
        
        return deleted_count
    
    async def send_telegram(self, msg):
        """টেলিগ্রামে মেসেজ পাঠান (২টি বাটন সহ)"""
        try:
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Main Channel", url=MAIN_CHANNEL_LINK),
                    InlineKeyboardButton("Number Bot", url=NUMBER_BOT_LINK)
                ]
            ])
            
            result = await self.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=msg,
                parse_mode="Markdown",
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
            
            self.sent_messages.append({
                'message_id': result.message_id,
                'timestamp': datetime.now().isoformat()
            })
            
            if len(self.sent_messages) > 100:
                self.sent_messages = self.sent_messages[-100:]
            
            self._save_messages()
            return True
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    async def send_random_otp(self):
        """একটি সিম্পল OTP জেনারেট করে পাঠান"""
        
        otp_data = self.generator.generate_fake_otp_data()
        
        otp_id = f"{otp_data['time']}_{otp_data['full_phone']}_{otp_data['otp']}"
        
        if otp_id in self.processed_otps:
            logger.info(f"⚠️ Duplicate OTP skipped")
            return False
        
        delay = random.randint(DELAY_MIN, DELAY_MAX)
        logger.info(f"⏳ Generated: {otp_data['country']['name']} - {otp_data['platform_name'].upper()}")
        logger.info(f"⏰ Waiting {delay} seconds...")
        
        await asyncio.sleep(delay)
        
        # সিম্পল মেসেজ ফরম্যাট
        msg = f"""{otp_data['platform']['icon']} **New {otp_data['platform']['name']} OTP!**
━━━━━━━━━━━━━━━━━━━━
🌍 **Country:** {otp_data['country']['flag']} {otp_data['country']['name']}
📱 **Phone:** `{otp_data['masked_phone']}`
🕐 **Time:** `{otp_data['time']}`

🔐 **Code:** `{otp_data['otp']}`

📝 **Message:**
{otp_data['message']}
━━━━━━━━━━━━━━━━━━━━
🤖 @updaterange"""
        
        if await self.send_telegram(msg):
            self.processed_otps.add(otp_id)
            self.total_otps_sent += 1
            self._save_processed_otps()
            logger.info(f"✅ OTP #{self.total_otps_sent} sent! ({otp_data['otp']})")
            return True
        
        return False
    
    async def cleanup_loop(self):
        """ক্লিনআপ লুপ - প্রতি 30 মিনিট পর পর"""
        while self.is_monitoring:
            try:
                await asyncio.sleep(CLEANUP_INTERVAL_MINUTES * 60)
                logger.info("🧹 Running cleanup...")
                await self.delete_old_messages()
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
    
    async def run_generator(self):
        """মূল জেনারেটর লুপ"""
        print("\n" + "="*50)
        print("🤖 SIMPLE OTP GENERATOR BOT")
        print("="*50)
        print(f"🌍 {len(COUNTRIES)} Countries")
        print(f"📱 {len(PLATFORMS)} Platforms")
        print(f"⏱️ Delay: {DELAY_MIN}-{DELAY_MAX}s")
        print(f"⚡ Every: {GENERATION_INTERVAL}s")
        print(f"🗑️ Auto-delete: {AUTO_DELETE_MINUTES} min")
        print(f"🔘 Buttons: Main Channel | Number Bot")
        print("="*50)
        print("\n🚀 Bot is running...")
        print("💾 Press Ctrl+C to stop\n")
        
        cleanup_task = asyncio.create_task(self.cleanup_loop())
        
        while self.is_monitoring:
            try:
                await self.send_random_otp()
                await asyncio.sleep(GENERATION_INTERVAL)
            except Exception as e:
                logger.error(f"Generator error: {e}")
                await asyncio.sleep(5)
        
        cleanup_task.cancel()
    
    async def run(self):
        """বট রান করুন"""
        await self.run_generator()


async def main():
    bot = OTPBot()
    try:
        await bot.run()
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped!")
        print(f"📊 Total OTPs sent: {bot.total_otps_sent}")
        print("👋 Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
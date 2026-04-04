#!/usr/bin/env python3
"""
OTP Generator Bot - Telegram
"""

import os
import json
import logging
import random
import asyncio
from datetime import datetime, timedelta
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

# ========== কনফিগারেশন ==========
TELEGRAM_BOT_TOKEN = "8209694083:AAFw8YQqpoPy_XW8s4EP7JGn2MX1GYL5ZOY"
GROUP_CHAT_ID = "-1001153782407"

MAIN_CHANNEL_LINK = "https://t.me/updaterange"
NUMBER_BOT_LINK = "https://t.me/Updateotpnew_bot"

AUTO_DELETE_MINUTES = 30
CLEANUP_INTERVAL_MINUTES = 30

# ========== দেশের তালিকা ==========
COUNTRIES = [
    # ইউরোপ
    {'code': '358', 'name': 'Finland', 'flag': '🇫🇮'},
    {'code': '44', 'name': 'United Kingdom', 'flag': '🇬🇧'},
    {'code': '380', 'name': 'Ukraine', 'flag': '🇺🇦'},
    {'code': '49', 'name': 'Germany', 'flag': '🇩🇪'},
    {'code': '33', 'name': 'France', 'flag': '🇫🇷'},
    {'code': '39', 'name': 'Italy', 'flag': '🇮🇹'},
    {'code': '34', 'name': 'Spain', 'flag': '🇪🇸'},
    {'code': '7', 'name': 'Russia', 'flag': '🇷🇺'},
    {'code': '48', 'name': 'Poland', 'flag': '🇵🇱'},
    {'code': '46', 'name': 'Sweden', 'flag': '🇸🇪'},
    {'code': '47', 'name': 'Norway', 'flag': '🇳🇴'},
    {'code': '45', 'name': 'Denmark', 'flag': '🇩🇰'},
    {'code': '31', 'name': 'Netherlands', 'flag': '🇳🇱'},
    {'code': '32', 'name': 'Belgium', 'flag': '🇧🇪'},
    {'code': '41', 'name': 'Switzerland', 'flag': '🇨🇭'},
    {'code': '43', 'name': 'Austria', 'flag': '🇦🇹'},
    {'code': '351', 'name': 'Portugal', 'flag': '🇵🇹'},
    {'code': '30', 'name': 'Greece', 'flag': '🇬🇷'},
    {'code': '90', 'name': 'Turkey', 'flag': '🇹🇷'},
    
    # এশিয়া
    {'code': '977', 'name': 'Nepal', 'flag': '🇳🇵'},
    {'code': '91', 'name': 'India', 'flag': '🇮🇳'},
    {'code': '92', 'name': 'Pakistan', 'flag': '🇵🇰'},
    {'code': '94', 'name': 'Sri Lanka', 'flag': '🇱🇰'},
    {'code': '880', 'name': 'Bangladesh', 'flag': '🇧🇩'},
    {'code': '60', 'name': 'Malaysia', 'flag': '🇲🇾'},
    {'code': '62', 'name': 'Indonesia', 'flag': '🇮🇩'},
    {'code': '63', 'name': 'Philippines', 'flag': '🇵🇭'},
    {'code': '66', 'name': 'Thailand', 'flag': '🇹🇭'},
    {'code': '84', 'name': 'Vietnam', 'flag': '🇻🇳'},
    {'code': '82', 'name': 'South Korea', 'flag': '🇰🇷'},
    {'code': '81', 'name': 'Japan', 'flag': '🇯🇵'},
    {'code': '86', 'name': 'China', 'flag': '🇨🇳'},
    {'code': '886', 'name': 'Taiwan', 'flag': '🇹🇼'},
    {'code': '852', 'name': 'Hong Kong', 'flag': '🇭🇰'},
    {'code': '65', 'name': 'Singapore', 'flag': '🇸🇬'},
    
    # আফ্রিকা
    {'code': '263', 'name': 'Zimbabwe', 'flag': '🇿🇼'},
    {'code': '218', 'name': 'Libya', 'flag': '🇱🇾'},
    {'code': '234', 'name': 'Nigeria', 'flag': '🇳🇬'},
    {'code': '27', 'name': 'South Africa', 'flag': '🇿🇦'},
    {'code': '20', 'name': 'Egypt', 'flag': '🇪🇬'},
    {'code': '212', 'name': 'Morocco', 'flag': '🇲🇦'},
    {'code': '216', 'name': 'Tunisia', 'flag': '🇹🇳'},
    {'code': '213', 'name': 'Algeria', 'flag': '🇩🇿'},
    {'code': '254', 'name': 'Kenya', 'flag': '🇰🇪'},
    {'code': '233', 'name': 'Ghana', 'flag': '🇬🇭'},
    {'code': '251', 'name': 'Ethiopia', 'flag': '🇪🇹'},
    {'code': '255', 'name': 'Tanzania', 'flag': '🇹🇿'},
    {'code': '256', 'name': 'Uganda', 'flag': '🇺🇬'},
    
    # মধ্যপ্রাচ্য
    {'code': '966', 'name': 'Saudi Arabia', 'flag': '🇸🇦'},
    {'code': '971', 'name': 'UAE', 'flag': '🇦🇪'},
    {'code': '974', 'name': 'Qatar', 'flag': '🇶🇦'},
    {'code': '965', 'name': 'Kuwait', 'flag': '🇰🇼'},
    {'code': '968', 'name': 'Oman', 'flag': '🇴🇲'},
    {'code': '973', 'name': 'Bahrain', 'flag': '🇧🇭'},
    {'code': '961', 'name': 'Lebanon', 'flag': '🇱🇧'},
    {'code': '962', 'name': 'Jordan', 'flag': '🇯🇴'},
    {'code': '964', 'name': 'Iraq', 'flag': '🇮🇶'},
    {'code': '98', 'name': 'Iran', 'flag': '🇮🇷'},
    {'code': '972', 'name': 'Israel', 'flag': '🇮🇱'},
    
    # আমেরিকা
    {'code': '1', 'name': 'United States', 'flag': '🇺🇸'},
    {'code': '1', 'name': 'Canada', 'flag': '🇨🇦'},
    {'code': '52', 'name': 'Mexico', 'flag': '🇲🇽'},
    {'code': '55', 'name': 'Brazil', 'flag': '🇧🇷'},
    {'code': '54', 'name': 'Argentina', 'flag': '🇦🇷'},
    {'code': '56', 'name': 'Chile', 'flag': '🇨🇱'},
    {'code': '57', 'name': 'Colombia', 'flag': '🇨🇴'},
    {'code': '51', 'name': 'Peru', 'flag': '🇵🇪'},
    {'code': '58', 'name': 'Venezuela', 'flag': '🇻🇪'},
]

# ========== প্ল্যাটফর্মের তালিকা (বর্ধিত) ==========
PLATFORMS = {
    # সোশ্যাল মিডিয়া
    'tiktok': {'icon': '🎬', 'name': 'TIKTOK'},
    'snapchat': {'icon': '👻', 'name': 'SNAPCHAT'},
    'instagram': {'icon': '📸', 'name': 'INSTAGRAM'},
    'facebook': {'icon': '📘', 'name': 'FACEBOOK'},
    'twitter': {'icon': '🐦', 'name': 'TWITTER'},
    'telegram': {'icon': '📨', 'name': 'TELEGRAM'},
    'whatsapp': {'icon': '💚', 'name': 'WHATSAPP'},
    'signal': {'icon': '🔒', 'name': 'SIGNAL'},
    'discord': {'icon': '🎮', 'name': 'DISCORD'},
    'twitch': {'icon': '🎮', 'name': 'TWITCH'},
    'viber': {'icon': '💜', 'name': 'VIBER'},
    'wechat': {'icon': '💚', 'name': 'WECHAT'},
    'line': {'icon': '💚', 'name': 'LINE'},
    
    # টেক কোম্পানি
    'microsoft': {'icon': '💻', 'name': 'MICROSOFT'},
    'apple': {'icon': '🍎', 'name': 'APPLE'},
    'icloud': {'icon': '☁️', 'name': 'ICLOUD'},
    'google': {'icon': '🔴', 'name': 'GOOGLE'},
    'yandex': {'icon': '🔵', 'name': 'YANDEX'},
    'huawei': {'icon': '📱', 'name': 'HUAWEI'},
    'samsung': {'icon': '📱', 'name': 'SAMSUNG'},
    'adobe': {'icon': '🎨', 'name': 'ADOBE'},
    
    # ফাইন্যান্সিয়াল
    'paypal': {'icon': '💰', 'name': 'PAYPAL'},
    'binance': {'icon': '📊', 'name': 'BINANCE'},
    'exness': {'icon': '📈', 'name': 'EXNESS'},
    'remitly': {'icon': '💸', 'name': 'REMITLY'},
    'moneygram': {'icon': '💵', 'name': 'MONEYGRAM'},
    'wise': {'icon': '🌍', 'name': 'WISE'},
    
    # বেটিং ও গেমিং
    '1xbet': {'icon': '🎲', 'name': '1XBET'},
    'melbet': {'icon': '🎰', 'name': 'MELBET'},
    'qnet': {'icon': '💎', 'name': 'QNET'},
    
    # সার্ভিসেস
    'truecaller': {'icon': '📞', 'name': 'TRUECALLER'},
    'sinchverify': {'icon': '✅', 'name': 'SINCHVERIFY'},
    'verimsg': {'icon': '📨', 'name': 'VERIMSG'},
    'infosms': {'icon': '💬', 'name': 'INFOSMS'},
    'procare': {'icon': '🏥', 'name': 'PROCARE'},
    
    # অ্যাপস
    'yango': {'icon': '🚗', 'name': 'YANGO'},
    'glovo': {'icon': '🛵', 'name': 'GLOVO'},
    'indrive': {'icon': '🚙', 'name': 'INDRIVE'},
    'heetch': {'icon': '🚘', 'name': 'HEETCH'},
    'airbnb': {'icon': '🏠', 'name': 'AIRBNB'},
    'ecorparis': {'icon': '🚲', 'name': 'ECOR PARIS'},
    
    # অন্যান্য
    'spova': {'icon': '⭐', 'name': 'SPOVA'},
    'oia': {'icon': '🔵', 'name': 'OIA'},
    'wert': {'icon': '💎', 'name': 'WERT'},
    'mfsafrica': {'icon': '🌍', 'name': 'MFS AFRICA'},
    'cirad': {'icon': '🔬', 'name': 'CIRAD'},
    'fintana': {'icon': '💰', 'name': 'FINTANA'},
}

DELAY_MIN = 5
DELAY_MAX = 10
GENERATION_INTERVAL = 8
PHONE_PREFIX_LEN = 4
PHONE_SUFFIX_LEN = 5

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RandomOTPGenerator:
    
    @staticmethod
    def generate_phone_number(country_code):
        # দেশ অনুযায়ী ফোন নাম্বারের দৈর্ঘ্য
        lengths = {
            '358': 9, '44': 10, '380': 9, '49': 11, '33': 9, '39': 10,
            '34': 9, '7': 10, '48': 9, '46': 9, '47': 8, '45': 8,
            '31': 9, '32': 9, '41': 9, '43': 10, '351': 9, '30': 10,
            '90': 10, '977': 10, '91': 10, '92': 10, '94': 9, '880': 10,
            '60': 9, '62': 10, '63': 10, '66': 9, '84': 9, '82': 10,
            '81': 10, '86': 11, '886': 9, '852': 8, '65': 8, '263': 9,
            '218': 9, '234': 10, '27': 9, '20': 10, '212': 9, '216': 8,
            '213': 9, '254': 9, '233': 9, '251': 9, '255': 9, '256': 9,
            '966': 9, '971': 9, '974': 8, '965': 8, '968': 8, '973': 8,
            '961': 8, '962': 9, '964': 10, '98': 10, '972': 9, '1': 10,
            '52': 10, '55': 11, '54': 10, '56': 9, '57': 10, '51': 9, '58': 10,
        }
        length = lengths.get(str(country_code), 9)
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
            'snapchat': f"Snapchat: Your verification code is {otp_code}",
            'instagram': f"Instagram: Your code is {otp_code}",
            'facebook': f"Facebook: Your verification code is {otp_code}",
            'twitter': f"Twitter: Your code is {otp_code}",
            'telegram': f"Telegram code: {otp_code}",
            'whatsapp': f"WhatsApp code: {otp_code}",
            'discord': f"Discord: Your verification code is {otp_code}",
            'viber': f"Viber code: {otp_code}",
            'wechat': f"WeChat: Your verification code is {otp_code}",
            'line': f"LINE: Your code is {otp_code}",
            'google': f"Google verification code: {otp_code}",
            'yandex': f"Yandex: Your verification code is {otp_code}",
            'huawei': f"Huawei: Your verification code is {otp_code}",
            'samsung': f"Samsung account verification: {otp_code}",
            'adobe': f"Adobe: Your verification code is {otp_code}",
            'paypal': f"PayPal: Your code is {otp_code}",
            'binance': f"Binance: Your verification code is {otp_code}",
            'exness': f"Exness: Your verification code is {otp_code}",
            'remitly': f"Remitly: Your verification code is {otp_code}",
            'moneygram': f"MoneyGram: Your code is {otp_code}",
            'wise': f"Wise: Your verification code is {otp_code}",
            '1xbet': f"1xBet: Your verification code is {otp_code}",
            'melbet': f"Melbet: Your verification code is {otp_code}",
            'qnet': f"QNET: Your verification code is {otp_code}",
            'sinchverify': f"SinchVerify: Your code is {otp_code}",
            'verimsg': f"VERIMSG: Your verification code is {otp_code}",
            'infosms': f"INFOSMS: Your code is {otp_code}",
            'procare': f"ProCare: Your verification code is {otp_code}",
            'yango': f"Yango: Your verification code is {otp_code}",
            'glovo': f"Glovo: Your verification code is {otp_code}",
            'indrive': f"inDrive: Your verification code is {otp_code}",
            'heetch': f"Heetch: Your verification code is {otp_code}",
            'airbnb': f"Airbnb: Your verification code is {otp_code}",
            'ecorparis': f"Ecor Paris: Your verification code is {otp_code}",
            'spova': f"Spova: Your verification code is {otp_code}",
            'oia': f"OIA: Your verification code is {otp_code}",
            'wert': f"Wert: Your verification code is {otp_code}",
            'mfsafrica': f"MFS Africa: Your verification code is {otp_code}",
            'cirad': f"Cirad: Your verification code is {otp_code}",
            'fintana': f"Fintana: Your verification code is {otp_code}",
        }
        base_msg = messages.get(platform.lower(), f"Your verification code is: {otp_code}")
        return f"{base_msg}\nThis OTP will only be valid for 5 minutes. Please do not share your OTP with anyone."
    
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
        
        logger.info("🤖 OTP Generator Bot Initialized")
        logger.info(f"🌍 Total Countries: {len(COUNTRIES)}")
        logger.info(f"📱 Total Platforms: {len(PLATFORMS)}")
    
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
        otp_data = self.generator.generate_fake_otp_data()
        
        otp_id = f"{otp_data['time']}_{otp_data['full_phone']}_{otp_data['otp']}"
        
        if otp_id in self.processed_otps:
            logger.info(f"⚠️ Duplicate OTP skipped")
            return False
        
        delay = random.randint(DELAY_MIN, DELAY_MAX)
        logger.info(f"⏳ Generated: {otp_data['country']['name']} - {otp_data['platform_name'].upper()}")
        logger.info(f"⏰ Waiting {delay} seconds...")
        
        await asyncio.sleep(delay)
        
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
        while self.is_monitoring:
            try:
                await asyncio.sleep(CLEANUP_INTERVAL_MINUTES * 60)
                logger.info("🧹 Running cleanup...")
                await self.delete_old_messages()
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
    
    async def run_generator(self):
        print("\n" + "="*50)
        print("🤖 OTP GENERATOR BOT")
        print("="*50)
        print(f"🌍 Total Countries: {len(COUNTRIES)}")
        print(f"📱 Total Platforms: {len(PLATFORMS)}")
        print(f"⏱️ Delay: {DELAY_MIN}-{DELAY_MAX}s")
        print(f"⚡ Every: {GENERATION_INTERVAL}s")
        print(f"🗑️ Auto-delete: {AUTO_DELETE_MINUTES} min")
        print("="*50)
        print("\n🚀 Bot is running...\n")
        
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
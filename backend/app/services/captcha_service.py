import random
import string
import io
import uuid
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from typing import Optional


class CaptchaService:
    """图形验证码服务"""
    
    _captchas = {}
    
    @staticmethod
    def generate_captcha(length: int = 4) -> tuple[str, str, bytes]:
        """
        生成图形验证码
        返回: (captcha_id, captcha_text, image_bytes)
        """
        captcha_id = str(uuid.uuid4())
        captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        
        img = Image.new('RGB', (120, 40), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 28)
        except:
            font = ImageFont.load_default()
        
        for i, char in enumerate(captcha_text):
            x = 20 + i * 25
            y = random.randint(5, 10)
            color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
            draw.text((x, y), char, font=font, fill=color)
        
        for _ in range(50):
            x1 = random.randint(0, 120)
            y1 = random.randint(0, 40)
            x2 = random.randint(0, 120)
            y2 = random.randint(0, 40)
            color = (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))
            draw.line([(x1, y1), (x2, y2)], fill=color, width=1)
        
        for _ in range(100):
            x = random.randint(0, 120)
            y = random.randint(0, 40)
            color = (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))
            draw.point((x, y), fill=color)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        CaptchaService._captchas[captcha_id] = {
            'text': captcha_text.lower(),
            'expires': datetime.utcnow() + timedelta(minutes=5)
        }
        
        return captcha_id, captcha_text, img_bytes
    
    @staticmethod
    def verify_captcha(captcha_id: str, captcha_text: str) -> bool:
        """验证验证码"""
        if captcha_id not in CaptchaService._captchas:
            return False
        
        captcha_data = CaptchaService._captchas[captcha_id]
        
        if datetime.utcnow() > captcha_data['expires']:
            del CaptchaService._captchas[captcha_id]
            return False
        
        is_valid = captcha_data['text'] == captcha_text.lower()
        
        if is_valid:
            del CaptchaService._captchas[captcha_id]
        
        return is_valid
    
    @staticmethod
    def get_captcha_base64(captcha_id: str, img_bytes: bytes) -> str:
        """获取Base64编码的验证码图片"""
        import base64
        return f"data:image/png;base64,{base64.b64encode(img_bytes).decode()}"
    
    @staticmethod
    def cleanup_expired():
        """清理过期的验证码"""
        now = datetime.utcnow()
        expired_ids = [
            cid for cid, data in CaptchaService._captchas.items()
            if now > data['expires']
        ]
        for cid in expired_ids:
            del CaptchaService._captchas[cid]

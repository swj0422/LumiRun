import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import get_settings
from app.core.logger import logger

settings = get_settings()


class EmailService:
    """邮件服务"""
    
    @staticmethod
    def send_email(to: str, subject: str, body: str) -> bool:
        """
        发送邮件
        
        Args:
            to: 收件人邮箱
            subject: 邮件主题
            body: 邮件正文
            
        Returns:
            bool: 发送是否成功
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_FROM
            msg['To'] = to
            msg['Subject'] = subject
            
            # 添加邮件正文
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # 连接SMTP服务器
            if settings.SMTP_USE_TLS:
                server = smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT)
            else:
                server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
            
            # 登录SMTP服务器
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            
            # 发送邮件
            server.send_message(msg)
            
            # 关闭连接
            server.quit()
            
            logger.info(f"邮件发送成功: {to}")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {to}, 错误: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_email(to: str, reset_link: str) -> bool:
        """
        发送密码重置邮件
        
        Args:
            to: 收件人邮箱
            reset_link: 密码重置链接
            
        Returns:
            bool: 发送是否成功
        """
        subject = "【逐光成长系统】密码重置"
        body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">密码重置请求</h2>
            <p>您好，</p>
            <p>我们收到了您的密码重置请求。请点击以下链接重置您的密码：</p>
            <p style="margin: 20px 0;">
                <a href="{reset_link}" style="display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px;">重置密码</a>
            </p>
            <p>该链接将在1小时后过期。</p>
            <p>如果您没有请求重置密码，请忽略此邮件。</p>
            <p style="margin-top: 30px; font-size: 14px; color: #666;">逐光成长系统</p>
        </div>
        """.format(reset_link=reset_link)
        
        return EmailService.send_email(to, subject, body)

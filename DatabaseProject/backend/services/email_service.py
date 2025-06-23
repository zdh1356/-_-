"""
华轩书店邮件服务模块
负责发送各种类型的邮件通知
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class EmailService:
    """邮件服务类"""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """初始化邮件服务"""
        self.app = app

        # 从配置中获取邮件设置
        self.smtp_server = app.config.get('MAIL_SERVER', 'smtp.qq.com')
        self.smtp_port = app.config.get('MAIL_PORT', 587)
        self.smtp_username = app.config.get('MAIL_USERNAME')
        self.smtp_password = app.config.get('MAIL_PASSWORD')
        self.use_tls = app.config.get('MAIL_USE_TLS', True)
        self.default_sender = app.config.get('MAIL_DEFAULT_SENDER', ('华轩书店', self.smtp_username))

        logger.info(f"邮件服务初始化完成: {self.smtp_server}:{self.smtp_port}")

    def send_email(self, to_email, subject, content, content_type='plain'):
        """
        发送邮件

        Args:
            to_email (str): 收件人邮箱
            subject (str): 邮件主题
            content (str): 邮件内容
            content_type (str): 内容类型 ('plain' 或 'html')

        Returns:
            bool: 发送是否成功
        """
        try:
            logger.info(f"📧 准备发送邮件")
            logger.info(f"  收件人: {to_email}")
            logger.info(f"  主题: {subject}")
            logger.info(f"  SMTP服务器: {self.smtp_server}:{self.smtp_port}")
            logger.info(f"  发件人: {self.smtp_username}")

            # 验证邮件配置
            if not self.smtp_username or not self.smtp_password:
                logger.error("❌ 邮件配置不完整：缺少用户名或密码")
                return False

            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username  # 直接使用邮箱地址，不加显示名
            msg['To'] = to_email
            msg['Subject'] = subject

            # 添加邮件内容
            msg.attach(MIMEText(content, content_type, 'utf-8'))

            logger.info("📝 邮件内容准备完成，开始连接SMTP服务器...")

            # 连接SMTP服务器
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            logger.info("🔗 SMTP服务器连接成功")

            # 启用调试模式
            server.set_debuglevel(1)

            if self.use_tls:
                logger.info("🔒 启用TLS加密...")
                server.starttls()
                logger.info("✅ TLS加密启用成功")

            # 登录
            logger.info("🔑 正在登录SMTP服务器...")
            server.login(self.smtp_username, self.smtp_password)
            logger.info("✅ SMTP登录成功")

            # 发送邮件
            logger.info("📤 正在发送邮件...")
            text = msg.as_string()
            server.sendmail(self.smtp_username, to_email, text)
            server.quit()

            logger.info(f"🎉 邮件发送成功: {to_email}")
            print(f"🎉 邮件发送成功: {to_email}")  # 控制台输出
            return True

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"❌ SMTP认证失败: {e}"
            logger.error(error_msg)
            print(error_msg)
            print("💡 请检查：")
            print("   1. QQ邮箱是否开启了SMTP服务")
            print("   2. 是否使用了正确的授权码（不是QQ密码）")
            print("   3. 授权码是否已过期")
            return False
        except smtplib.SMTPConnectError as e:
            error_msg = f"❌ SMTP连接失败: {e}"
            logger.error(error_msg)
            print(error_msg)
            print("💡 请检查网络连接和SMTP服务器设置")
            return False
        except smtplib.SMTPException as e:
            error_msg = f"❌ SMTP错误: {e}"
            logger.error(error_msg)
            print(error_msg)
            return False
        except Exception as e:
            error_msg = f"❌ 邮件发送失败: {e}"
            logger.error(error_msg)
            print(error_msg)
            return False

    def send_order_confirmation(self, user_email, user_name, order_data):
        """
        发送订单确认邮件

        Args:
            user_email (str): 用户邮箱
            user_name (str): 用户姓名
            order_data (dict): 订单数据

        Returns:
            bool: 发送是否成功
        """
        try:
            subject = f"订单确认 - {order_data['order_number']} - 华轩书店"

            # 生成邮件内容
            content = self._generate_order_email_content(user_name, order_data)

            return self.send_email(user_email, subject, content, 'html')

        except Exception as e:
            logger.error(f"发送订单确认邮件失败: {e}")
            return False

    def _generate_order_email_content(self, user_name, order_data):
        """生成订单确认邮件内容"""

        # 格式化订单商品列表 - 增强版本
        items_html = ""
        for item in order_data.get('items', []):
            items_html += f"""
            <tr>
                <td style="padding: 15px 10px; border-bottom: 1px solid #eee;">
                    <div style="font-weight: bold; color: #2c3e50;">{item.get('title', '未知商品')}</div>
                    <div style="font-size: 12px; color: #666; margin-top: 5px;">
                        作者：{item.get('author', '未知')} | 出版社：{item.get('publisher', '未知')}
                    </div>
                    <div style="font-size: 12px; color: #666;">
                        ISBN：{item.get('isbn', '未知')}
                    </div>
                </td>
                <td style="padding: 15px 10px; border-bottom: 1px solid #eee; text-align: center;">
                    {item.get('quantity', 1)}
                </td>
                <td style="padding: 15px 10px; border-bottom: 1px solid #eee; text-align: right;">
                    ¥{item.get('unit_price', 0):.2f}
                </td>
                <td style="padding: 15px 10px; border-bottom: 1px solid #eee; text-align: right; font-weight: bold;">
                    ¥{item.get('total_price', 0):.2f}
                </td>
            </tr>
            """

        # 获取支付方式
        payment_method_map = {
            'alipay': '支付宝',
            'wechat': '微信支付',
            'bankTransfer': '银行转账'
        }
        payment_method = payment_method_map.get(order_data.get('payment_method', 'alipay'), '支付宝')

        # 生成HTML邮件内容
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>订单确认</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .order-info {{ background-color: white; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .items-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                .items-table th {{ background-color: #34495e; color: white; padding: 10px; text-align: left; }}
                .total {{ font-size: 18px; font-weight: bold; color: #e74c3c; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📚 华轩书店</h1>
                    <h2>订单确认通知</h2>
                </div>

                <div class="content">
                    <p>亲爱的 {user_name}，</p>
                    <p>感谢您在华轩书店购买图书！您的订单已确认，图书详情如下：</p>

                    <div class="order-info" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 20px;">
                        <h3 style="color: white; margin: 0;">📧 数字图书订单</h3>
                        <p style="margin: 10px 0; font-size: 14px;">您购买的图书将以数字形式通过此邮件提供</p>
                    </div>

                    <div class="order-info">
                        <h3>📋 订单信息</h3>
                        <p><strong>订单号：</strong>{order_data.get('order_number', '')}</p>
                        <p><strong>下单时间：</strong>{order_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</p>
                        <p><strong>支付方式：</strong>{payment_method}</p>
                        <p><strong>订单状态：</strong><span style="color: #27ae60; font-weight: bold;">已确认</span></p>
                    </div>

                    <div class="order-info">
                        <h3>📚 您购买的图书</h3>
                        <table class="items-table">
                            <thead>
                                <tr>
                                    <th>图书详情</th>
                                    <th style="text-align: center;">数量</th>
                                    <th style="text-align: right;">单价</th>
                                    <th style="text-align: right;">小计</th>
                                </tr>
                            </thead>
                            <tbody>
                                {items_html}
                            </tbody>
                        </table>
                        <div style="text-align: right; margin-top: 15px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
                            <p class="total" style="margin: 0;">订单总额：¥{order_data.get('total_amount', 0):.2f}</p>
                        </div>
                    </div>

                    <div class="order-info">
                        <h3>📧 数字图书说明</h3>
                        <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; border-left: 4px solid #27ae60;">
                            <p style="margin: 0 0 10px 0;"><strong>📖 阅读方式：</strong>您购买的图书为数字版本，可在任何设备上阅读</p>
                            <p style="margin: 0 0 10px 0;"><strong>📱 支持设备：</strong>电脑、平板、手机等所有智能设备</p>
                            <p style="margin: 0 0 10px 0;"><strong>🔄 永久访问：</strong>购买后可永久保存和阅读</p>
                            <p style="margin: 0;"><strong>💾 下载提示：</strong>建议保存此邮件以便随时查看图书信息</p>
                        </div>
                    </div>

                    <div class="order-info">
                        <h3>💡 温馨提示</h3>
                        <ul>
                            <li>此邮件包含您购买的所有图书详细信息</li>
                            <li>建议将此邮件保存到您的收藏夹或重要邮件文件夹</li>
                            <li>如需纸质版图书，请联系客服：400-123-4567</li>
                            <li>如有任何问题，请随时联系我们的客服团队</li>
                        </ul>
                    </div>
                </div>

                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                    <p>华轩书店 © 2024 版权所有</p>
                    <p>如需帮助，请访问我们的网站或联系客服</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html_content

# 创建全局邮件服务实例
email_service = EmailService()

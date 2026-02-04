"""
Sistema de envío de emails para REDI7 IA
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT


def enviar_codigo_recuperacion(destinatario: str, codigo: str, username: str) -> dict:
    """
    Envía un código de recuperación por email
    
    Args:
        destinatario: Email del destinatario
        codigo: Código de 6 dígitos
        username: Nombre de usuario
    
    Returns:
        dict con success y mensaje
    """
    try:
        # Crear mensaje
        mensaje = MIMEMultipart("alternative")
        mensaje["Subject"] = "🔑 Código de Recuperación - REDI7 IA"
        mensaje["From"] = f"REDI7 IA <{EMAIL_SENDER}>"
        mensaje["To"] = destinatario
        
        # Contenido HTML del email
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .code-box {{
                    background-color: #f8f9fa;
                    border: 2px dashed #667eea;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    margin: 30px 0;
                }}
                .code {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #667eea;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 REDI7 IA</h1>
                    <p>Recuperación de Contraseña</p>
                </div>
                <div class="content">
                    <h2>Hola, {username}!</h2>
                    <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta.</p>
                    
                    <p>Tu código de recuperación es:</p>
                    
                    <div class="code-box">
                        <div class="code">{codigo}</div>
                    </div>
                    
                    <div class="warning">
                        <strong>⏰ Importante:</strong> Este código es válido por <strong>15 minutos</strong> solamente.
                    </div>
                    
                    <p><strong>Instrucciones:</strong></p>
                    <ol>
                        <li>Copia el código de 6 dígitos</li>
                        <li>Vuelve a la aplicación REDI7 IA</li>
                        <li>Ingresa el código y tu nueva contraseña</li>
                    </ol>
                    
                    <p style="color: #dc3545; margin-top: 30px;">
                        <strong>⚠️ ¿No solicitaste este cambio?</strong><br>
                        Si no fuiste tú, ignora este email. Tu contraseña permanecerá segura.
                    </p>
                </div>
                <div class="footer">
                    <p><strong>REDI7 IA</strong> - Sistema Profesional de Análisis de Trading</p>
                    <p>Este es un email automático, por favor no respondas.</p>
                    <p>🔒 Tus datos están protegidos con encriptación SHA-256</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Versión texto plano
        texto = f"""
        REDI7 IA - Recuperación de Contraseña
        
        Hola, {username}!
        
        Tu código de recuperación es: {codigo}
        
        Este código es válido por 15 minutos.
        
        Instrucciones:
        1. Copia el código de 6 dígitos
        2. Vuelve a la aplicación REDI7 IA
        3. Ingresa el código y tu nueva contraseña
        
        Si no solicitaste este cambio, ignora este email.
        
        ---
        REDI7 IA - Sistema Profesional de Análisis de Trading
        """
        
        # Adjuntar versiones al mensaje
        parte_texto = MIMEText(texto, "plain")
        parte_html = MIMEText(html, "html")
        mensaje.attach(parte_texto)
        mensaje.attach(parte_html)
        
        # Conectar y enviar
        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(mensaje)
        
        return {
            "success": True,
            "mensaje": "✅ Código enviado a tu email"
        }
        
    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "mensaje": "❌ Error de autenticación del servidor de email"
        }
    except smtplib.SMTPException as e:
        return {
            "success": False,
            "mensaje": f"❌ Error al enviar email: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "mensaje": f"❌ Error inesperado: {str(e)}"
        }


def enviar_bienvenida(destinatario: str, username: str, nombre_completo: str) -> dict:
    """
    Envía un email de bienvenida profesional al nuevo usuario
    
    Args:
        destinatario: Email del destinatario
        username: Nombre de usuario
        nombre_completo: Nombre completo del usuario
    
    Returns:
        dict con success y mensaje
    """
    try:
        # Crear mensaje
        mensaje = MIMEMultipart("alternative")
        mensaje["Subject"] = "🎉 ¡Bienvenido a REDI7 IA! Tu cuenta está lista"
        mensaje["From"] = f"REDI7 IA <{EMAIL_SENDER}>"
        mensaje["To"] = destinatario
        
        # Contenido HTML del email
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 32px;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 18px;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .welcome-box {{
                    background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
                    border-left: 4px solid #667eea;
                    padding: 20px;
                    margin: 25px 0;
                    border-radius: 5px;
                }}
                .credentials {{
                    background-color: #f8f9fa;
                    border: 2px solid #667eea;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 25px 0;
                    text-align: center;
                }}
                .credentials .label {{
                    color: #666;
                    font-size: 14px;
                    margin-bottom: 5px;
                }}
                .credentials .value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                    font-family: 'Courier New', monospace;
                }}
                .features {{
                    margin: 30px 0;
                }}
                .feature {{
                    padding: 15px;
                    margin: 10px 0;
                    border-left: 3px solid #667eea;
                    background-color: #f8f9fa;
                }}
                .feature-icon {{
                    font-size: 24px;
                    margin-right: 10px;
                }}
                .cta-button {{
                    display: inline-block;
                    padding: 15px 40px;
                    background-color: #667eea;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                    text-align: center;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 30px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                }}
                .footer-links {{
                    margin: 15px 0;
                }}
                .footer-links a {{
                    color: #667eea;
                    text-decoration: none;
                    margin: 0 10px;
                }}
                .social {{
                    margin: 20px 0;
                }}
                .highlight {{
                    color: #667eea;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 ¡Bienvenido a REDI7 IA!</h1>
                    <p>Tu cuenta ha sido creada exitosamente</p>
                </div>
                
                <div class="content">
                    <h2>Hola, {nombre_completo}! 👋</h2>
                    
                    <div class="welcome-box">
                        <p style="margin: 0; font-size: 16px;">
                            <strong>¡Felicitaciones!</strong> Ahora formas parte de la comunidad de traders profesionales que utilizan 
                            <span class="highlight">análisis institucional con Inteligencia Artificial</span> para tomar decisiones informadas en el mercado.
                        </p>
                    </div>
                    
                    <h3>📋 Tus Credenciales de Acceso</h3>
                    <div class="credentials">
                        <div class="label">Tu nombre de usuario es:</div>
                        <div class="value">{username}</div>
                        <p style="margin-top: 15px; color: #666; font-size: 14px;">
                            Usa este usuario junto con tu contraseña para iniciar sesión
                        </p>
                    </div>
                    
                    <h3>🚀 ¿Qué puedes hacer ahora?</h3>
                    <div class="features">
                        <div class="feature">
                            <span class="feature-icon">📊</span>
                            <strong>Análisis Institucional:</strong> Sube hasta 3 capturas diarias para análisis avanzado con GPT-4 Vision
                        </div>
                        <div class="feature">
                            <span class="feature-icon">⏰</span>
                            <strong>Multi-temporalidad:</strong> Obtén análisis para Scalping, Day Trading o Swing Trading
                        </div>
                        <div class="feature">
                            <span class="feature-icon">🎯</span>
                            <strong>Gestión de Riesgo:</strong> Recibe cálculos automáticos de entry, stop loss y take profit
                        </div>
                        <div class="feature">
                            <span class="feature-icon">📱</span>
                            <strong>Telegram:</strong> Configura notificaciones y recibe señales directamente en tu móvil
                        </div>
                        <div class="feature">
                            <span class="feature-icon">📈</span>
                            <strong>Historial:</strong> Consulta todos tus análisis previos en cualquier momento
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://share.streamlit.io" class="cta-button">
                            🚀 Iniciar Sesión Ahora
                        </a>
                    </div>
                    
                    <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 25px 0;">
                        <strong>💡 Consejo Pro:</strong> Para aprovechar al máximo REDI7 IA, asegúrate de subir capturas 
                        de calidad que incluyan el gráfico completo con indicadores visibles.
                    </div>
                    
                    <h3>🆙 ¿Quieres más análisis?</h3>
                    <p>Con nuestro <strong>Plan PRO</strong> (10 análisis/día) o <strong>Plan ELITE</strong> (25 análisis/día) 
                    tendrás acceso ilimitado y funciones exclusivas.</p>
                    
                    <p style="text-align: center; margin: 20px 0;">
                        <a href="https://wa.me/51960239007?text=Hola,%20quiero%20actualizar%20mi%20plan%20REDI7%20IA" 
                           style="color: #667eea; text-decoration: none; font-weight: bold;">
                            💬 Contactar para Actualizar Plan
                        </a>
                    </p>
                </div>
                
                <div class="footer">
                    <p><strong>🧠 REDI7 IA</strong></p>
                    <p>Sistema Profesional de Análisis de Trading Institucional</p>
                    
                    <div class="footer-links">
                        <a href="#">Términos de Servicio</a> | 
                        <a href="#">Política de Privacidad</a> | 
                        <a href="https://wa.me/51960239007">Soporte</a>
                    </div>
                    
                    <div class="social">
                        <p>📧 redi7soporte@gmail.com</p>
                        <p>📱 WhatsApp: +51 960 239 007</p>
                    </div>
                    
                    <p style="font-size: 12px; color: #999; margin-top: 20px;">
                        ⚠️ Disclaimer: Esta herramienta es educacional. El trading conlleva riesgo de pérdida.<br>
                        Opera bajo tu propia responsabilidad.
                    </p>
                    
                    <p style="font-size: 12px; color: #999; margin-top: 15px;">
                        Este email fue enviado a {destinatario}<br>
                        © 2026 REDI7 IA. Todos los derechos reservados.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Versión texto plano
        texto = f"""
        🧠 ¡Bienvenido a REDI7 IA!
        
        Hola, {nombre_completo}!
        
        Tu cuenta ha sido creada exitosamente.
        
        📋 TUS CREDENCIALES:
        Usuario: {username}
        
        🚀 ¿QUÉ PUEDES HACER?
        - Análisis Institucional con IA
        - Multi-temporalidad (Scalping, Day, Swing)
        - Gestión de Riesgo automática
        - Integración con Telegram
        - Historial completo de análisis
        
        Inicia sesión ahora y comienza a analizar el mercado como un profesional.
        
        ¿Necesitas ayuda? Contáctanos:
        📱 WhatsApp: +51 960 239 007
        📧 redi7soporte@gmail.com
        
        ---
        REDI7 IA - Sistema Profesional de Análisis de Trading
        © 2026. Todos los derechos reservados.
        """
        
        # Adjuntar versiones al mensaje
        parte_texto = MIMEText(texto, "plain")
        parte_html = MIMEText(html, "html")
        mensaje.attach(parte_texto)
        mensaje.attach(parte_html)
        
        # Conectar y enviar
        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(mensaje)
        
        return {
            "success": True,
            "mensaje": "✅ Email de bienvenida enviado"
        }
        
    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "mensaje": "❌ Error de autenticación del servidor de email"
        }
    except smtplib.SMTPException as e:
        return {
            "success": False,
            "mensaje": f"❌ Error al enviar email: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "mensaje": f"❌ Error inesperado: {str(e)}"
        }

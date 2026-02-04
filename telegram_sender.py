"""
Sistema de envío de señales a Telegram para REDI7 AI
"""

import requests
import os
from typing import Dict, Optional

class TelegramSender:
    """Clase para enviar mensajes a Telegram"""
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Inicializa el sender de Telegram
        
        Args:
            bot_token: Token del bot de Telegram (opcional, se puede usar variable de entorno)
            chat_id: ID del chat o grupo (opcional, se puede usar variable de entorno)
        """
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        chat_id_str = str(chat_id or os.getenv("TELEGRAM_CHAT_ID", "")).strip()
        
        # Convertir chat_id a número si es posible (soporta negativos para grupos)
        try:
            chat_id_int = int(chat_id_str) if chat_id_str else ""
            
            # Si el chat_id empieza con 100 (supergrupo sin -100), agregar -100
            # Grupos/Supergrupos de Telegram tienen IDs negativos con formato -100xxxxxxxxxx
            if chat_id_int > 0 and str(chat_id_int).startswith('100') and len(str(chat_id_int)) >= 10:
                # Es probablemente un supergrupo sin el prefijo -100
                chat_id_int = int(f"-100{chat_id_int}")
                print(f"ℹ️ Chat ID convertido a formato de supergrupo: {chat_id_int}")
            
            self.chat_id = chat_id_int
        except (ValueError, TypeError):
            self.chat_id = chat_id_str
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def validar_configuracion(self) -> Dict[str, any]:
        """
        Valida que la configuración de Telegram esté completa
        
        Returns:
            Dict con status de validación
        """
        if not self.bot_token:
            return {
                "valido": False,
                "mensaje": "❌ Token del bot no configurado. Configura TELEGRAM_BOT_TOKEN en variables de entorno."
            }
        
        if not self.chat_id:
            return {
                "valido": False,
                "mensaje": "❌ Chat ID no configurado. Configura TELEGRAM_CHAT_ID en variables de entorno."
            }
        
        # Verificar que el bot sea válido
        try:
            response = requests.get(f"{self.api_url}/getMe", timeout=5)
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get("ok"):
                    return {
                        "valido": True,
                        "mensaje": f"✅ Bot conectado: @{bot_info['result']['username']}"
                    }
                else:
                    return {
                        "valido": False,
                        "mensaje": "❌ Token del bot inválido"
                    }
            else:
                return {
                    "valido": False,
                    "mensaje": f"❌ Error al conectar con Telegram: {response.status_code}"
                }
        except Exception as e:
            return {
                "valido": False,
                "mensaje": f"❌ Error de conexión: {str(e)}"
            }
    
    def formatear_mensaje(self, analisis: str, activo: str, modo: str) -> str:
        """
        Formatea el mensaje para Telegram con Markdown
        
        Args:
            analisis: Texto del análisis
            activo: Activo analizado
            modo: Modo de operación
            
        Returns:
            Mensaje formateado para Telegram
        """
        # Telegram usa Markdown, escapar caracteres especiales excepto los de formato
        mensaje = f"🧠 *REDI7 AI - Señal de Trading*\n"
        mensaje += f"━━━━━━━━━━━━━━━━━━━━\n\n"
        mensaje += analisis
        mensaje += f"\n\n━━━━━━━━━━━━━━━━━━━━\n"
        mensaje += f"📊 Activo: *{activo}* | Modo: *{modo}*\n"
        mensaje += f"🤖 Generado por REDI7 IA v1.0"
        
        return mensaje
    
    def enviar_mensaje(
        self, 
        mensaje: str, 
        parse_mode: Optional[str] = "Markdown",
        disable_notification: bool = False
    ) -> Dict[str, any]:
        """
        Envía un mensaje a Telegram
        
        Args:
            mensaje: Texto del mensaje
            parse_mode: Modo de parseo (Markdown o HTML)
            disable_notification: Si se desactiva la notificación
            
        Returns:
            Dict con resultado del envío
        """
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": mensaje,
                "disable_notification": disable_notification
            }

            if parse_mode:
                payload["parse_mode"] = parse_mode
            
            # Debug: mostrar info de envío (sin token completo)
            print(f"🔍 Intentando enviar a Telegram:")
            print(f"   Chat ID: {self.chat_id} (tipo: {type(self.chat_id).__name__})")
            print(f"   Bot Token: {'***' + str(self.bot_token)[-6:] if self.bot_token else 'No configurado'}")
            
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json=payload,
                timeout=10
            )
            
            print(f"   Respuesta HTTP: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Resultado OK: {result.get('ok')}")
                if result.get("ok"):
                    return {
                        "exito": True,
                        "mensaje": "✅ Señal enviada a Telegram correctamente",
                        "message_id": result["result"]["message_id"]
                    }
                else:
                    error_desc = result.get('description', 'Error desconocido')
                    print(f"   Error Telegram: {error_desc}")
                    return {
                        "exito": False,
                        "mensaje": f"❌ Error de Telegram: {error_desc}"
                    }
            else:
                error_text = response.text
                print(f"   Error HTTP: {error_text}")
                return {
                    "exito": False,
                    "mensaje": f"❌ Error HTTP {response.status_code}: {error_text[:100]}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "exito": False,
                "mensaje": "❌ Timeout al enviar a Telegram (verifica tu conexión)"
            }
        except Exception as e:
            return {
                "exito": False,
                "mensaje": f"❌ Error al enviar: {str(e)}"
            }
    
    def enviar_senal(self, analisis: str, activo: str, modo: str) -> Dict[str, any]:
        """
        Envía una señal de trading formateada a Telegram
        
        Args:
            analisis: Texto del análisis completo
            activo: Activo analizado
            modo: Modo de operación
            
        Returns:
            Dict con resultado del envío
        """
        # Validar configuración
        validacion = self.validar_configuracion()
        if not validacion["valido"]:
            return {
                "exito": False,
                "mensaje": validacion["mensaje"]
            }
        
        # Formatear mensaje
        mensaje = self.formatear_mensaje(analisis, activo, modo)
        
        # Enviar mensaje
        return self.enviar_mensaje(mensaje)


def main():
    """Función de prueba"""
    print("=" * 60)
    print("🤖 REDI7 AI - Test de Telegram")
    print("=" * 60)
    print()
    
    # Inicializar
    sender = TelegramSender()
    
    # Validar configuración
    validacion = sender.validar_configuracion()
    print(validacion["mensaje"])
    
    if validacion["valido"]:
        print("\n✅ Configuración válida. Listo para enviar señales.")
        print(f"📱 Chat ID: {sender.chat_id}")
    else:
        print("\n⚠️  Configura las variables de entorno:")
        print("   - TELEGRAM_BOT_TOKEN: Token de tu bot")
        print("   - TELEGRAM_CHAT_ID: ID de tu chat/grupo")
        print("\n📖 Cómo obtenerlos:")
        print("   1. Crea un bot con @BotFather en Telegram")
        print("   2. Obtén el token del bot")
        print("   3. Obtén tu chat_id enviando /start a @userinfobot")


if __name__ == "__main__":
    main()

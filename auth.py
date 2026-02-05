"""
Sistema de Autenticación para REDI7 IA - Versión MySQL
Gestión de usuarios, login y registro con MySQL/Hostinger
"""

import mysql.connector
from mysql.connector import Error
import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional, Dict

class AuthSystem:
    """Sistema de autenticación y gestión de usuarios con MySQL"""

    PLAN_LIMITS = {
        "free": 3,
        "pro": 10,
        "elite": 25
    }
    
    def __init__(self):
        """Inicializar conexión a MySQL"""
        self._get_db_config()
        self._init_database()
    
    def _get_db_config(self):
        """Obtener configuración de base de datos desde secrets o variables de entorno"""
        try:
            import streamlit as st
            self.db_host = st.secrets.get("DB_HOST", "srv1716.hstgr.io")
            self.db_port = int(st.secrets.get("DB_PORT", 3306))
            self.db_user = st.secrets.get("DB_USER", "u114360920_redi7")
            self.db_password = st.secrets.get("DB_PASSWORD", "")
            self.db_name = st.secrets.get("DB_NAME", "u114360920_redi7_users")
        except:
            self.db_host = os.getenv("DB_HOST", "srv1716.hstgr.io")
            self.db_port = int(os.getenv("DB_PORT", 3306))
            self.db_user = os.getenv("DB_USER", "u114360920_redi7")
            self.db_password = os.getenv("DB_PASSWORD", "")
            self.db_name = os.getenv("DB_NAME", "u114360920_redi7_users")
    
    def _get_connection(self):
        """Crear conexión a MySQL"""
        try:
            connection = mysql.connector.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name,
                connect_timeout=10
            )
            return connection
        except Error as e:
            print(f"Error conectando a MySQL: {e}")
            return None
    
    def _safe_close_cursor(self, cursor):
        """Cierra el cursor de forma segura consumiendo resultados pendientes"""
        try:
            if cursor:
                # Consumir cualquier resultado pendiente
                try:
                    while cursor.nextset():
                        pass
                except:
                    pass
                cursor.close()
        except:
            pass
    
    def _init_database(self):
        """Inicializa las tablas de la base de datos"""
        conn = self._get_connection()
        if not conn:
            print("⚠️ No se pudo conectar a la base de datos")
            return
        
        cursor = conn.cursor(buffered=True)
        
        try:
            # Tabla de usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    nombre_completo VARCHAR(255),
                    whatsapp VARCHAR(50) UNIQUE,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ultimo_acceso TIMESTAMP NULL,
                    plan VARCHAR(50) DEFAULT 'free',
                    activo TINYINT DEFAULT 1,
                    is_admin TINYINT DEFAULT 0,
                    referral_code VARCHAR(50) UNIQUE,
                    referred_by INT,
                    telegram_bot_token TEXT,
                    telegram_chat_id VARCHAR(255),
                    recovery_code VARCHAR(10),
                    recovery_expiry DATETIME,
                    INDEX idx_username (username),
                    INDEX idx_email (email),
                    INDEX idx_referral (referral_code)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de historial de análisis
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historial_analisis (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    activo VARCHAR(50),
                    modo VARCHAR(50),
                    temporalidad VARCHAR(255),
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resultado TEXT,
                    FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                    INDEX idx_user_fecha (user_id, fecha)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de sesiones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sesiones (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    token VARCHAR(255) UNIQUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_expiracion TIMESTAMP NULL,
                    FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                    INDEX idx_token (token)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            conn.commit()
            print("✅ Tablas inicializadas correctamente")
            
        except Error as e:
            print(f"Error inicializando tablas: {e}")
        finally:
            self._safe_close_cursor(cursor)
            conn.close()
        
        self._ensure_referral_codes()
        self._crear_admin_inicial()
        self._promover_usuarios_admin()
    
    def _crear_admin_inicial(self):
        """Crea usuario admin si no existe"""
        import os
        
        try:
            import streamlit as st
            admin_username = st.secrets.get("ADMIN_USERNAME", "admin_redi7")
            admin_email = st.secrets.get("ADMIN_EMAIL", "admin@redi7.com")
            admin_password = st.secrets.get("ADMIN_PASSWORD", "Redi7Admin2026!")
        except:
            admin_username = os.getenv("ADMIN_USERNAME", "admin_redi7")
            admin_email = os.getenv("ADMIN_EMAIL", "admin@redi7.com")
            admin_password = os.getenv("ADMIN_PASSWORD", "Redi7Admin2026!")
        
        conn = self._get_connection()
        if not conn:
            return
        
        cursor = conn.cursor(buffered=True)
        
        try:
            cursor.execute("SELECT id FROM usuarios WHERE is_admin = 1")
            result = cursor.fetchone()
            
            if result is None:
                password_hash = self._hash_password(admin_password)
                referral_code = self._generate_referral_code(admin_username)
                
                cursor.execute("""
                    INSERT INTO usuarios (username, email, password_hash, nombre_completo, 
                                        plan, is_admin, referral_code, whatsapp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (admin_username, admin_email, password_hash, "Administrador REDI7", 
                      "elite", 1, referral_code, "+51000000000"))
                conn.commit()
                print(f"✅ Usuario admin creado: {admin_username}")
        except Error as e:
            print(f"Error creando admin: {e}")
        finally:
            self._safe_close_cursor(cursor)
            conn.close()
    
    def _promover_usuarios_admin(self):
        """Promueve usuarios específicos a admin automáticamente"""
        import os
        
        try:
            import streamlit as st
            admin_users = st.secrets.get("ADMIN_USERS", "REDI7,admin").split(",")
        except:
            admin_users = os.getenv("ADMIN_USERS", "REDI7,admin").split(",")
        
        conn = self._get_connection()
        if not conn:
            return
        
        cursor = conn.cursor(buffered=True)
        
        for username in admin_users:
            username = username.strip()
            if username:
                try:
                    cursor.execute("""
                        UPDATE usuarios 
                        SET is_admin = 1, plan = 'elite' 
                        WHERE username = %s AND is_admin = 0
                    """, (username,))
                    if cursor.rowcount > 0:
                        print(f"✅ Usuario {username} promovido a admin")
                except Error as e:
                    print(f"⚠️ Error promoviendo {username}: {e}")
        
        conn.commit()
        self._safe_close_cursor(cursor)
        conn.close()
    
    def _ensure_referral_codes(self):
        """Genera códigos de referido para usuarios existentes"""
        conn = self._get_connection()
        if not conn:
            return
        
        cursor = conn.cursor(buffered=True)
        
        try:
            cursor.execute("SELECT id, username, referral_code FROM usuarios")
            users = cursor.fetchall()
            
            for user_id, username, referral_code in users:
                if not referral_code:
                    new_code = self._generate_referral_code(username)
                    cursor.execute(
                        "UPDATE usuarios SET referral_code = %s WHERE id = %s",
                        (new_code, user_id)
                    )
            
            conn.commit()
        except Error as e:
            print(f"Error generando códigos de referido: {e}")
        finally:
            self._safe_close_cursor(cursor)
            conn.close()
    
    def _hash_password(self, password: str) -> str:
        """Genera hash SHA-256 de la contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_referral_code(self, username: str) -> str:
        """Genera un código único de referido"""
        base = f"{username}-{datetime.now().timestamp()}"
        return hashlib.sha256(base.encode()).hexdigest()[:10].upper()
    
    def registrar_usuario(
        self,
        username: str,
        email: str,
        password: str,
        nombre_completo: str = "",
        codigo_referido: str = "",
        whatsapp: str = ""
    ) -> Dict:
        """Registra un nuevo usuario"""
        try:
            conn = self._get_connection()
            if not conn:
                return {"success": False, "mensaje": "❌ Error de conexión a la base de datos"}
            
            cursor = conn.cursor(buffered=True)
            
            # Validar que no exista el usuario
            cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
            if cursor.fetchone():
                self._safe_close_cursor(cursor)
                conn.close()
                return {"success": False, "mensaje": "❌ El usuario ya existe"}
            
            # Validar que no exista el email
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                self._safe_close_cursor(cursor)
                conn.close()
                return {"success": False, "mensaje": "❌ El email ya está registrado"}
            
            # Validar que no exista el WhatsApp
            if whatsapp:
                cursor.execute("SELECT id FROM usuarios WHERE whatsapp = %s", (whatsapp,))
                if cursor.fetchone():
                    self._safe_close_cursor(cursor)
                    conn.close()
                    return {"success": False, "mensaje": "❌ El número de WhatsApp ya está registrado"}
            
            # Validaciones básicas
            if len(password) < 6:
                self._safe_close_cursor(cursor)
                conn.close()
                return {"success": False, "mensaje": "❌ La contraseña debe tener al menos 6 caracteres"}
            
            if len(username) < 3:
                self._safe_close_cursor(cursor)
                conn.close()
                return {"success": False, "mensaje": "❌ El usuario debe tener al menos 3 caracteres"}
            
            # Verificar código de referido
            referred_by = None
            if codigo_referido:
                cursor.execute("SELECT id FROM usuarios WHERE referral_code = %s", (codigo_referido,))
                ref_user = cursor.fetchone()
                if ref_user:
                    referred_by = ref_user[0]
            
            # Insertar usuario
            password_hash = self._hash_password(password)
            referral_code = self._generate_referral_code(username)
            cursor.execute("""
                INSERT INTO usuarios (username, email, password_hash, nombre_completo, whatsapp, referral_code, referred_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (username, email, password_hash, nombre_completo, whatsapp, referral_code, referred_by))
            
            conn.commit()
            self._safe_close_cursor(cursor)
            conn.close()
            
            # Enviar email de bienvenida
            try:
                from email_sender import enviar_bienvenida
                enviar_bienvenida(email, username, nombre_completo)
            except Exception as e:
                print(f"Advertencia: No se pudo enviar email de bienvenida: {e}")
            
            return {"success": True, "mensaje": "✅ Usuario registrado exitosamente"}
            
        except Error as e:
            return {"success": False, "mensaje": f"❌ Error al registrar: {str(e)}"}
    
    def login(self, username: str, password: str) -> Dict:
        """Autentica un usuario"""
        try:
            conn = self._get_connection()
            if not conn:
                return {"success": False, "mensaje": "❌ Error de conexión a la base de datos"}
            
            cursor = conn.cursor(buffered=True)
            
            # Verificar y promover a admin si corresponde
            import os
            try:
                import streamlit as st
                admin_users = st.secrets.get("ADMIN_USERS", "REDI7").split(",")
            except:
                admin_users = os.getenv("ADMIN_USERS", "REDI7").split(",")
            
            admin_users = [u.strip() for u in admin_users if u.strip()]
            
            # Si el usuario está en la lista de admins, actualizarlo
            if username in admin_users:
                cursor.execute("""
                    UPDATE usuarios 
                    SET is_admin = 1, plan = 'elite' 
                    WHERE username = %s AND is_admin = 0
                """, (username,))
                conn.commit()
            
            password_hash = self._hash_password(password)
            
            cursor.execute("""
                SELECT id, username, email, nombre_completo, plan, activo
                FROM usuarios
                WHERE username = %s AND password_hash = %s
            """, (username, password_hash))
            
            user = cursor.fetchone()
            
            if not user:
                self._safe_close_cursor(cursor)
                conn.close()
                return {"success": False, "mensaje": "❌ Usuario o contraseña incorrectos"}
            
            if user[5] == 0:  # activo
                self._safe_close_cursor(cursor)
                conn.close()
                return {"success": False, "mensaje": "❌ Usuario inactivo. Contacta al administrador"}
            
            # Actualizar último acceso
            cursor.execute("""
                UPDATE usuarios
                SET ultimo_acceso = NOW()
                WHERE id = %s
            """, (user[0],))
            
            conn.commit()
            self._safe_close_cursor(cursor)
            conn.close()
            
            return {
                "success": True,
                "mensaje": f"✅ Bienvenido {user[1]}",
                "user_data": {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2],
                    "nombre_completo": user[3],
                    "plan": user[4]
                }
            }
            
        except Error as e:
            return {"success": False, "mensaje": f"❌ Error al iniciar sesión: {str(e)}"}
    
    def can_analyze(self, user_id: int, plan: str) -> Dict:
        """Verifica si el usuario puede realizar más análisis hoy"""
        conn = self._get_connection()
        if not conn:
            return {"allowed": False, "used": 0, "limit": 0, "remaining": 0}
        
        cursor = conn.cursor(buffered=True)
        
        try:
            today = datetime.now().date()
            cursor.execute("""
                SELECT COUNT(*) FROM historial_analisis 
                WHERE user_id = %s AND DATE(fecha) = %s
            """, (user_id, today))
            
            used = cursor.fetchone()[0]
            limit = self.PLAN_LIMITS.get(plan, 3)
            remaining = max(0, limit - used)
            
            self._safe_close_cursor(cursor)
            conn.close()
            
            return {
                "allowed": remaining > 0,
                "used": used,
                "limit": limit,
                "remaining": remaining
            }
        except Error as e:
            print(f"Error verificando límites: {e}")
            self._safe_close_cursor(cursor)
            conn.close()
            return {"allowed": False, "used": 0, "limit": 0, "remaining": 0}
    
    def obtener_historial(self, user_id: int, limit: int = 10):
        """Obtiene el historial de análisis del usuario"""
        conn = self._get_connection()
        if not conn:
            return []
        
        cursor = conn.cursor(buffered=True)
        
        try:
            cursor.execute("""
                SELECT activo, modo, temporalidad, fecha, resultado 
                FROM historial_analisis 
                WHERE user_id = %s 
                ORDER BY fecha DESC 
                LIMIT %s
            """, (user_id, limit))
            
            historial = cursor.fetchall()
            self._safe_close_cursor(cursor)
            conn.close()
            
            return historial
        except Error as e:
            print(f"Error obteniendo historial: {e}")
            self._safe_close_cursor(cursor)
            conn.close()
            return []
    
    def guardar_telegram_config(self, user_id: int, bot_token: str, chat_id: str) -> Dict:
        """Guarda la configuración de Telegram del usuario"""
        conn = self._get_connection()
        if not conn:
            return {"success": False, "mensaje": "❌ Error de conexión"}
        
        cursor = conn.cursor(buffered=True)
        
        try:
            cursor.execute("""
                UPDATE usuarios 
                SET telegram_bot_token = %s, telegram_chat_id = %s 
                WHERE id = %s
            """, (bot_token, chat_id, user_id))
            
            conn.commit()
            self._safe_close_cursor(cursor)
            conn.close()
            
            return {"success": True, "mensaje": "✅ Configuración guardada"}
        except Error as e:
            self._safe_close_cursor(cursor)
            conn.close()
            return {"success": False, "mensaje": f"❌ Error: {str(e)}"}
    
    def obtener_telegram_config(self, user_id: int) -> Dict:
        """Obtiene la configuración de Telegram del usuario"""
        conn = self._get_connection()
        if not conn:
            return {"configurado": False, "bot_token": "", "chat_id": ""}
        
        cursor = conn.cursor(buffered=True)
        
        try:
            cursor.execute("""
                SELECT telegram_bot_token, telegram_chat_id 
                FROM usuarios 
                WHERE id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            self._safe_close_cursor(cursor)
            conn.close()
            
            if result and result[0] and result[1]:
                return {
                    "configurado": True,
                    "bot_token": result[0],
                    "chat_id": result[1]
                }
            else:
                return {"configurado": False, "bot_token": "", "chat_id": ""}
        except Error as e:
            print(f"Error obteniendo config Telegram: {e}")
            self._safe_close_cursor(cursor)
            conn.close()
            return {"configurado": False, "bot_token": "", "chat_id": ""}
    
    def solicitar_recuperacion(self, email: str) -> Dict:
        """Genera y envía código de recuperación de contraseña"""
        import random
        
        conn = self._get_connection()
        if not conn:
            return {"success": False, "mensaje": "❌ Error de conexión"}
        
        cursor = conn.cursor(buffered=True)
        
        try:
            cursor.execute("SELECT id, username FROM usuarios WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if not user:
                self._safe_close_cursor(cursor)
                conn.close()
                return {"success": False, "mensaje": "❌ Email no registrado"}
            
            user_id, username = user
            codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            codigo_hash = self._hash_password(codigo)
            expiry = datetime.now() + timedelta(minutes=15)
            
            cursor.execute("""
                UPDATE usuarios 
                SET recovery_code = %s, recovery_expiry = %s 
                WHERE id = %s
            """, (codigo_hash, expiry, user_id))
            
            conn.commit()
            self._safe_close_cursor(cursor)
            conn.close()
            
            # Enviar email
            try:
                from email_sender import enviar_codigo_recuperacion
                resultado_email = enviar_codigo_recuperacion(email, username, codigo)
                
                if resultado_email.get("success"):
                    return {"success": True, "mensaje": "📧 Código enviado a tu email"}
                else:
                    return {"success": True, "mensaje": "✅ Código generado", "codigo": codigo}
            except Exception as e:
                print(f"Error enviando email: {e}")
                return {"success": True, "mensaje": "✅ Código generado", "codigo": codigo}
                
        except Error as e:
            return {"success": False, "mensaje": f"❌ Error: {str(e)}"}
    
    def verificar_codigo_recuperacion(self, email: str, codigo: str) -> bool:
        """Verifica si el código de recuperación es válido"""
        conn = self._get_connection()
        if not conn:
            return False
        
        cursor = conn.cursor(buffered=True)
        
        try:
            codigo_hash = self._hash_password(codigo)
            cursor.execute("""
                SELECT recovery_expiry 
                FROM usuarios 
                WHERE email = %s AND recovery_code = %s
            """, (email, codigo_hash))
            
            result = cursor.fetchone()
            self._safe_close_cursor(cursor)
            conn.close()
            
            if not result:
                return False
            
            expiry = result[0]
            if datetime.now() > expiry:
                return False
            
            return True
        except Error as e:
            print(f"Error verificando código: {e}")
            self._safe_close_cursor(cursor)
            conn.close()
            return False
    
    def restablecer_contrasena(self, email: str, codigo: str, nueva_password: str) -> Dict:
        """Restablece la contraseña del usuario"""
        if not self.verificar_codigo_recuperacion(email, codigo):
            return {"success": False, "mensaje": "❌ Código inválido o expirado"}
        
        conn = self._get_connection()
        if not conn:
            return {"success": False, "mensaje": "❌ Error de conexión"}
        
        cursor = conn.cursor(buffered=True)
        
        try:
            password_hash = self._hash_password(nueva_password)
            cursor.execute("""
                UPDATE usuarios 
                SET password_hash = %s, recovery_code = NULL, recovery_expiry = NULL 
                WHERE email = %s
            """, (password_hash, email))
            
            conn.commit()
            self._safe_close_cursor(cursor)
            conn.close()
            
            return {"success": True, "mensaje": "✅ Contraseña actualizada"}
        except Error as e:
            self._safe_close_cursor(cursor)
            conn.close()
            return {"success": False, "mensaje": f"❌ Error: {str(e)}"}

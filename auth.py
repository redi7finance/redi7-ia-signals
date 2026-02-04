"""
Sistema de Autenticación para REDI7 IA
Gestión de usuarios, login y registro
"""

import sqlite3
import hashlib
import os
from datetime import datetime
from typing import Optional, Dict

class AuthSystem:
    """Sistema de autenticación y gestión de usuarios"""

    PLAN_LIMITS = {
        "free": 3,
        "pro": 10,
        "elite": 25
    }
    
    def __init__(self, db_path: str = "redi7_users.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Inicializa la base de datos de usuarios"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nombre_completo TEXT,
                whatsapp TEXT UNIQUE,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_acceso TIMESTAMP,
                plan TEXT DEFAULT 'free',
                activo INTEGER DEFAULT 1,
                is_admin INTEGER DEFAULT 0,
                referral_code TEXT UNIQUE,
                referred_by INTEGER
            )
        """)
        
        # Tabla de historial de análisis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_analisis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                activo TEXT,
                modo TEXT,
                temporalidad TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resultado TEXT,
                FOREIGN KEY (user_id) REFERENCES usuarios (id)
            )
        """)
        
        # Tabla de sesiones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sesiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                token TEXT UNIQUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_expiracion TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES usuarios (id)
            )
        """)
        
        conn.commit()
        conn.close()

        self._ensure_columns()
        self._ensure_referral_codes()
        self._crear_admin_inicial()
        self._promover_usuarios_admin()
    
    def _crear_admin_inicial(self):
        """Crea usuario admin si no existe (desde Streamlit secrets o valores por defecto)"""
        import os
        
        # Intentar obtener desde Streamlit secrets primero
        try:
            import streamlit as st
            admin_username = st.secrets.get("ADMIN_USERNAME", "admin_redi7")
            admin_email = st.secrets.get("ADMIN_EMAIL", "admin@redi7.com")
            admin_password = st.secrets.get("ADMIN_PASSWORD", "Redi7Admin2026!")
        except:
            # Fallback a variables de entorno o valores por defecto
            admin_username = os.getenv("ADMIN_USERNAME", "admin_redi7")
            admin_email = os.getenv("ADMIN_EMAIL", "admin@redi7.com")
            admin_password = os.getenv("ADMIN_PASSWORD", "Redi7Admin2026!")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar si ya existe un admin
        cursor.execute("SELECT id FROM usuarios WHERE is_admin = 1")
        if cursor.fetchone() is None:
            # No hay admin, crear uno
            password_hash = self._hash_password(admin_password)
            referral_code = self._generate_referral_code(admin_username)
            
            try:
                cursor.execute("""
                    INSERT INTO usuarios (username, email, password_hash, nombre_completo, 
                                        plan, is_admin, referral_code, whatsapp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (admin_username, admin_email, password_hash, "Administrador REDI7", 
                      "elite", 1, referral_code, "+51000000000"))
                conn.commit()
                print(f"✅ Usuario admin creado: {admin_username}")
            except sqlite3.IntegrityError:
                # Ya existe, ignorar
                pass
        
        conn.close()
    
    def _promover_usuarios_admin(self):
        """Promueve usuarios específicos a admin automáticamente"""
        import os
        
        # Lista de usuarios que deben ser admin
        try:
            import streamlit as st
            admin_users = st.secrets.get("ADMIN_USERS", "REDI7,admin").split(",")
        except:
            admin_users = os.getenv("ADMIN_USERS", "REDI7,admin").split(",")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for username in admin_users:
            username = username.strip()
            if username:
                try:
                    cursor.execute("""
                        UPDATE usuarios 
                        SET is_admin = 1, plan = 'elite' 
                        WHERE username = ? AND is_admin = 0
                    """, (username,))
                    if cursor.rowcount > 0:
                        print(f"✅ Usuario {username} promovido a admin")
                except Exception as e:
                    print(f"⚠️ Error promoviendo {username}: {e}")
        
        conn.commit()
        conn.close()

    def _ensure_columns(self):
        """Asegura que existan las columnas necesarias en la tabla usuarios"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(usuarios)")
        existing_cols = {row[1] for row in cursor.fetchall()}

        columns_to_add = {
            "is_admin": "INTEGER DEFAULT 0",
            "referral_code": "TEXT",
            "referred_by": "INTEGER",
            "whatsapp": "TEXT",
            "telegram_bot_token": "TEXT",
            "telegram_chat_id": "TEXT",
            "recovery_code": "TEXT",
            "recovery_expiry": "TEXT"
        }

        for col, col_def in columns_to_add.items():
            if col not in existing_cols:
                cursor.execute(f"ALTER TABLE usuarios ADD COLUMN {col} {col_def}")

        # Índices únicos
        cursor.execute("PRAGMA index_list(usuarios)")
        indexes = {row[1] for row in cursor.fetchall()}
        if "idx_usuarios_referral_code" not in indexes:
            cursor.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_referral_code ON usuarios(referral_code)"
            )
        if "idx_usuarios_whatsapp" not in indexes:
            cursor.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_whatsapp ON usuarios(whatsapp)"
            )

        conn.commit()
        conn.close()

    def _generate_referral_code(self, username: str) -> str:
        """Genera un código único de referido"""
        base = f"{username}-{datetime.now().timestamp()}"
        return hashlib.sha256(base.encode()).hexdigest()[:10].upper()

    def _ensure_referral_codes(self):
        """Genera códigos de referido para usuarios existentes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, referral_code FROM usuarios")
        users = cursor.fetchall()

        for user_id, username, referral_code in users:
            if not referral_code:
                new_code = self._generate_referral_code(username)
                cursor.execute(
                    "UPDATE usuarios SET referral_code = ? WHERE id = ?",
                    (new_code, user_id)
                )

        conn.commit()
        conn.close()
    
    def _hash_password(self, password: str) -> str:
        """Genera hash SHA-256 de la contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def registrar_usuario(
        self,
        username: str,
        email: str,
        password: str,
        nombre_completo: str = "",
        referral_code_input: str = "",
        whatsapp: str = ""
    ) -> Dict:
        """
        Registra un nuevo usuario
        
        Returns:
            Dict con status y mensaje
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Validar que no exista el usuario
            cursor.execute(
                "SELECT id FROM usuarios WHERE username = ?",
                (username,)
            )
            if cursor.fetchone():
                return {
                    "success": False,
                    "mensaje": "❌ El usuario ya existe"
                }
            
            # Validar que no exista el email
            cursor.execute(
                "SELECT id FROM usuarios WHERE email = ?",
                (email,)
            )
            if cursor.fetchone():
                return {
                    "success": False,
                    "mensaje": "❌ El email ya está registrado"
                }
            
            # Validar que no exista el WhatsApp
            if whatsapp:
                cursor.execute(
                    "SELECT id FROM usuarios WHERE whatsapp = ?",
                    (whatsapp,)
                )
                if cursor.fetchone():
                    return {
                        "success": False,
                        "mensaje": "❌ El número de WhatsApp ya está registrado"
                    }
            
            # Validaciones básicas
            if len(password) < 6:
                return {
                    "success": False,
                    "mensaje": "❌ La contraseña debe tener al menos 6 caracteres"
                }
            
            if len(username) < 3:
                return {
                    "success": False,
                    "mensaje": "❌ El usuario debe tener al menos 3 caracteres"
                }
            
            referred_by = None
            if referral_code_input:
                cursor.execute(
                    "SELECT id FROM usuarios WHERE referral_code = ?",
                    (referral_code_input.strip().upper(),)
                )
                ref_user = cursor.fetchone()
                if not ref_user:
                    return {
                        "success": False,
                        "mensaje": "❌ Código de referido inválido"
                    }
                referred_by = ref_user[0]

            # Insertar usuario
            password_hash = self._hash_password(password)
            referral_code = self._generate_referral_code(username)
            cursor.execute("""
                INSERT INTO usuarios (username, email, password_hash, nombre_completo, whatsapp, referral_code, referred_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, email, password_hash, nombre_completo, whatsapp, referral_code, referred_by))
            
            conn.commit()
            conn.close()
            
            # Enviar email de bienvenida
            try:
                from email_sender import enviar_bienvenida
                enviar_bienvenida(email, username, nombre_completo)
            except Exception as e:
                # Si falla el envío del email, no afecta el registro
                print(f"Advertencia: No se pudo enviar email de bienvenida: {e}")
            
            return {
                "success": True,
                "mensaje": "✅ Usuario registrado exitosamente"
            }
            
        except Exception as e:
            return {
                "success": False,
                "mensaje": f"❌ Error al registrar: {str(e)}"
            }
    
    def login(self, username: str, password: str) -> Dict:
        """
        Autentica un usuario
        
        Returns:
            Dict con success, user_data y mensaje
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
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
                    WHERE username = ? AND is_admin = 0
                """, (username,))
                conn.commit()
            
            password_hash = self._hash_password(password)
            
            cursor.execute("""
                SELECT id, username, email, nombre_completo, plan, activo
                FROM usuarios
                WHERE username = ? AND password_hash = ?
            """, (username, password_hash))
            
            user = cursor.fetchone()
            
            if not user:
                return {
                    "success": False,
                    "mensaje": "❌ Usuario o contraseña incorrectos"
                }
            
            if user[5] == 0:  # activo
                return {
                    "success": False,
                    "mensaje": "❌ Usuario inactivo. Contacta al administrador"
                }
            
            # Actualizar último acceso
            cursor.execute("""
                UPDATE usuarios
                SET ultimo_acceso = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (user[0],))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "mensaje": "✅ Acceso concedido",
                "user_data": {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2],
                    "nombre_completo": user[3],
                    "plan": user[4]
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "mensaje": f"❌ Error de autenticación: {str(e)}"
            }
    
    def guardar_analisis(
        self,
        user_id: int,
        activo: str,
        modo: str,
        temporalidad: str,
        resultado: str
    ):
        """Guarda un análisis en el historial del usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO historial_analisis 
                (user_id, activo, modo, temporalidad, resultado)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, activo, modo, temporalidad, resultado))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error guardando análisis: {e}")

    def get_referral_code(self, user_id: int) -> str:
        """Obtiene o genera el código de referido de un usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT referral_code, username FROM usuarios WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return ""

            referral_code, username = row
            if not referral_code:
                referral_code = self._generate_referral_code(username)
                cursor.execute(
                    "UPDATE usuarios SET referral_code = ? WHERE id = ?",
                    (referral_code, user_id)
                )
                conn.commit()
            conn.close()
            return referral_code
        except Exception as e:
            print(f"Error obteniendo referido: {e}")
            return ""

    def get_plan_limit(self, plan: str) -> int:
        """Obtiene el límite diario por plan"""
        return self.PLAN_LIMITS.get(plan.lower(), self.PLAN_LIMITS["free"])

    def get_daily_analisis_count(self, user_id: int) -> int:
        """Cuenta análisis del día para un usuario (zona horaria Perú/Colombia/Ecuador UTC-5)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Usar UTC-5 para Perú/Colombia/Ecuador
            cursor.execute("""
                SELECT COUNT(*) FROM historial_analisis
                WHERE user_id = ? 
                AND date(datetime(fecha, '-5 hours')) = date(datetime('now', '-5 hours'))
            """, (user_id,))
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"Error contando análisis diarios: {e}")
            return 0

    def can_analyze(self, user_id: int, plan: str) -> Dict:
        """Valida si el usuario puede realizar más análisis hoy"""
        used = self.get_daily_analisis_count(user_id)
        limit = self.get_plan_limit(plan)
        remaining = max(limit - used, 0)
        return {
            "allowed": used < limit,
            "used": used,
            "limit": limit,
            "remaining": remaining
        }
    
    def obtener_historial(self, user_id: int, limit: int = 10) -> list:
        """Obtiene el historial de análisis del usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT activo, modo, temporalidad, fecha, resultado
                FROM historial_analisis
                WHERE user_id = ?
                ORDER BY fecha DESC
                LIMIT ?
            """, (user_id, limit))
            
            historial = cursor.fetchall()
            conn.close()
            
            return historial
            
        except Exception as e:
            print(f"Error obteniendo historial: {e}")
            return []
    
    def obtener_estadisticas(self, user_id: int) -> Dict:
        """Obtiene estadísticas del usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total de análisis
            cursor.execute("""
                SELECT COUNT(*) FROM historial_analisis
                WHERE user_id = ?
            """, (user_id,))
            total_analisis = cursor.fetchone()[0]
            
            # Activo más analizado
            cursor.execute("""
                SELECT activo, COUNT(*) as count
                FROM historial_analisis
                WHERE user_id = ?
                GROUP BY activo
                ORDER BY count DESC
                LIMIT 1
            """, (user_id,))
            activo_favorito = cursor.fetchone()
            
            conn.close()
            
            return {
                "total_analisis": total_analisis,
                "activo_favorito": activo_favorito[0] if activo_favorito else "N/A"
            }
            
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {
                "total_analisis": 0,
                "activo_favorito": "N/A"
            }
    
    def guardar_telegram_config(self, user_id: int, bot_token: str, chat_id: str) -> Dict:
        """
        Guarda la configuración de Telegram del usuario
        
        Args:
            user_id: ID del usuario
            bot_token: Token del bot de Telegram
            chat_id: Chat ID del usuario o grupo
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE usuarios 
                SET telegram_bot_token = ?, telegram_chat_id = ?
                WHERE id = ?
            """, (bot_token, chat_id, user_id))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "mensaje": "✅ Configuración de Telegram guardada correctamente"
            }
            
        except Exception as e:
            return {
                "success": False,
                "mensaje": f"❌ Error al guardar configuración: {str(e)}"
            }
    
    def obtener_telegram_config(self, user_id: int) -> Dict:
        """
        Obtiene la configuración de Telegram del usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Dict con bot_token y chat_id
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT telegram_bot_token, telegram_chat_id
                FROM usuarios
                WHERE id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "bot_token": result[0] or "",
                    "chat_id": result[1] or "",
                    "configurado": bool(result[0] and result[1])
                }
            else:
                return {
                    "bot_token": "",
                    "chat_id": "",
                    "configurado": False
                }
                
        except Exception as e:
            print(f"Error obteniendo configuración de Telegram: {e}")
            return {
                "bot_token": "",
                "chat_id": "",
                "configurado": False
            }    
    def solicitar_recuperacion(self, email: str) -> Dict:
        """Genera código de recuperación temporal para un email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar que el email existe
            cursor.execute("SELECT id, username FROM usuarios WHERE email = ?", (email,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return {"success": False, "mensaje": "❌ No existe una cuenta con ese email"}
            
            user_id, username = result
            
            # Generar código de 6 dígitos
            import random
            codigo_recuperacion = str(random.randint(100000, 999999))
            codigo_hash = self._hash_password(codigo_recuperacion)
            
            # Guardar código temporal con expiración de 15 minutos
            from datetime import datetime, timedelta
            expiracion = (datetime.now() + timedelta(minutes=15)).isoformat()
            
            cursor.execute("""
                UPDATE usuarios 
                SET recovery_code = ?, recovery_expiry = ?
                WHERE id = ?
            """, (codigo_hash, expiracion, user_id))
            
            conn.commit()
            conn.close()
            
            # Enviar email con el código
            try:
                from email_sender import enviar_codigo_recuperacion
                resultado_email = enviar_codigo_recuperacion(email, codigo_recuperacion, username)
                
                if resultado_email["success"]:
                    return {
                        "success": True,
                        "mensaje": f"✅ Código enviado a {email}",
                        "username": username
                    }
                else:
                    # Si falla el envío, mostrar el código en pantalla como fallback
                    return {
                        "success": True,
                        "mensaje": f"⚠️ No se pudo enviar email. Tu código es: {codigo_recuperacion}",
                        "codigo": codigo_recuperacion,
                        "username": username
                    }
            except Exception as e:
                # Fallback: mostrar código en pantalla si hay error
                return {
                    "success": True,
                    "mensaje": f"⚠️ Error de email. Tu código es: {codigo_recuperacion}",
                    "codigo": codigo_recuperacion,
                    "username": username
                }
            
        except Exception as e:
            return {"success": False, "mensaje": f"❌ Error: {str(e)}"}
    
    def verificar_codigo_recuperacion(self, email: str, codigo: str) -> Dict:
        """Verifica el código de recuperación"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, recovery_code, recovery_expiry 
                FROM usuarios 
                WHERE email = ?
            """, (email,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return {"success": False, "mensaje": "❌ Email no encontrado"}
            
            user_id, recovery_code_hash, recovery_expiry = result
            
            if not recovery_code_hash or not recovery_expiry:
                return {"success": False, "mensaje": "❌ No hay código activo. Solicita uno nuevo."}
            
            # Verificar expiración
            from datetime import datetime
            if datetime.now() > datetime.fromisoformat(recovery_expiry):
                return {"success": False, "mensaje": "⏰ Código expirado. Solicita uno nuevo."}
            
            # Verificar código
            codigo_hash = self._hash_password(codigo)
            if codigo_hash != recovery_code_hash:
                return {"success": False, "mensaje": "❌ Código incorrecto"}
            
            return {"success": True, "mensaje": "✅ Código válido", "user_id": user_id}
            
        except Exception as e:
            return {"success": False, "mensaje": f"❌ Error: {str(e)}"}
    
    def restablecer_contrasena(self, email: str, codigo: str, nueva_password: str) -> Dict:
        """Restablece la contraseña después de verificar el código"""
        try:
            # Primero verificar el código
            verificacion = self.verificar_codigo_recuperacion(email, codigo)
            if not verificacion["success"]:
                return verificacion
            
            user_id = verificacion["user_id"]
            
            # Actualizar contraseña
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            nueva_password_hash = self._hash_password(nueva_password)
            
            cursor.execute("""
                UPDATE usuarios 
                SET password_hash = ?, recovery_code = NULL, recovery_expiry = NULL
                WHERE id = ?
            """, (nueva_password_hash, user_id))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "mensaje": "✅ Contraseña actualizada correctamente"}
            
        except Exception as e:
            return {"success": False, "mensaje": f"❌ Error: {str(e)}"}
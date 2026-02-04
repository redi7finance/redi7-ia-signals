"""
Script temporal para hacer admin al usuario REDI7
Ejecutar en Streamlit Cloud para promover usuario a admin
"""

import sqlite3

def hacer_admin(username="REDI7"):
    """Hace admin a un usuario específico"""
    try:
        conn = sqlite3.connect("redi7_users.db")
        cursor = conn.cursor()
        
        # Verificar si el usuario existe
        cursor.execute("SELECT id, username, is_admin FROM usuarios WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Usuario {username} no encontrado")
            conn.close()
            return False
        
        user_id, username, is_admin = user
        
        if is_admin == 1:
            print(f"✅ Usuario {username} ya es admin")
            conn.close()
            return True
        
        # Hacer admin
        cursor.execute("""
            UPDATE usuarios 
            SET is_admin = 1, plan = 'elite' 
            WHERE username = ?
        """, (username,))
        
        conn.commit()
        print(f"✅ Usuario {username} promovido a ADMIN con plan ELITE")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    hacer_admin("REDI7")

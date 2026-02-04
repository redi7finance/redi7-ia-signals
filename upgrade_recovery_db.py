"""
Script para agregar columnas de recuperación de contraseña a la base de datos
"""
import sqlite3

def upgrade_database():
    """Agrega las columnas de recovery_code y recovery_expiry"""
    try:
        conn = sqlite3.connect("redi7_users.db")
        cursor = conn.cursor()
        
        # Verificar qué columnas existen
        cursor.execute("PRAGMA table_info(usuarios)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        
        # Agregar recovery_code si no existe
        if "recovery_code" not in existing_cols:
            print("Agregando columna recovery_code...")
            cursor.execute("ALTER TABLE usuarios ADD COLUMN recovery_code TEXT")
            print("✅ Columna recovery_code agregada")
        else:
            print("ℹ️ Columna recovery_code ya existe")
        
        # Agregar recovery_expiry si no existe
        if "recovery_expiry" not in existing_cols:
            print("Agregando columna recovery_expiry...")
            cursor.execute("ALTER TABLE usuarios ADD COLUMN recovery_expiry TEXT")
            print("✅ Columna recovery_expiry agregada")
        else:
            print("ℹ️ Columna recovery_expiry ya existe")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Base de datos actualizada correctamente")
        print("Ya puedes usar la función de recuperación de contraseña")
        
    except Exception as e:
        print(f"❌ Error actualizando base de datos: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("Actualización de Base de Datos - Recuperación de Contraseña")
    print("=" * 50)
    print()
    upgrade_database()

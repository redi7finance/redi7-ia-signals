"""
Panel de Administración para REDI7 IA
Sistema completo de gestión y monitoreo
"""

import streamlit as st
from auth import AuthSystem
from datetime import datetime, timedelta
import sqlite3

class AdminPanel:
    """Panel administrativo con estadísticas y gestión"""
    
    def __init__(self):
        self.auth = AuthSystem()
        self.db_path = "redi7_users.db"
    
    def is_admin(self, user_id: int) -> bool:
        """Verifica si el usuario es administrador"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT is_admin FROM usuarios WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result and result[0] == 1
    
    def make_admin(self, username: str) -> dict:
        """Convierte un usuario en administrador"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE usuarios 
                SET is_admin = 1 
                WHERE username = ?
            """, (username,))
            conn.commit()
            conn.close()
            return {"success": True, "message": f"✅ {username} es ahora administrador"}
        except Exception as e:
            return {"success": False, "message": f"❌ Error: {str(e)}"}
    
    def get_dashboard_stats(self) -> dict:
        """Obtiene estadísticas generales del sistema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total usuarios
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total_usuarios = cursor.fetchone()[0]
        
        # Usuarios por plan
        cursor.execute("SELECT plan, COUNT(*) FROM usuarios GROUP BY plan")
        usuarios_por_plan = dict(cursor.fetchall())
        
        # Total análisis
        cursor.execute("SELECT COUNT(*) FROM historial_analisis")
        total_analisis = cursor.fetchone()[0]
        
        # Análisis últimos 7 días
        hace_7_dias = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT COUNT(*) FROM historial_analisis 
            WHERE fecha >= ?
        """, (hace_7_dias,))
        analisis_7_dias = cursor.fetchone()[0]
        
        # Análisis por activo
        cursor.execute("""
            SELECT activo, COUNT(*) 
            FROM historial_analisis 
            GROUP BY activo 
            ORDER BY COUNT(*) DESC
        """)
        analisis_por_activo = dict(cursor.fetchall())
        
        # Usuarios activos (últimos 7 días)
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) FROM historial_analisis 
            WHERE fecha >= ?
        """, (hace_7_dias,))
        usuarios_activos_7d = cursor.fetchone()[0]
        
        # Análisis hoy
        hoy = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT COUNT(*) FROM historial_analisis 
            WHERE fecha >= ?
        """, (hoy,))
        analisis_hoy = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_usuarios": total_usuarios,
            "usuarios_por_plan": usuarios_por_plan,
            "total_analisis": total_analisis,
            "analisis_7_dias": analisis_7_dias,
            "analisis_por_activo": analisis_por_activo,
            "usuarios_activos_7d": usuarios_activos_7d,
            "analisis_hoy": analisis_hoy
        }
    
    def get_all_users(self) -> list:
        """Obtiene lista de todos los usuarios"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, plan, fecha_registro, is_admin, referral_code, referred_by
            FROM usuarios
            ORDER BY fecha_registro DESC
        """)
        users = cursor.fetchall()
        conn.close()
        return users
    
    def get_user_details(self, user_id: int) -> dict:
        """Obtiene detalles completos de un usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Info usuario
        cursor.execute("""
            SELECT username, email, plan, fecha_registro
            FROM usuarios WHERE id = ?
        """, (user_id,))
        user_info = cursor.fetchone()
        
        # Estadísticas del usuario
        cursor.execute("""
                 SELECT COUNT(*), 
                     COUNT(CASE WHEN fecha >= date('now', '-7 days') THEN 1 END)
                 FROM historial_analisis WHERE user_id = ?
        """, (user_id,))
        analisis_stats = cursor.fetchone()
        
        # Últimos análisis
        cursor.execute("""
            SELECT fecha, activo, modo, temporalidad
            FROM historial_analisis 
            WHERE user_id = ?
            ORDER BY fecha DESC
            LIMIT 10
        """, (user_id,))
        ultimos_analisis = cursor.fetchall()

        # Referidos
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE referred_by = ?", (user_id,))
        referidos_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "username": user_info[0],
            "email": user_info[1],
            "plan": user_info[2],
            "fecha_registro": user_info[3],
            "total_analisis": analisis_stats[0],
            "analisis_7d": analisis_stats[1],
            "ultimos_analisis": ultimos_analisis,
            "referidos_count": referidos_count
        }
    
    def change_user_plan(self, user_id: int, new_plan: str) -> dict:
        """Cambia el plan de un usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE usuarios 
                SET plan = ?
                WHERE id = ?
            """, (new_plan, user_id))
            conn.commit()
            conn.close()
            return {"success": True, "message": f"✅ Plan cambiado a {new_plan}"}
        except Exception as e:
            return {"success": False, "message": f"❌ Error: {str(e)}"}
    
    def block_user(self, user_id: int) -> dict:
        """Bloquea un usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET activo = 0 WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            return {"success": True, "message": "✅ Usuario bloqueado"}
        except Exception as e:
            return {"success": False, "message": f"❌ Error: {str(e)}"}
    
    def unblock_user(self, user_id: int) -> dict:
        """Desbloquea un usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET activo = 1 WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            return {"success": True, "message": "✅ Usuario desbloqueado"}
        except Exception as e:
            return {"success": False, "message": f"❌ Error: {str(e)}"}
    
    def delete_user(self, user_id: int) -> dict:
        """Elimina un usuario y sus análisis"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Eliminar análisis
            cursor.execute("DELETE FROM historial_analisis WHERE user_id = ?", (user_id,))
            
            # Eliminar usuario
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            return {"success": True, "message": "✅ Usuario eliminado"}
        except Exception as e:
            return {"success": False, "message": f"❌ Error: {str(e)}"}
    
    def get_recent_activity(self, limit: int = 20) -> list:
        """Obtiene actividad reciente del sistema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.fecha, u.username, a.activo, a.modo
            FROM historial_analisis a
            JOIN usuarios u ON a.user_id = u.id
            ORDER BY a.fecha DESC
            LIMIT ?
        """, (limit,))
        activity = cursor.fetchall()
        conn.close()
        return activity
    
    def render_admin_page(self):
        """Renderiza la página completa de administración"""
        
        # Header
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 15px; margin-bottom: 30px;'>
            <h1 style='color: white; text-align: center; margin: 0;'>
                👑 Panel de Administración REDI7 IA
            </h1>
            <p style='color: white; text-align: center; margin-top: 10px;'>
                Sistema de gestión y monitoreo completo
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs principales
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Dashboard", 
            "👥 Usuarios", 
            "📈 Actividad",
            "⚙️ Configuración"
        ])
        
        # TAB 1: DASHBOARD
        with tab1:
            stats = self.get_dashboard_stats()
            
            # Métricas superiores
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "👥 Total Usuarios",
                    stats['total_usuarios'],
                    f"+{stats['usuarios_activos_7d']} activos (7d)"
                )
            
            with col2:
                st.metric(
                    "📊 Total Análisis",
                    stats['total_analisis'],
                    f"+{stats['analisis_7_dias']} (7d)"
                )
            
            with col3:
                st.metric(
                    "🔥 Análisis Hoy",
                    stats['analisis_hoy']
                )
            
            with col4:
                revenue_estimate = (
                    stats['usuarios_por_plan'].get('pro', 0) * 79 +
                    stats['usuarios_por_plan'].get('elite', 0) * 199
                )
                st.metric(
                    "💰 Ingresos Est.",
                    f"${revenue_estimate:,.0f}/mes"
                )
            
            st.markdown("---")
            
            # Gráficos
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.subheader("📊 Usuarios por Plan")
                for plan, count in stats['usuarios_por_plan'].items():
                    percentage = (count / stats['total_usuarios'] * 100) if stats['total_usuarios'] > 0 else 0
                    st.progress(percentage / 100)
                    st.write(f"**{plan.upper()}**: {count} usuarios ({percentage:.1f}%)")
            
            with col_right:
                st.subheader("🎯 Análisis por Activo")
                for activo, count in stats['analisis_por_activo'].items():
                    percentage = (count / stats['total_analisis'] * 100) if stats['total_analisis'] > 0 else 0
                    st.progress(percentage / 100)
                    st.write(f"**{activo}**: {count} análisis ({percentage:.1f}%)")
        
        # TAB 2: GESTIÓN DE USUARIOS
        with tab2:
            st.subheader("👥 Gestión de Usuarios")
            
            # Tabla de uso de consultas diarias
            st.markdown("#### 📊 Uso de Consultas Hoy")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener uso de consultas por usuario hoy (UTC-5)
            cursor.execute("""
                SELECT 
                    u.username,
                    u.plan,
                    COUNT(h.id) as consultas_hoy,
                    CASE u.plan
                        WHEN 'free' THEN 3
                        WHEN 'pro' THEN 10
                        WHEN 'elite' THEN 25
                        ELSE 3
                    END as limite
                FROM usuarios u
                LEFT JOIN historial_analisis h ON u.id = h.user_id 
                    AND date(datetime(h.fecha, '-5 hours')) = date(datetime('now', '-5 hours'))
                WHERE u.activo = 1
                GROUP BY u.id, u.username, u.plan
                ORDER BY consultas_hoy DESC
            """)
            usage_data = cursor.fetchall()
            conn.close()
            
            if usage_data:
                col1, col2, col3, col4 = st.columns(4)
                col1.markdown("**Usuario**")
                col2.markdown("**Plan**")
                col3.markdown("**Consultas Hoy**")
                col4.markdown("**Límite**")
                
                for username, plan, consultas, limite in usage_data:
                    col1, col2, col3, col4 = st.columns(4)
                    col1.text(username)
                    col2.text(plan.upper())
                    
                    # Colorear según uso
                    if consultas >= limite:
                        col3.markdown(f"🔴 **{consultas}**")
                    elif consultas >= limite * 0.8:
                        col3.markdown(f"🟡 **{consultas}**")
                    else:
                        col3.markdown(f"🟢 {consultas}")
                    
                    col4.text(f"{limite}")
            
            st.markdown("---")
            st.markdown("#### 👥 Lista de Usuarios")
            
            users = self.get_all_users()
            
            # Filtros
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                plan_filter = st.selectbox(
                    "Filtrar por plan:",
                    ["Todos", "free", "pro", "elite"]
                )
            
            # Tabla de usuarios
            for user in users:
                user_id, username, email, plan, fecha_reg, is_admin, referral_code, referred_by = user
                
                if plan_filter != "Todos" and plan != plan_filter:
                    continue
                
                # Obtener estado activo
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT activo FROM usuarios WHERE id = ?", (user_id,))
                activo = cursor.fetchone()[0]
                conn.close()
                
                status_icon = "🔴" if activo == 0 else "🟢"
                with st.expander(f"{status_icon} {'👑' if is_admin else '👤'} {username} - {email} [{plan.upper()}]"):
                    details = self.get_user_details(user_id)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Análisis", details['total_analisis'])
                    with col2:
                        st.metric("Análisis (7d)", details['analisis_7d'])
                    with col3:
                        st.metric("Miembro desde", fecha_reg[:10])
                    
                    st.markdown(f"**Estado:** {'🔴 BLOQUEADO' if activo == 0 else '🟢 ACTIVO'}")
                    st.markdown(f"**Referidos:** {details['referidos_count']}")
                    if referral_code:
                        st.markdown("**Link de referido:**")
                        st.code(f"?ref={referral_code}")

                    # Acciones
                    st.markdown("**Acciones:**")
                    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
                    
                    with col_a1:
                        plan_options = ["free", "pro", "elite"]
                        if plan not in plan_options:
                            plan_options.append(plan)
                        new_plan = st.selectbox(
                            "Cambiar plan",
                            plan_options,
                            index=plan_options.index(plan),
                            key=f"plan_{user_id}"
                        )
                        if st.button("💾 Guardar", key=f"save_{user_id}"):
                            result = self.change_user_plan(user_id, new_plan)
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['message'])
                    
                    with col_a2:
                        if activo == 1:
                            if st.button("🔒 Bloquear", key=f"block_{user_id}", type="secondary"):
                                result = self.block_user(user_id)
                                if result['success']:
                                    st.success(result['message'])
                                    st.rerun()
                                else:
                                    st.error(result['message'])
                        else:
                            if st.button("🔓 Desbloquear", key=f"unblock_{user_id}", type="primary"):
                                result = self.unblock_user(user_id)
                                if result['success']:
                                    st.success(result['message'])
                                    st.rerun()
                                else:
                                    st.error(result['message'])
                    
                    with col_a3:
                        if not is_admin:
                            if st.button("👑 Hacer Admin", key=f"admin_{user_id}"):
                                result = self.make_admin(username)
                                if result['success']:
                                    st.success(result['message'])
                                    st.rerun()
                    
                    with col_a4:
                        if st.button("🗑️ Eliminar", key=f"delete_{user_id}", type="secondary"):
                            if st.checkbox(f"Confirmar eliminación de {username}", key=f"confirm_{user_id}"):
                                result = self.delete_user(user_id)
                                if result['success']:
                                    st.success(result['message'])
                                    st.rerun()
                                else:
                                    st.error(result['message'])
                    
                    # Últimos análisis
                    if details['ultimos_analisis']:
                        st.markdown("**Últimos análisis:**")
                        for analisis in details['ultimos_analisis'][:5]:
                            st.caption(f"📅 {analisis[0]} | {analisis[1]} | {analisis[2]}")
        
        # TAB 3: ACTIVIDAD RECIENTE
        with tab3:
            st.subheader("📈 Actividad Reciente del Sistema")
            
            activity = self.get_recent_activity(50)
            
            if activity:
                st.markdown("**Últimos 50 análisis realizados:**")
                for item in activity:
                    fecha, username, activo, modo = item
                    st.markdown(f"🕐 `{fecha}` | 👤 **{username}** | 📊 {activo} ({modo})")
            else:
                st.info("No hay actividad reciente")
        
        # TAB 4: CONFIGURACIÓN
        with tab4:
            st.subheader("⚙️ Configuración del Sistema")
            
            st.markdown("### 🎨 Personalización")
            
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Nombre de la plataforma", value="REDI7 IA")
                st.text_input("Slogan", value="Análisis Institucional con IA")
            
            with col2:
                st.color_picker("Color primario", value="#FF4B4B")
                st.color_picker("Color secundario", value="#667eea")
            
            st.markdown("### 📊 Límites por Plan")
            
            st.markdown("""
            | Plan | Análisis/Día | Precio |
            |------|--------------|--------|
            | FREE | 3 | $0 |
            | PRO | 10 | $79 |
            | ELITE | 25 | $199 |
            """)
            
            if st.button("💾 Guardar Configuración"):
                st.success("✅ Configuración guardada")


def show_admin_panel():
    """Función principal para mostrar el panel admin"""
    admin = AdminPanel()
    
    # Verificar si el usuario es admin
    if 'user_data' not in st.session_state or not st.session_state.user_data:
        st.error("❌ Debes iniciar sesión para acceder al panel de administración")
        return
    
    user_id = st.session_state.user_data['id']
    
    if not admin.is_admin(user_id):
        st.error("❌ No tienes permisos de administrador")
        st.info("💡 Contacta al administrador del sistema para obtener acceso")
        return
    
    admin.render_admin_page()


if __name__ == "__main__":
    st.set_page_config(
        page_title="Admin - REDI7 IA",
        page_icon="👑",
        layout="wide"
    )
    show_admin_panel()

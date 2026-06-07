// =========================================
// Sistema de Alertas Premium - La Paella Real
// Convierte mensajes de Django en SweetAlert2
// modals centrados con diseño premium.
// =========================================

(function() {
    'use strict';

    // Configuración de colores por tipo de mensaje
    const ALERT_CONFIG = {
        success: {
            icon: 'success',
            confirmButtonColor: '#6B1A2B',
            iconColor: '#27ae60',
            title: '¡Éxito!'
        },
        error: {
            icon: 'error',
            confirmButtonColor: '#6B1A2B',
            iconColor: '#e74c3c',
            title: 'Error'
        },
        warning: {
            icon: 'warning',
            confirmButtonColor: '#6B1A2B',
            iconColor: '#f39c12',
            title: 'Atención'
        },
        info: {
            icon: 'info',
            confirmButtonColor: '#6B1A2B',
            iconColor: '#3498db',
            title: 'Información'
        }
    };

    // Detectar si un mensaje contiene contraseña provisional
    function isProvisionalPassword(text) {
        return text.includes('contraseña provisional') || text.includes('Contraseña provisional');
    }

    // Extraer la contraseña del mensaje
    function extractPassword(text) {
        const match = text.match(/(?:contraseña provisional(?:\s+es)?:\s*)(\S+)/i);
        return match ? match[1] : null;
    }

    // Mostrar modal de contraseña provisional (estático, copiable)
    function showProvisionalPasswordModal(fullText, password) {
        // Extraer el mensaje base sin la contraseña
        const baseMessage = fullText.replace(/Su contraseña provisional es:\s*\S+/i, '').trim()
            || fullText.replace(/Contraseña provisional:\s*\S+/i, '').trim()
            || 'Registro completado correctamente.';

        Swal.fire({
            icon: 'success',
            title: '¡Registro Exitoso!',
            html: `
                <p style="color:#555; font-size:0.95rem; margin-bottom:1.2rem;">${baseMessage.replace(/\.$/, '')}.</p>
                <div style="
                    background: linear-gradient(135deg, #fdf2f8, #fce7f3);
                    border: 2px dashed #6B1A2B;
                    border-radius: 12px;
                    padding: 1.2rem 1.5rem;
                    margin: 0.5rem 0;
                    position: relative;
                ">
                    <p style="color:#6B1A2B; font-weight:600; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px; margin:0 0 0.5rem 0;">
                        🔑 Contraseña Provisional
                    </p>
                    <div style="display:flex; align-items:center; gap:0.75rem; justify-content:center;">
                        <code id="swal-pw-text" style="
                            font-size:1.4rem;
                            font-weight:700;
                            color:#1a1a2e;
                            background:#fff;
                            padding:0.5rem 1rem;
                            border-radius:8px;
                            letter-spacing:2px;
                            border:1px solid rgba(107,26,43,0.15);
                            user-select:all;
                        ">${password}</code>
                        <button id="swal-copy-btn" type="button" style="
                            background:#6B1A2B;
                            color:#fff;
                            border:none;
                            border-radius:8px;
                            padding:0.5rem 0.85rem;
                            cursor:pointer;
                            font-size:0.85rem;
                            display:flex;
                            align-items:center;
                            gap:0.35rem;
                            transition:all 0.2s;
                            white-space:nowrap;
                        " onmouseover="this.style.background='#8B2A3B'" onmouseout="this.style.background='#6B1A2B'">
                            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9.75a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184" />
                            </svg>
                            Copiar
                        </button>
                    </div>
                </div>
                <p style="color:#999; font-size:0.78rem; margin-top:0.8rem; font-style:italic;">
                    ⚠️ Guarda esta contraseña. El usuario deberá cambiarla en su primer inicio de sesión.
                </p>
            `,
            showConfirmButton: true,
            confirmButtonText: 'Entendido',
            confirmButtonColor: '#6B1A2B',
            allowOutsideClick: false,
            allowEscapeKey: false,
            customClass: {
                popup: 'swal-premium-popup',
                title: 'swal-premium-title'
            },
            didOpen: () => {
                const copyBtn = document.getElementById('swal-copy-btn');
                if (copyBtn) {
                    copyBtn.addEventListener('click', function() {
                        navigator.clipboard.writeText(password).then(() => {
                            this.innerHTML = `
                                <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                                </svg>
                                ¡Copiado!
                            `;
                            this.style.background = '#27ae60';
                            setTimeout(() => {
                                this.innerHTML = `
                                    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9.75a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184" />
                                    </svg>
                                    Copiar
                                `;
                                this.style.background = '#6B1A2B';
                            }, 2000);
                        });
                    });
                }
            }
        });
    }

    // Mostrar modal premium estándar (centrado, bonito)
    function showPremiumAlert(type, text) {
        const config = ALERT_CONFIG[type] || ALERT_CONFIG.info;

        Swal.fire({
            icon: config.icon,
            title: config.title,
            text: text,
            confirmButtonColor: config.confirmButtonColor,
            confirmButtonText: 'Aceptar',
            customClass: {
                popup: 'swal-premium-popup',
                title: 'swal-premium-title',
                confirmButton: 'swal-premium-btn'
            }
        });
    }

    // Procesar todos los mensajes de Django
    function processDjangoMessages() {
        if (typeof Swal === 'undefined') return;

        const msgs = document.querySelectorAll('.django-message');
        if (msgs.length === 0) return;

        // Separar mensajes provisionales de normales
        const provisionalMsgs = [];
        const normalMsgs = [];

        msgs.forEach(msg => {
            const text = msg.innerText.trim();
            const rawType = (msg.getAttribute('data-type') || '').toLowerCase();

            // Normalizar tipo
            let type = 'info';
            if (rawType.includes('error') || rawType === 'danger') type = 'error';
            else if (rawType.includes('success')) type = 'success';
            else if (rawType.includes('warning')) type = 'warning';
            else if (rawType.includes('info')) type = 'info';

            if (isProvisionalPassword(text)) {
                provisionalMsgs.push({ text, type });
            } else {
                normalMsgs.push({ text, type });
            }
        });

        // Mostrar mensajes provisionales con modal especial
        if (provisionalMsgs.length > 0) {
            const msg = provisionalMsgs[0];
            const password = extractPassword(msg.text);
            if (password) {
                showProvisionalPasswordModal(msg.text, password);
                return; // No mostrar otros mensajes al mismo tiempo
            }
        }

        // Mostrar mensajes normales encadenados
        if (normalMsgs.length === 1) {
            showPremiumAlert(normalMsgs[0].type, normalMsgs[0].text);
        } else if (normalMsgs.length > 1) {
            // Si hay múltiples, mostrar uno a uno
            let chain = Promise.resolve();
            normalMsgs.forEach(msg => {
                chain = chain.then(() => {
                    return Swal.fire({
                        icon: (ALERT_CONFIG[msg.type] || ALERT_CONFIG.info).icon,
                        title: (ALERT_CONFIG[msg.type] || ALERT_CONFIG.info).title,
                        text: msg.text,
                        confirmButtonColor: '#6B1A2B',
                        confirmButtonText: 'Aceptar',
                        customClass: {
                            popup: 'swal-premium-popup',
                            title: 'swal-premium-title'
                        }
                    });
                });
            });
        }
    }

    // Auto-inicializar al cargar el DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', processDjangoMessages);
    } else {
        processDjangoMessages();
    }

    // Exportar para uso manual
    window.PremiumAlerts = {
        show: showPremiumAlert,
        showPassword: showProvisionalPasswordModal,
        process: processDjangoMessages
    };

})();

<template>
  <div class="app-layout" :class="{ 'dark-theme': isDarkMode }">
    
    <!-- Custom Delete Single Modal -->
    <transition name="fade">
      <div v-if="showDeleteModal" class="modal-overlay delete-modal-overlay" @click.self="showDeleteModal = false">
        <div class="modal-box">
          <div class="modal-icon">🗑️</div>
          <h3>¿Eliminar conversación?</h3>
          <p>Esta acción no se puede deshacer y se eliminará esta consulta del historial.</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="showDeleteModal = false">Cancelar</button>
            <button class="btn-confirm" @click="confirmDelete">Sí, eliminar</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Custom Delete All History Modal -->
    <transition name="fade">
      <div v-if="showConfirmClearAllModal" class="modal-overlay delete-modal-overlay" @click.self="showConfirmClearAllModal = false">
        <div class="modal-box">
          <div class="modal-icon">⚠️</div>
          <h3>¿Eliminar todo el historial?</h3>
          <p>Se borrarán de forma definitiva todas las consultas y conversaciones registradas.</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="showConfirmClearAllModal = false">Cancelar</button>
            <button class="btn-confirm" @click="confirmClearAllHistory">Sí, borrar todo</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- 1. Modal Separado: Actividad (Estilo Gemini) -->
    <transition name="fade">
      <div v-if="showActivityModal" class="modal-overlay" @click.self="showActivityModal = false">
        <div class="modal-box gemini-settings-modal" style="max-width: 560px;">
          <div class="gemini-modal-top">
            <div class="gemini-modal-title">
              <h3>Actividad de TransiAI</h3>
            </div>
            <button class="gemini-close-x" @click="showActivityModal = false">✕</button>
          </div>

          <div class="gemini-settings-content">
            <div class="gemini-card">
              <div class="gemini-card-header">
                <span class="gemini-card-icon">🕒</span>
                <div>
                  <h4>Mantén la actividad</h4>
                  <p>Guardar tu actividad te permite retomar las conversaciones donde las dejaste y respalda las consultas.</p>
                </div>
              </div>
              <div class="gemini-activity-actions">
                <div class="gemini-activity-meta">
                  <span> Control de privacidad de sesión</span>
                </div>
                <button class="gemini-delete-activity-btn" @click="showConfirmClearAllModal = true">
                  Borrar actividad
                </button>
              </div>
            </div>

            <div class="activity-section-title">
              <span>Consultas registradas</span>
              <span style="font-size: 11px; color: var(--text-secondary);">({{ conversations.length }} chats)</span>
            </div>

            <div class="activity-list">
              <div v-if="conversations.length === 0" style="text-align: center; color: var(--text-secondary); padding: 20px; font-size: 13px;">
                No hay actividad reciente registrada en la vista.
              </div>
              <div v-for="conv in conversations" :key="conv.id" class="activity-item">
                <div class="activity-item-header">
                  <span style="font-size: 12px; color: #0db37b; font-weight: 600;">TransiAI</span>
                  <div class="has-custom-tooltip">
                    <button class="activity-del-btn" @click.stop="deleteConversation(conv.id)" aria-label="Eliminar consulta">
                      ✕
                    </button>
                    <div class="custom-tooltip-pill tooltip-left">
                      Eliminar consulta
                    </div>
                  </div>
                </div>
                <div class="activity-item-query">{{ conv.title || 'Consulta de tránsito' }}</div>
                <div class="activity-item-footer">
                  <span>🕒 {{ conv.createdAt ? conv.createdAt.substring(11, 16) : 'Reciente' }}</span>
                  <span>•</span>
                  <span>Detalles</span>
                </div>
              </div>
            </div>
          </div>

          <div class="gemini-modal-bottom-actions">
            <button class="btn-primary-green" @click="showActivityModal = false">
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- 2. Modal Separado: Información del Modelo -->
    <transition name="fade">
      <div v-if="showModelModal" class="modal-overlay" @click.self="showModelModal = false">
        <div class="modal-box gemini-settings-modal" style="max-width: 580px;">
          <div class="gemini-modal-top">
            <div class="gemini-modal-title">
              <h3>Información del Modelo de IA</h3>
            </div>
            <button class="gemini-close-x" @click="showModelModal = false">✕</button>
          </div>

          <div class="gemini-settings-content">
            <!-- Tarjeta 1: Motor LLM -->
            <div class="gemini-card">
              <div class="gemini-card-header">
                <span class="gemini-card-icon">🧠</span>
                <div>
                  <h4>Motor de Lenguaje (LLM)</h4>
                  <p>Inferencia avanzada en tiempo real con Google Gemini</p>
                </div>
              </div>
              <div class="model-badge-container" style="margin: 8px 0 10px 0;">
                <span class="model-badge-name">{{ selectedModel }}</span>
                <span class="model-badge-status">● En línea</span>
              </div>
              <p style="font-size: 12.5px; color: var(--text-secondary); line-height: 1.5; margin: 0;">
                Implementa <strong>Gemini 3.1 Flash Lite</strong>, un modelo multimodal de última generación optimizado para entregar respuestas con latencia ultra reducida, alta comprensión de lenguaje natural y procesamiento contextual especializado.
              </p>
            </div>

            <!-- Tarjeta 2: Arquitectura RAG -->
            <div class="gemini-card">
              <div class="gemini-card-header">
                <span class="gemini-card-icon">⚡</span>
                <div>
                  <h4>Arquitectura RAG (Generación Aumentada por Recuperación)</h4>
                  <p>Fundamentación jurídica exacta sin alucinaciones</p>
                </div>
              </div>
              <p style="font-size: 12.5px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 10px;">
                Para garantizar que el modelo no invente leyes ni cometa errores normativos, el sistema aplica un flujo RAG de 4 fases:
              </p>
              <div class="rag-flow-steps">
                <div class="rag-step-item">
                  <span class="rag-step-num">1</span>
                  <div><strong>Consulta del Usuario:</strong> El sistema procesa la consulta y genera un embedding vectorial matemático semántico.</div>
                </div>
                <div class="rag-step-item">
                  <span class="rag-step-num">2</span>
                  <div><strong>Recuperación en Qdrant:</strong> Busca en la base de datos vectorial los fragmentos de leyes más similares por distancia coseno.</div>
                </div>
                <div class="rag-step-item">
                  <span class="rag-step-num">3</span>
                  <div><strong>Inyección de Contexto:</strong> Ensambla los artículos legales pertinentes directamente en el prompt del sistema.</div>
                </div>
                <div class="rag-step-item">
                  <span class="rag-step-num">4</span>
                  <div><strong>Respuesta con Rigor Legal:</strong> Gemini genera una explicación detallada citando artículos del COIP y LOTTTSV con su análisis de gravedad.</div>
                </div>
              </div>
            </div>

            <!-- Tarjeta 3: Stack Tecnológico -->
            <div class="gemini-card">
              <div class="gemini-card-header">
                <span class="gemini-card-icon">🛠️</span>
                <div>
                  <h4>Infraestructura y Persistencia</h4>
                  <p>Orquestación en backend y almacenamiento seguro</p>
                </div>
              </div>
              <div class="gemini-info-row">
                <strong>Orquestador Backend:</strong> Spring Boot 4 + Spring AI (Java 17/21)
              </div>
              <div class="gemini-info-row">
                <strong>Base de Datos Vectorial:</strong> Qdrant VectorStore (Embeddings multilingües)
              </div>
              <div class="gemini-info-row">
                <strong>Base de Datos Relacional:</strong> PostgreSQL (Almacenamiento seguro del sistema)
              </div>
              <div class="gemini-info-row">
                <strong>Streaming de Tokens:</strong> Server-Sent Events (SSE) para respuesta en tiempo real
              </div>
            </div>
          </div>

          <div class="gemini-modal-bottom-actions">
            <button class="btn-primary-green" @click="showModelModal = false">
              Entendido
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- 3. Modal Separado: Marco Legal -->
    <transition name="fade">
      <div v-if="showLegalModal" class="modal-overlay" @click.self="showLegalModal = false">
        <div class="modal-box gemini-settings-modal">
          <div class="gemini-modal-top">
            <div class="gemini-modal-title">
              <h3>Marco Legal de Tránsito</h3>
            </div>
            <button class="gemini-close-x" @click="showLegalModal = false">✕</button>
          </div>

          <div class="gemini-settings-content">
            <div class="gemini-card">
              <div class="gemini-card-header">
                <span class="gemini-card-icon">📜</span>
                <div>
                  <h4>Leyes y Reglamentos Integrados</h4>
                  <p>Normativas indexadas en la base vectorial para resolver dudas jurídicas</p>
                </div>
              </div>
              <ul class="legal-framework-list" style="margin-top: 12px; gap: 8px;">
                <li>📜 <strong>COIP:</strong> Código Orgánico Integral Penal (Infracciones de Tránsito)</li>
                <li>🚗 <strong>LOTTTSV:</strong> Ley Orgánica de Transporte Terrestre, Tránsito y Seguridad Vial</li>
                <li>📋 <strong>Reglamento:</strong> Reglamento General para la aplicación de la LOTTTSV</li>
                <li>💼 <strong>Código del Trabajo:</strong> Indemnizaciones por accidentes y fallecimiento laboral</li>
                <li>⚖️ <strong>COGEP:</strong> Código Orgánico General de Procesos</li>
                <li>🇪🇨 <strong>Constitución:</strong> Constitución de la República del Ecuador</li>
              </ul>
            </div>
          </div>

          <div class="gemini-modal-bottom-actions">
            <button class="btn-primary-green" @click="showLegalModal = false">
              Entendido
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- 4. Modal de Éxito: Check Azul estilo Gemini -->
    <transition name="fade">
      <div v-if="showSuccessClearModal" class="modal-overlay" @click.self="showSuccessClearModal = false">
        <div class="modal-box gemini-success-modal">
          <div class="gemini-success-check-circle">✓</div>
          <h3 style="font-size: 20px; font-weight: 700; margin-bottom: 8px;">Eliminación completada</h3>
          <p style="font-size: 13.5px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 20px;">
            La actividad seleccionada se ha eliminado y ya no aparece en tu historial. Puedes iniciar una nueva conversación cuando lo desees.
          </p>
          <div class="gemini-privacy-hint">
            <span style="font-size: 16px;"></span>
            <span>Tu pantalla actual se ha despejado. Puedes comenzar una nueva consulta cuando lo desees.</span>
          </div>
          <div class="modal-actions" style="margin-top: 24px;">
            <button class="gemini-blue-btn" @click="showSuccessClearModal = false">
              Entiendo
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Mobile Drawer Backdrop Overlay -->
    <transition name="fade">
      <div v-if="isMobileSidebarOpen || isMobileWidgetsOpen" class="mobile-drawer-overlay" @click="closeMobileDrawers"></div>
    </transition>

    <!-- ══════════ LEFT COLUMN (Sidebar) ══════════ -->
    <aside class="sidebar" :class="{ 'mobile-open': isMobileSidebarOpen }">
      <div class="brand-header">
        <div class="brand-header-info" @click="$router.push('/')" style="cursor: pointer;">
          <div class="has-custom-tooltip">
            <div class="brand-icon">
              <img :src="carrosLogo" alt="Logo" style="width: 28px; height: auto;" />
            </div>
            <div class="custom-tooltip-pill tooltip-bottom">
              Volver al inicio
            </div>
          </div>
          <div class="brand-text">
            <span class="brand-subtitle">ASISTENTE</span>
            <span class="brand-title">TransiAI</span>
            <span class="brand-slogan">Información que te mueve <span class="dot"></span></span>
          </div>
        </div>
        <button class="mobile-drawer-close-btn" @click="isMobileSidebarOpen = false" title="Cerrar menú">✕</button>
      </div>

      <button class="new-chat-btn" @click="newConversation">
        💬 Nuevo chat
      </button>

      <div class="nav-menu">
        <div class="recent-chats-header">
          Recientes
        </div>
        
        <!-- Conversation List with Gemini Slider & Hover Tooltip -->
        <div class="conversations-list">
          <div v-if="conversations.length === 0" style="padding: 14px 10px; font-size: 12px; color: #64748b; text-align: center;">
            No hay conversaciones recientes
          </div>
          <div v-for="conv in conversations" :key="conv.id"
               class="conv-item"
               :class="{ active: conv.id === activeConversationId }"
               @click="selectConversation(conv.id)">
            <span class="conv-title"
                  @mouseenter="onConvMouseEnter($event, conv.title)"
                  @mouseleave="onConvMouseLeave">
              {{ conv.title || 'Consulta de tránsito' }}
            </span>
            <div class="has-custom-tooltip">
              <button class="conv-del-btn"
                      @click.stop="deleteConversation(conv.id)"
                      @mouseenter="onConvMouseLeave"
                      aria-label="Eliminar consulta">
                ✕
              </button>
              <div class="custom-tooltip-pill tooltip-top align-right">
                Eliminar consulta
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Bottom left: Settings, Return home, and footer -->
      <div class="sidebar-footer">
        <div class="settings-anchor">
          <!-- Popover Dropdown Menu (Gemini Style) -->
          <transition name="pop-up">
            <div v-if="showSettingsMenu" class="gemini-popover-menu" @click.stop>
              <!-- Item 1: Actividad -->
              <div class="gemini-menu-item" @click="openActivityModal">
                <span class="menu-icon">🕒</span>
                <span class="menu-label">Actividad</span>
              </div>

              <!-- Item 2: Tema (con submenú interactivo) -->
              <div class="gemini-menu-item has-submenu" @mouseenter="showThemeSubmenu = true" @mouseleave="showThemeSubmenu = false">
                <div class="menu-item-row">
                  <span class="menu-icon">☼</span>
                  <span class="menu-label">Tema</span>
                  <span class="menu-arrow">▶</span>
                </div>
                <!-- Submenú de Tema -->
                <transition name="fade">
                  <div v-if="showThemeSubmenu" class="gemini-submenu">
                    <div class="gemini-submenu-item" :class="{ 'is-selected': !isDarkMode }" @click="isDarkMode = false">
                      <span>Luz</span>
                      <span v-if="!isDarkMode" class="check-mark">✓</span>
                    </div>
                    <div class="gemini-submenu-item" :class="{ 'is-selected': isDarkMode }" @click="isDarkMode = true">
                      <span>Oscuro</span>
                      <span v-if="isDarkMode" class="check-mark">✓</span>
                    </div>
                  </div>
                </transition>
              </div>

              <!-- Item 3: Información del Modelo -->
              <div class="gemini-menu-item" @click="openModelModal">
                <span class="menu-icon">🧠</span>
                <span class="menu-label">Información del Modelo</span>
              </div>

              <!-- Item 4: Marco Legal -->
              <div class="gemini-menu-item" @click="openLegalModal">
                <span class="menu-icon">⚖️</span>
                <span class="menu-label">Marco Legal de Tránsito</span>
              </div>

              <div class="gemini-menu-divider"></div>

              <!-- Item 5: Ubicación detectada dinámicamente -->
              <div class="gemini-menu-item location-item" @click="fetchWeather" title="Ubicación">
                <span class="location-dot">●</span>
                <div class="location-text-col">
                  <span class="location-name">{{ weatherLocationName }}</span>
                  <span class="location-sub">Detectado vía IP / GPS</span>
                </div>
              </div>
            </div>
          </transition>

          <div class="sidebar-footer-row">
            <div class="settings-gear-container" :class="{ 'menu-open': showSettingsMenu }">
              <button class="settings-gear-circle-btn" :class="{ active: showSettingsMenu }" @click.stop="showSettingsMenu = !showSettingsMenu" aria-label="Ajustes">
                ⚙️
              </button>
              <div class="settings-tooltip-pill">
                Ajustes
              </div>
            </div>
          </div>
        </div>

        <div class="footer-text">
          Hecho para una movilidad<br>más segura y eficiente 💚
        </div>
      </div>

      <!-- Gemini Floating Tooltip on Hover for History items -->
      <transition name="fade">
        <div v-if="hoveredConvTitle && !isMobileSidebarOpen"
             class="conv-floating-tooltip"
             :style="{ top: `${hoveredTooltipTop}px` }">
          {{ hoveredConvTitle }}
        </div>
      </transition>
    </aside>

    <!-- ══════════ MAIN CHAT AREA (CENTER PANEL) ══════════ -->
    <main class="main-content">
      <div class="top-bar">
        <div class="top-bar-left">
          <button class="mobile-nav-toggle" @click="isMobileSidebarOpen = true" title="Abrir menú">
            <span class="hamburger-bar"></span>
            <span class="hamburger-bar"></span>
            <span class="hamburger-bar"></span>
          </button>
          <div class="mobile-brand-info" @click="$router.push('/')" title="Ir al Inicio">
            <img :src="carrosLogo" alt="Logo" class="mobile-brand-logo" />
            <span class="mobile-brand-title">TransiAI</span>
          </div>
        </div>

        <div class="top-bar-right">
          <button class="mobile-widgets-toggle" @click="isMobileWidgetsOpen = true" title="Ver clima y tiempos de viaje">
            <span style="font-size: 15px;">🌤️</span>
            <span class="mobile-widgets-label">Rutas & Clima</span>
          </button>
          <div class="user-profile">
            <span>Bienvenido</span>
            <div class="user-avatar">👨‍💼</div>
          </div>
        </div>
      </div>

      <div class="chat-area" ref="chatArea">
        
        <!-- Welcome Screen -->
        <div v-if="currentMessages.length === 0 && !isStreaming" class="welcome-container" :class="{ 'chat-reset-flash': isResettingChat }">
          <div class="welcome-banner">
            <div class="welcome-text">
              <h2>Hola, estoy aquí para <span>ayudarte</span></h2>
              <p>con información de tránsito en tiempo real</p>
            </div>
            <div class="welcome-robot">🤖</div>
          </div>
          
          <div class="suggestions-container">
            <button class="sug-btn sug-blue" @click="sendSuggestion(suggestedQuestions[0])">
              <span class="sug-icon">🪪</span><span class="sug-text">{{ suggestedQuestions[0] }}</span><span class="sug-arrow">></span>
            </button>
            <button class="sug-btn sug-green" @click="sendSuggestion(suggestedQuestions[1])">
              <span class="sug-icon">⏱️</span><span class="sug-text">{{ suggestedQuestions[1] }}</span><span class="sug-arrow">></span>
            </button>
            <button class="sug-btn sug-purple" @click="sendSuggestion(suggestedQuestions[2])">
              <span class="sug-icon">⚠️</span><span class="sug-text">{{ suggestedQuestions[2] }}</span><span class="sug-arrow">></span>
            </button>
          </div>
        </div>

        <!-- Messages List -->
        <div class="chat-messages" v-if="currentMessages.length > 0 || isStreaming">
          <div v-for="(msg, idx) in currentMessages" :key="idx" class="message-wrapper">
            <div class="message" :class="msg.role">
              <div v-if="msg.role === 'assistant'" class="bot-avatar">🤖</div>
              <div class="message-bubble">
                <div v-html="formatMessage(msg.content)"></div>
              </div>
              <div v-if="msg.role === 'user'" class="user-avatar-small">👨‍💼</div>
            </div>
            
            <!-- INFRACTION ANALYZER -->
            <transition name="fade">
              <div v-if="msg.role === 'assistant' && getInfractionData(msg.content)" class="infraction-card">
                
                <div class="infraction-header">
                  ⚖️ ANALIZADOR DE INFRACCIONES
                </div>

                <div class="infraction-top-centered">
                  <div class="gauge-container">
                    <!-- Advanced SVG-like Gauge -->
                    <div class="gauge-meter">
                      <div class="gauge-arcs">
                        <div class="gauge-arc arc-green"></div>
                        <div class="gauge-arc arc-orange"></div>
                        <div class="gauge-arc arc-red"></div>
                      </div>
                      <div class="gauge-needle" :style="{ transform: getNeedleAngle(getInfractionData(msg.content).gravedad) }">
                        <div class="needle-base"></div>
                      </div>
                    </div>

                    <div class="gauge-value" :class="getGravityClass(getInfractionData(msg.content).gravedad)">
                      {{ getInfractionData(msg.content).gravedad }}
                    </div>
                    <div class="gauge-subtitle">Nivel de gravedad</div>
                  </div>
                </div>

                <div class="infraction-grid-2">
                  <div class="ig-item">
                    <span class="ig-label">Contexto detectado</span>
                    <span class="ig-value normal" style="font-size: 14px;">{{ getInfractionData(msg.content).contexto }}</span>
                  </div>
                  <div class="ig-item">
                    <span class="ig-label">Base Legal Principal</span>
                    <span class="ig-value blue" style="font-size: 14px;">{{ getInfractionData(msg.content).baseLegal }}</span>
                  </div>
                </div>
                
                <div class="infraction-details">
                  <div class="detail-box box-info" v-if="getInfractionData(msg.content).puntosClave && getInfractionData(msg.content).puntosClave.length > 0">
                    <h4>ℹ️ Puntos Claves</h4>
                    <ul>
                      <li v-for="(pt, i) in getInfractionData(msg.content).puntosClave" :key="i">{{ pt }}</li>
                    </ul>
                  </div>
                  <div class="detail-box box-cons" v-if="getInfractionData(msg.content).consecuencias && getInfractionData(msg.content).consecuencias.length > 0">
                    <h4>⚠️ Consecuencias Posibles</h4>
                    <ul>
                      <li v-for="(pt, i) in getInfractionData(msg.content).consecuencias" :key="i">{{ pt }}</li>
                    </ul>
                  </div>
                  <div class="detail-box box-reco" v-if="getInfractionData(msg.content).recomendaciones && getInfractionData(msg.content).recomendaciones.length > 0">
                    <h4>🛡️ Recomendaciones</h4>
                    <ul>
                      <li v-for="(pt, i) in getInfractionData(msg.content).recomendaciones" :key="i">{{ pt }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </transition>
          </div>
          
          <!-- Streaming Message -->
          <div v-if="isStreaming" class="message assistant">
             <div class="bot-avatar">🤖</div>
             <div class="message-bubble">
               <span v-html="formatMessage(streamingContent)"></span>
               <div class="typing-indicator" v-if="!streamingContent">
                 <span class="dot"></span>
                 <span class="dot"></span>
                 <span class="dot"></span>
               </div>
             </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="input-area">
        <div class="input-container">
          <input
              type="file"
              ref="fileInputRef"
              style="display: none;"
              accept=".pdf,.txt,.docx,.doc,.rtf,.csv"
              @change="handleFileUpload"
          />
          <div class="has-custom-tooltip">
            <button
                class="upload-btn"
                @click="$refs.fileInputRef.click()"
                :disabled="isUploading || isStreaming"
                aria-label="Adjuntar documento"
                type="button"
            >
              <img v-if="!isUploading" :src="clipIcon" alt="Adjuntar" style="width: 20px; height: 20px; object-fit: contain; display: block;" />
              <span v-else class="spin-icon">⏳</span>
            </button>
            <div class="custom-tooltip-pill tooltip-top align-left">
              Adjuntar documento
            </div>
          </div>
          <textarea
              ref="inputTextarea"
              v-model="inputMessage"
              placeholder="Escribe tu pregunta sobre tránsito o adjunta un documento..."
              @input="adjustTextareaHeight"
              @keydown.enter.exact.prevent="sendMessage"
              :disabled="isStreaming"
              rows="1"
          ></textarea>
          <div class="has-custom-tooltip">
            <button class="send-btn" @click="sendMessage" :disabled="!inputMessage.trim() || isStreaming" aria-label="Enviar mensaje">
              ➤
            </button>
            <div class="custom-tooltip-pill tooltip-top align-right" v-if="inputMessage.trim() && !isStreaming">
              Enviar mensaje
            </div>
          </div>
        </div>
        <div v-if="uploadStatusMessage" :style="{ fontSize: '12px', marginTop: '6px', textAlign: 'center', color: uploadStatusColor, fontWeight: '600' }">
          {{ uploadStatusMessage }}
        </div>
        <div class="disclaimer">
          Información generada por IA.
        </div>
      </div>
    </main>

    <!-- ══════════ RIGHT PANEL (TOOLS) ══════════ -->
    <aside class="right-panel" :class="{ 'mobile-open': isMobileWidgetsOpen }">
      <div class="mobile-panel-header">
        <div class="mobile-panel-title">
          <span>🌤️</span>
          <h3>Rutas y Clima</h3>
        </div>
        <button class="mobile-drawer-close-btn panel-close" @click="isMobileWidgetsOpen = false" title="Cerrar panel">✕</button>
      </div>
      <!-- Weather Widget (Detección dinámica en todo Ecuador) -->
      <div class="widget-card weather">
        <div class="widget-title-row">
          <div class="widget-title-text">
            <span>Clima</span>
            <span style="color: #6ee7b7; font-size: 30px;">●</span>
          </div>
          <div class="has-custom-tooltip">
            <button class="refresh-loc-btn" @click="fetchWeather" aria-label="Ubicación">
              <span :class="{ 'spin-icon': isLocatingWeather }">🔄</span>
            </button>
            <div class="custom-tooltip-pill tooltip-left">
              Ubicación
            </div>
          </div>
        </div>



        <div class="weather-info-box" v-if="weatherData && !isLocatingWeather">
          <div class="weather-top-row">
            <span class="weather-big-emoji">{{ weatherCondition.emoji }}</span>
            <div class="weather-temp-col">
              <span class="weather-temp-num">{{ Math.round(weatherData.temperature) }}°C</span>
              <span class="weather-cond-label">{{ weatherCondition.label }}</span>
            </div>
          </div>
          <div class="weather-details-row">
            <div class="weather-detail-item">
              📍 <strong>{{ weatherLocationName }}</strong>
            </div>
            <div class="weather-detail-item">
              💨 Viento: <span>{{ weatherData.windspeed }} km/h</span>
            </div>
          </div>
        </div>

        <div v-else-if="isLocatingWeather" class="weather-loading">
          ⏳ Detectando ubicación y consultando clima...
        </div>

        <div v-else class="weather-loading">
          ⚠️ No se pudo cargar el clima.
          <button @click="fetchWeather" class="retry-weather-btn">Reintentar</button>
        </div>
      </div>

      <!-- Rutas y Navegación (Tiempos de Viaje TomTom en Vivo) -->
      <div class="widget-card">
        <div class="widget-title">
          Tiempos de Viaje
          <span class="see-all">En vivo (TomTom)</span>
        </div>
        <div class="widget-list" v-if="!isLoadingRoutes && routeEstimates.length > 0">
          <a v-for="(route, idx) in routeEstimates" :key="idx"
             :href="route.mapsUrl" target="_blank"
             class="widget-list-item"
             :class="{ 'border-none': idx === routeEstimates.length - 1 }"
             style="text-decoration: none; padding: 10px 0;">
            <div style="display: flex; flex-direction: column; gap: 2px;">
              <span style="font-weight: 600; font-size: 13px;">{{ route.title }}</span>
              <div style="display: flex; align-items: center; gap: 6px; font-size: 11px;">
                <span v-if="route.distanceText" style="color: var(--text-secondary); font-weight: 600;">
                  📍 {{ route.distanceText }}
                </span>
                <span :style="{ color: route.trafficStatus.color, fontWeight: '500' }">
                  {{ route.trafficStatus.text }}
                </span>
              </div>
            </div>
            <div style="display: flex; align-items: center; gap: 4px;">
              <span style="font-weight: 800; font-size: 13px; color: var(--text-primary); white-space: nowrap;">{{ route.timeText }}</span>
              <span class="arrow" style="font-size: 12px;">🧭</span>
            </div>
          </a>
        </div>
        <div class="widget-list" v-else-if="isLoadingRoutes">
          <div class="widget-list-item border-none" style="font-size: 11px; color: #64748b; padding-bottom: 0;">
            ⏳ Calculando tiempos de viaje...
          </div>
        </div>
        <div class="widget-list" v-else>
          <a href="https://www.google.com/maps" target="_blank" class="widget-list-item border-none" style="text-decoration: none;">
            <span>🗺️ Abrir Google Maps</span><span class="arrow">🧭</span>
          </a>
        </div>
      </div>

    </aside>

  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue';
import { API_BASE_URL } from '../config.js';
import carrosLogo from '../assets/carros.png';
import clipIcon from '../assets/clip.png';

const WMO_LABELS = {
  0: 'Despejado', 1: 'Mayormente despejado', 2: 'Parcialmente nublado', 3: 'Nublado',
  45: 'Niebla', 48: 'Niebla helada',
  51: 'Llovizna ligera', 53: 'Llovizna moderada', 55: 'Llovizna densa',
  61: 'Lluvia ligera', 63: 'Lluvia moderada', 65: 'Lluvia fuerte',
  71: 'Nieve ligera', 73: 'Nieve moderada', 75: 'Nieve fuerte', 77: 'Granizo fino',
  80: 'Chubascos ligeros', 81: 'Chubascos moderados', 82: 'Chubascos fuertes',
  85: 'Granizada ligera', 86: 'Granizada fuerte',
  95: 'Tormenta eléctrica', 96: 'Tormenta con granizo', 99: 'Tormenta con granizo'
};

export default {
  name: 'App',
  setup() {
    const conversations = ref([]);
    const activeConversationId = ref(null);
    const localMessages = ref({}); 
    const inputMessage = ref('');
    const isStreaming = ref(false);
    const streamingContent = ref('');
    const chatArea = ref(null);
    const inputTextarea = ref(null);
    const isResettingChat = ref(false);
    const showSettingsMenu = ref(false);
    const showThemeSubmenu = ref(false);
    const showActivityModal = ref(false);
    const showModelModal = ref(false);
    const showLegalModal = ref(false);
    const showSuccessClearModal = ref(false);
    const selectedModel = ref('gemini-3.1-flash-lite');
    const weatherData = ref(null);
    const weatherLocationName = ref('Detectando...');
    const isLocatingWeather = ref(false);
    const trafficAlerts = ref([]);
    const isDarkMode = ref(false);
    const isMobileSidebarOpen = ref(false);
    const isMobileWidgetsOpen = ref(false);

    function closeMobileDrawers() {
      isMobileSidebarOpen.value = false;
      isMobileWidgetsOpen.value = false;
    }

    // TomTom Routing State
    const routeEstimates = ref([]);
    const isLoadingRoutes = ref(false);

    // TomTom Map State (Option 2)
    const tomtomMapRef = ref(null);
    const isMapLoaded = ref(false);
    let ttMapInstance = null;

    function getWeatherCondition(code, isDay = 1) {
      if (code === undefined || code === null) return { label: 'Sin datos', emoji: '🌡️' };
      
      const label = WMO_LABELS[code] || 'Clima variable';
      let emoji = '🌡️';

      if (code === 0) emoji = isDay ? '☀️' : '🌙';
      else if (code === 1) emoji = isDay ? '🌤️' : '🌙';
      else if (code === 2) emoji = isDay ? '⛅' : '☁️';
      else if (code === 3) emoji = '☁️';
      else if (code === 45 || code === 48) emoji = '🌫️';
      else if (code >= 51 && code <= 57) emoji = isDay ? '🌦️' : '🌧️';
      else if (code >= 61 && code <= 67) emoji = '🌧️';
      else if (code >= 71 && code <= 77) emoji = '❄️';
      else if (code >= 80 && code <= 82) emoji = isDay ? '🌦️' : '🌧️';
      else if (code >= 85 && code <= 86) emoji = '🌨️';
      else if (code >= 95 && code <= 99) emoji = '⛈️';

      const customLabel = (!isDay && code <= 1) ? 'Noche despejada' : (!isDay && code === 2) ? 'Noche parcialmente nublada' : label;

      return { label: customLabel, emoji };
    }

    const weatherCondition = computed(() => {
      if (!weatherData.value || weatherData.value.weathercode === undefined) {
        return { label: 'Sin datos', emoji: '🌡️' };
      }
      // Detección automática del ciclo día/noche de la ubicación
      let isDay = weatherData.value.is_day;
      if (isDay === undefined) {
        const currentHour = new Date().getHours();
        isDay = (currentHour >= 6 && currentHour < 18.5) ? 1 : 0;
      }
      return getWeatherCondition(weatherData.value.weathercode, isDay);
    });
    
    // Modal state
    const showDeleteModal = ref(false);
    const showConfirmClearAllModal = ref(false);
    const convToDelete = ref(null);

    const suggestedQuestions = [
      "¿Qué es una infracción de tránsito?",
      "¿Cuáles son los limites de velocidad permitidos?",
      "¿Qué hacer en caso de un accidente?"
    ];

    const currentMessages = computed(() => {
      if (!activeConversationId.value) return [];
      return localMessages.value[activeConversationId.value] || [];
    });

    onMounted(async () => {
      fetchWeather();
      await loadConversations();
      window.addEventListener('click', () => {
        showSettingsMenu.value = false;
        showThemeSubmenu.value = false;
      });
    });

    // ─── API FETCHING ────────────────────────────────────────────────────────
    async function loadConversations() {
      try {
        const res = await fetch(`${API_BASE_URL}/api/conversations`);
        if (res.ok) {
          const allConvs = await res.json();
          const hiddenIds = new Set(JSON.parse(localStorage.getItem('transiai_hidden_conv_ids') || '[]'));

          // Retirar clave temporal de borrado para que cualquier consulta nueva siempre sea visible
          if (localStorage.getItem('transiai_activity_cleared_at')) {
            localStorage.removeItem('transiai_activity_cleared_at');
          }

          conversations.value = allConvs.filter(c => !hiddenIds.has(c.id));
        }
      } catch (e) {
        console.error('Error cargando conversaciones:', e);
      }
    }

    async function selectConversation(id) {
      closeMobileDrawers();
      activeConversationId.value = id;
      streamingContent.value = '';

      if (!localMessages.value[id] || localMessages.value[id].length === 0) {
        try {
          const res = await fetch(`${API_BASE_URL}/api/conversations/${id}/messages`);
          if (res.ok) {
            localMessages.value[id] = await res.json();
          }
        } catch (e) {
          console.error('Error cargando mensajes:', e);
          localMessages.value[id] = [];
        }
      }
      await nextTick();
      scrollToBottom();
    }

    function deleteConversation(id) {
      convToDelete.value = id;
      showDeleteModal.value = true;
    }

    async function confirmDelete() {
      const id = convToDelete.value;
      if (!id) return;
      
      try {
        await fetch(`${API_BASE_URL}/api/conversations/${id}`, { method: 'DELETE' });
      } catch (e) {
        console.error('Error eliminando conversación en backend:', e);
      } finally {
        conversations.value = conversations.value.filter(c => c.id !== id);
        delete localMessages.value[id];

        const hiddenIds = JSON.parse(localStorage.getItem('transiai_hidden_conv_ids') || '[]');
        if (!hiddenIds.includes(id)) {
          hiddenIds.push(id);
          localStorage.setItem('transiai_hidden_conv_ids', JSON.stringify(hiddenIds));
        }

        if (activeConversationId.value === id) {
          activeConversationId.value = null;
        }
        showDeleteModal.value = false;
        convToDelete.value = null;
      }
    }

    async function fetchWeatherForCoords(lat, lon, customName = null) {
      try {
        fetchRoutesInfo(lat, lon); 
        initTomTomMap(lat, lon); 
        const res = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        weatherData.value = data.current_weather;

        if (customName) {
          weatherLocationName.value = customName;
        } else {
          try {
            const geoRes = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=es`);
            if (geoRes.ok) {
              const geoData = await geoRes.json();
              const place = geoData.city || geoData.locality || geoData.principalSubdivision || geoData.countryName;
              weatherLocationName.value = place ? place : 'Ubicación actual';
            } else {
              weatherLocationName.value = 'Ubicación actual';
            }
          } catch (geoErr) {
            console.warn('Geocodificación inversa fallida:', geoErr);
            weatherLocationName.value = 'Ubicación actual';
          }
        }
      } catch (e) {
        console.error('Error obteniendo clima:', e);
        weatherData.value = null;
      }
    }

    async function fetchWeather() {
      isLocatingWeather.value = true;

      if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
          async (position) => {
            try {
              const lat = position.coords.latitude;
              const lon = position.coords.longitude;
              await fetchWeatherForCoords(lat, lon);
            } catch (e) {
              console.error('Error procesando coordenadas GPS:', e);
              await fetchWeatherForCoords(-0.2298, -78.5249, 'Quito (Predeterminado)');
            } finally {
              isLocatingWeather.value = false;
            }
          },
          async (err) => {
            console.warn('Geolocalización rechazada o no disponible. Usando Quito predeterminado:', err.message);
            await fetchWeatherForCoords(-0.2298, -78.5249, 'Quito (Predeterminado)');
            isLocatingWeather.value = false;
          },
          { timeout: 8000, enableHighAccuracy: true }
        );
      } else {
        await fetchWeatherForCoords(-0.2298, -78.5249, 'Quito (Predeterminado)');
        isLocatingWeather.value = false;
      }
    }

    async function fetchRoutesInfo(userLat = -0.2298, userLon = -78.5249) {
      isLoadingRoutes.value = true;
      try {
        const apiKey = import.meta.env.VITE_TOMTOM_API_KEY;
        const destinations = [
          { title: '✈️ Aeropuerto Mariscal Sucre', destLat: -0.1292, destLon: -78.3575 },
          { title: '🎓 Universidad Central del Ecuador', destLat: -0.1997, destLon: -78.5061 },
          { title: '🚌 Terminal Terrestre Quitumbe', destLat: -0.2789, destLon: -78.5442 }
        ];

        const results = await Promise.all(
          destinations.map(async (d) => {
            const mapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${userLat},${userLon}&destination=${d.destLat},${d.destLon}`;
            try {
              const url = `https://api.tomtom.com/routing/1/calculateRoute/${userLat},${userLon}:${d.destLat},${d.destLon}/json?key=${apiKey}&traffic=true`;
              const res = await fetch(url);
              if (!res.ok) throw new Error(`HTTP ${res.status}`);
              const data = await res.json();
              const summary = data.routes?.[0]?.summary;
              if (summary) {
                const totalMinutes = Math.round(summary.travelTimeInSeconds / 60);
                let timeText = '';
                if (totalMinutes >= 60) {
                  const hours = Math.floor(totalMinutes / 60);
                  const mins = totalMinutes % 60;
                  timeText = mins > 0 ? `${hours} h ${mins} min` : `${hours} h`;
                } else {
                  timeText = `${totalMinutes} min`;
                }

                const lengthMeters = summary.lengthInMeters;
                let distanceText = '';
                if (lengthMeters !== undefined && lengthMeters !== null) {
                  const km = lengthMeters / 1000;
                  distanceText = km < 10 ? `${km.toFixed(1)} km` : `${Math.round(km)} km`;
                }

                const delayMin = Math.round((summary.trafficDelayInSeconds || 0) / 60);
                let trafficStatus = { text: '🟢 Fluido', color: '#10b981' };
                if (delayMin > 5) {
                  trafficStatus = { text: `🔴 +${delayMin} min tráfico`, color: '#ef4444' };
                } else if (delayMin > 1) {
                  trafficStatus = { text: `🟡 +${delayMin} min moderado`, color: '#f59e0b' };
                }
                return {
                  title: d.title,
                  timeText,
                  distanceText,
                  trafficStatus,
                  mapsUrl
                };
              }
            } catch (e) {
              console.warn(`Error calculando ruta para ${d.title}:`, e);
            }
            return {
              title: d.title,
              timeText: 'N/D',
              trafficStatus: { text: '🧭 Ver mapa', color: '#64748b' },
              mapsUrl
            };
          })
        );

        routeEstimates.value = results;
      } catch (e) {
        console.error('Error calculando estimado de rutas TomTom:', e);
      } finally {
        isLoadingRoutes.value = false;
      }
    }

    //Fallback para que no se rompa si no hay API Key

    function initTomTomMap(lat = -0.2298, lon = -78.5249) {
      const apiKey = import.meta.env.VITE_TOMTOM_API_KEY;
      if (!apiKey) return;

      if (!window.tt) {
        const cssLink = document.createElement('link');
        cssLink.rel = 'stylesheet';
        cssLink.href = 'https://api.tomtom.com/maps-sdk-for-web/cdn/6.x/6.25.0/maps/maps.css';
        document.head.appendChild(cssLink);

        const jsScript = document.createElement('script');
        jsScript.src = 'https://api.tomtom.com/maps-sdk-for-web/cdn/6.x/6.25.0/maps/maps-web.min.js';
        jsScript.onload = () => createTomTomMap(apiKey, lat, lon);
        document.head.appendChild(jsScript);
      } else {
        createTomTomMap(apiKey, lat, lon);
      }
    }

    function createTomTomMap(apiKey, lat, lon) {
      if (!tomtomMapRef.value || !window.tt) return;
      try {
        if (ttMapInstance) {
          ttMapInstance.remove();
        }
        ttMapInstance = window.tt.map({
          key: apiKey,
          container: tomtomMapRef.value,
          center: [lon, lat],
          zoom: 12.5,
          stylesVisibility: {
            trafficIncidents: true,
            trafficFlow: true
          }
        });
        
        isMapLoaded.value = true;
        ttMapInstance.addControl(new window.tt.NavigationControl());
      } catch (e) {
        console.error('Error al renderizar mapa de TomTom:', e);
      }
    }

    // ─── UI LOGIC ────────────────────────────────────────────────────────────
    function toggleTheme() {
      isDarkMode.value = !isDarkMode.value;
    }

    async function newConversation() {
      closeMobileDrawers();
      const id = crypto.randomUUID();
      activeConversationId.value = id;
      localMessages.value[id] = [];
      inputMessage.value = '';
      streamingContent.value = '';
      isStreaming.value = false;

      isResettingChat.value = true;
      setTimeout(() => {
        isResettingChat.value = false;
      }, 300);

      await nextTick();
      if (inputTextarea.value) {
        inputTextarea.value.focus();
      }
    }


    // ─── ANALYZER LOGIC ──────────────────────────────────────────────────────
    function getInfractionData(content) {
      if (!content) return null;
      const match = content.match(/\[INFRACTION_DATA\]([\s\S]*?)\[\/INFRACTION_DATA\]/i);
      if (match && match[1]) {
        try {
          return JSON.parse(match[1].trim());
        } catch (e) {
          console.error("Error parsing infraction data:", e);
          return null;
        }
      }
      return null;
    }

    function getGravityClass(gravity) {
      if (!gravity) return 'color-green';
      const g = gravity.toUpperCase();
      if (g === 'MUY GRAVE') return 'color-red';
      if (g === 'GRAVE') return 'color-orange';
      return 'color-green';
    }

    function getNeedleAngle(gravity) {
      if (!gravity) return 'rotate(-60deg)';
      const g = gravity.toUpperCase();
      if (g === 'LEVE') return 'rotate(-60deg)';
      if (g === 'GRAVE') return 'rotate(0deg)';
      return 'rotate(60deg)'; // MUY GRAVE
    }

    // ─── CHAT LOGIC ──────────────────────────────────────────────────────────
    async function sendMessage() {
      const text = inputMessage.value.trim();
      if (!text || isStreaming.value) return;

      if (!activeConversationId.value) newConversation();
      const convId = activeConversationId.value;

      if (!localMessages.value[convId]) localMessages.value[convId] = [];

      localMessages.value[convId].push({
        role: 'user',
        content: text
      });
      inputMessage.value = '';
      if (inputTextarea.value) {
        inputTextarea.value.style.height = 'auto';
      }
      isStreaming.value = true;
      streamingContent.value = '';

      await nextTick();
      scrollToBottom();

      try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: text,
            conversationId: convId,
            model: selectedModel.value
          })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let currentEvent = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed) continue;

            if (trimmed.startsWith('event:')) {
              currentEvent = trimmed.slice(6).trim();
            } else if (trimmed.startsWith('data:')) {
              const data = trimmed.slice(5).trim();
              if (currentEvent === 'token') {
                try {
                  const binaryString = atob(data);
                  const bytes = new Uint8Array(binaryString.length);
                  for (let i = 0; i < binaryString.length; i++) bytes[i] = binaryString.charCodeAt(i);
                  streamingContent.value += new TextDecoder('utf-8').decode(bytes);
                  await nextTick();
                  scrollToBottom();
                } catch (e) {}
              }
            }
          }
        }

        if (streamingContent.value) {
          localMessages.value[convId].push({
            role: 'assistant',
            content: streamingContent.value
          });
        }
      } catch (e) {
        console.error(e);
        localMessages.value[convId].push({
          role: 'assistant',
          content: '❌ Error al comunicarse con el servidor.'
        });
      } finally {
        streamingContent.value = '';
        isStreaming.value = false;
        await loadConversations(); // Reload history after replying
        await nextTick();
        scrollToBottom();
      }
    }

    function sendSuggestion(text) {
      inputMessage.value = text;
      sendMessage();
    }

    function scrollToBottom() {
      if (chatArea.value) chatArea.value.scrollTop = chatArea.value.scrollHeight;
    }

    function formatMessage(content) {
      if (!content) return '';
      // Ocultar el bloque JSON del sistema
      let text = content.replace(/\[INFRACTION_DATA\][\s\S]*?\[\/INFRACTION_DATA\]/gi, '').trim();
      
      let html = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      html = html.replace(/\n/g, '<br>');
      return html;
    }

    // File Upload State
    const fileInputRef = ref(null);
    const isUploading = ref(false);
    const uploadStatusMessage = ref('');
    const uploadStatusColor = ref('#10b981');

    async function handleFileUpload(event) {
      const file = event.target.files && event.target.files[0];
      if (!file) return;

      isUploading.value = true;
      uploadStatusMessage.value = `⏳ Indexando documento '${file.name}' en la base vectorial (Qdrant)...`;
      uploadStatusColor.value = '#f59e0b';

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
          method: 'POST',
          body: formData
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
          uploadStatusMessage.value = `✅ Documento '${file.name}' indexado exitosamente (${data.chunksCount} fragmentos)`;
          uploadStatusColor.value = '#10b981';
        } else {
          uploadStatusMessage.value = `❌ Error: ${data.message || 'No se pudo procesar el documento.'}`;
          uploadStatusColor.value = '#ef4444';
        }
      } catch (e) {
        console.error('Error al subir documento:', e);
        uploadStatusMessage.value = '❌ Error de conexión al servidor al subir el documento.';
        uploadStatusColor.value = '#ef4444';
      } finally {
        isUploading.value = false;
        if (fileInputRef.value) fileInputRef.value.value = '';
        setTimeout(() => {
          if (!isUploading.value) {
            uploadStatusMessage.value = '';
          }
        }, 8000);
      }
    }

    function adjustTextareaHeight() {
      if (!inputTextarea.value) return;
      inputTextarea.value.style.height = 'auto';
      const newHeight = Math.min(inputTextarea.value.scrollHeight, 180);
      inputTextarea.value.style.height = `${newHeight}px`;
    }

    function openActivityModal() {
      showSettingsMenu.value = false;
      showActivityModal.value = true;
    }

    function openModelModal() {
      showSettingsMenu.value = false;
      showModelModal.value = true;
    }

    function openLegalModal() {
      showSettingsMenu.value = false;
      showLegalModal.value = true;
    }

    const hoveredConvTitle = ref('');
    const hoveredTooltipTop = ref(0);

    function onConvMouseEnter(event, title) {
      if (typeof window !== 'undefined' && window.innerWidth <= 1024) return;
      if (!event || !event.currentTarget) return;
      const rect = event.currentTarget.getBoundingClientRect();
      const sidebarEl = event.currentTarget.closest('.sidebar');
      if (sidebarEl) {
        const sidebarRect = sidebarEl.getBoundingClientRect();
        hoveredTooltipTop.value = (rect.top - sidebarRect.top) + (rect.height / 2);
      } else {
        hoveredTooltipTop.value = rect.top + (rect.height / 2);
      }
      hoveredConvTitle.value = title || 'Consulta de tránsito';
    }

    function onConvMouseLeave() {
      hoveredConvTitle.value = '';
    }

    async function confirmClearAllHistory() {
      let currentIds = conversations.value.map(c => c.id);
      try {
        const res = await fetch(`${API_BASE_URL}/api/conversations`).catch(() => null);
        if (res && res.ok) {
          const remoteConvs = await res.json().catch(() => []);
          currentIds = Array.from(new Set([...currentIds, ...remoteConvs.map(c => c.id)]));
        }

        // 1. Eliminar en PostgreSQL usando el endpoint DELETE /api/conversations
        await fetch(`${API_BASE_URL}/api/conversations`, { method: 'DELETE' }).catch(err => {
          console.warn('DELETE /api/conversations:', err);
        });

        // 2. Si hay IDs activos, asegurar borrado individual como garantía adicional
        if (currentIds.length > 0) {
          await Promise.allSettled(currentIds.map(id => fetch(`${API_BASE_URL}/api/conversations/${id}`, { method: 'DELETE' })));
        }
      } catch (e) {
        console.error('Error al borrar todo el historial en backend:', e);
      } finally {
        // 3. Persistir IDs en localStorage y retirar filtro temporal para permitir nuevos chats
        const previouslyHidden = JSON.parse(localStorage.getItem('transiai_hidden_conv_ids') || '[]');
        const allHidden = Array.from(new Set([...previouslyHidden, ...currentIds]));
        localStorage.setItem('transiai_hidden_conv_ids', JSON.stringify(allHidden));
        localStorage.removeItem('transiai_activity_cleared_at');

        // 4. Limpiar estado reactivo
        conversations.value = [];
        localMessages.value = {};
        activeConversationId.value = null;

        // 5. Cerrar modales y notificar éxito
        showConfirmClearAllModal.value = false;
        showActivityModal.value = false;
        showSuccessClearModal.value = true;
      }
    }

    function clearChatActivity() {
      showConfirmClearAllModal.value = true;
    }

    return {
      conversations, activeConversationId, currentMessages, inputMessage, isStreaming, streamingContent,
      chatArea, selectedModel, weatherData, trafficAlerts, suggestedQuestions, isDarkMode,
      showDeleteModal, showConfirmClearAllModal, convToDelete, weatherLocationName, isLocatingWeather,
      weatherCondition, fetchWeather, routeEstimates, isLoadingRoutes, fetchRoutesInfo,
      tomtomMapRef, isMapLoaded, initTomTomMap, inputTextarea, isResettingChat,
      fileInputRef, isUploading, uploadStatusMessage, uploadStatusColor, handleFileUpload, adjustTextareaHeight,
      showSettingsMenu, showThemeSubmenu, showActivityModal, showModelModal, showLegalModal, showSuccessClearModal,
      openActivityModal, openModelModal, openLegalModal, clearChatActivity, confirmClearAllHistory,
      isMobileSidebarOpen, isMobileWidgetsOpen, closeMobileDrawers,
      hoveredConvTitle, hoveredTooltipTop, onConvMouseEnter, onConvMouseLeave,
      newConversation, selectConversation, deleteConversation, confirmDelete, sendMessage, sendSuggestion, 
      getInfractionData, getGravityClass, getNeedleAngle, formatMessage, toggleTheme, carrosLogo, clipIcon
    };
  }
};

</script>

<template>
  <div class="app-layout" :class="{ 'dark-theme': isDarkMode }">
    
    <!-- Custom Delete Modal -->
    <transition name="fade">
      <div v-if="showDeleteModal" class="modal-overlay">
        <div class="modal-box">
          <div class="modal-icon">⚠️</div>
          <h3>¿Eliminar conversación?</h3>
          <p>Esta acción no se puede deshacer y perderás el historial de este chat.</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="showDeleteModal = false">Cancelar</button>
            <button class="btn-confirm" @click="confirmDelete">Sí, eliminar</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- ══════════ LEFT COLUMN (Sidebar) ══════════ -->
    <aside class="sidebar">
      <div class="brand-header" @click="$router.push('/')" style="cursor: pointer;" title="Volver al Inicio">
        <div class="brand-icon">
          <img src="/carros.png" alt="Logo" style="width: 28px; height: auto;" />
        </div>
        <div class="brand-text">
          <span class="brand-subtitle">ASISTENTE</span>
          <span class="brand-title">TransiAI</span>
          <span class="brand-slogan">Información que te mueve <span class="dot"></span></span>
        </div>
      </div>

      <button class="new-chat-btn" @click="newConversation">
        💬 Nuevo chat
      </button>

      <div class="nav-menu">
        <div class="nav-item" style="cursor: pointer; background: rgba(255,255,255,0.05); pointer-events: none;">
          🕒 Historial de Consultas
        </div>
        
        <!-- Conversation List -->
        <div class="conversations-list">
          <div v-if="conversations.length === 0" style="padding: 10px; font-size: 12px; color: #64748b; text-align: center;">
            No hay conversaciones guardadas
          </div>
          <div v-for="conv in conversations" :key="conv.id"
               class="conv-item"
               :class="{ active: conv.id === activeConversationId }"
               @click="selectConversation(conv.id)">
            <span style="margin-right: 8px;">💬</span>
            <span class="conv-title">{{ conv.title || 'Consulta de tránsito' }}</span>
            <button class="conv-del-btn" @click.stop="deleteConversation(conv.id)">✕</button>
          </div>
        </div>

        <div class="nav-item" style="cursor: pointer;" @click="showConfig = !showConfig">
          ⚙️ Configuración (Modelo)
        </div>
        
        <transition name="fade">
          <div v-if="showConfig" class="config-dropdown">
            <label>Modelo LLM:</label>
            <select v-model="selectedModel" @change="saveModel">
              <option value="gemma-4-31b-it">gemma-4-31b-it</option>
              <option value="openai/gpt-oss-120b">openai/gpt-oss-120b</option>
              <option value="llama3-70b-8192">llama3-70b-8192</option>
            </select>
            <p>Se aplica automáticamente al backend</p>
          </div>
        </transition>
      </div>
      
      <!-- Bottom left: Theme toggle and footer -->
      <div class="sidebar-footer">
        <button class="back-home-btn-green" @click="$router.push('/')">
           Volver al Inicio
        </button>
        <button class="theme-toggle" @click="toggleTheme">
          {{ isDarkMode ? '☀️ Modo Claro' : '🌙 Modo Oscuro' }}
        </button>
        <div class="footer-text">
          Hecho para una movilidad<br>más segura y eficiente 💚
        </div>
      </div>
    </aside>

    <!-- ══════════ MAIN CHAT AREA (CENTER PANEL) ══════════ -->
    <main class="main-content">
      <div class="top-bar">
        <div class="user-profile">
          <span>Bienvenido</span>
          <div class="user-avatar">👨‍💼</div>
        </div>
      </div>

      <div class="chat-area" ref="chatArea">
        
        <!-- Welcome Screen -->
        <div v-if="currentMessages.length === 0 && !isStreaming" class="welcome-container">
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
               <span class="typing-dot" v-if="!streamingContent">...</span>
             </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="input-area">
        <div class="input-container">
          <textarea
              v-model="inputMessage"
              placeholder="Escribe tu pregunta sobre tránsito..."
              @keydown.enter.exact.prevent="sendMessage"
              :disabled="isStreaming"
              rows="1"
          ></textarea>
          <button class="send-btn" @click="sendMessage" :disabled="!inputMessage.trim() || isStreaming">
            ➤
          </button>
        </div>
        <div class="disclaimer">
          Puedes preguntar sobre tráfico, rutas, obras, cierres y más ⓘ
        </div>
      </div>
    </main>

    <!-- ══════════ RIGHT PANEL (TOOLS) ══════════ -->
    <aside class="right-panel">
      <!-- Weather Widget -->
      <div class="widget-card weather">
        <div class="widget-title">
          Clima local
          <span style="color: #0db37b;">●</span>
        </div>
        <div class="weather-info" v-if="weatherData">
          <div class="weather-temp">{{ weatherData.temperature }}°C</div>
          <div class="weather-desc">
            Viento: {{ weatherData.windspeed }} km/h<br>
            Condiciones moderadas
          </div>
        </div>
        <div v-else class="weather-desc">Cargando clima...</div>
      </div>

      <!-- Rutas en Google Maps -->
      <div class="widget-card">
        <div class="widget-title">
          Rutas y Navegación
          <span class="see-all">📍 Maps</span>
        </div>
        <div class="widget-list">
          <a href="https://www.google.com/maps/dir/?api=1&destination=Mi+Trabajo" target="_blank" class="widget-list-item" style="text-decoration: none;">
            <span>🏠 Casa - Trabajo</span><span class="arrow">🧭</span>
          </a>
          <a href="https://www.google.com/maps/dir/?api=1&destination=Aeropuerto" target="_blank" class="widget-list-item" style="text-decoration: none;">
            <span>✈️ Centro - Aeropuerto</span><span class="arrow">🧭</span>
          </a>
          <a href="https://www.google.com/maps" target="_blank" class="widget-list-item border-none" style="text-decoration: none;">
            <span>🗺️ Abrir Google Maps</span><span class="arrow">🧭</span>
          </a>
        </div>
      </div>

      <!-- Últimas Alertas -->
      <div class="widget-card">
        <div class="widget-title">
          Últimas alertas
          <span class="see-all">En vivo (TomTom)</span>
        </div>
        <div class="widget-list" v-if="trafficAlerts.length > 0">
          <div v-for="(alert, idx) in trafficAlerts" :key="idx" 
               class="widget-list-item" 
               :class="{ 'border-none': idx === trafficAlerts.length - 1 }">
            <span>{{ alert.text }}</span>
          </div>
        </div>
        <div class="widget-list" v-else>
          <div class="widget-list-item border-none" style="font-size: 11px; color: #64748b; padding-bottom: 0;">
            Cargando alertas...
          </div>
        </div>
      </div>
    </aside>

  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue';

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
    const showConfig = ref(false);
    const selectedModel = ref('gemma-4-31b-it');
    const weatherData = ref(null);
    const trafficAlerts = ref([]);
    const isDarkMode = ref(false);
    
    // Modal state
    const showDeleteModal = ref(false);
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
      fetchAlerts();
      await loadConversations();
    });

    // ─── API FETCHING ────────────────────────────────────────────────────────
    async function loadConversations() {
      try {
        const res = await fetch('/api/conversations');
        if (res.ok) {
          conversations.value = await res.json();
        }
      } catch (e) {
        console.error('Error cargando conversaciones:', e);
      }
    }

    async function selectConversation(id) {
      activeConversationId.value = id;
      streamingContent.value = '';

      if (!localMessages.value[id] || localMessages.value[id].length === 0) {
        try {
          const res = await fetch(`/api/conversations/${id}/messages`);
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
        await fetch(`/api/conversations/${id}`, { method: 'DELETE' });
        conversations.value = conversations.value.filter(c => c.id !== id);
        delete localMessages.value[id];
        if (activeConversationId.value === id) {
          activeConversationId.value = null;
        }
      } catch (e) {
        console.error('Error eliminando conversación:', e);
      } finally {
        showDeleteModal.value = false;
        convToDelete.value = null;
      }
    }

    async function fetchWeather() {
      try {
        const res = await fetch('https://api.open-meteo.com/v1/forecast?latitude=-0.2298&longitude=-78.5249&current_weather=true');
        const data = await res.json();
        weatherData.value = data.current_weather;
      } catch (e) {}
    }

    async function fetchAlerts() {
      try {
        const apiKey = import.meta.env.VITE_TOMTOM_API_KEY;
        const bbox = '-78.5869,-0.3601,-78.4116,-0.0911';
        const url = `https://api.tomtom.com/traffic/services/5/incidentDetails?key=${apiKey}&bbox=${bbox}&language=es-ES&fields={incidents{type,geometry{type,coordinates},properties{iconCategory,magnitudeOfDelay,events{description,code,iconCategory}}}}`;
        const res = await fetch(url);
        const data = await res.json();
        if (data && data.incidents && data.incidents.length > 0) {
          trafficAlerts.value = data.incidents.slice(0, 3).map(inc => {
            let desc = inc.properties.events?.[0]?.description || 'Alerta de tráfico';
            const cat = inc.properties.iconCategory;
            let emoji = '⚠️';
            if (cat === 1) emoji = '🚗'; 
            else if (cat === 6) emoji = '⛔'; 
            else if (cat === 9) emoji = '🚧'; 
            return { text: `${emoji} ${desc}` };
          });
        } else {
          trafficAlerts.value = [{ text: '✅ Todo despejado en la ciudad' }];
        }
      } catch (e) {
        trafficAlerts.value = [{ text: '⚠️ Error al cargar alertas' }];
      }
    }

    // ─── UI LOGIC ────────────────────────────────────────────────────────────
    function toggleTheme() {
      isDarkMode.value = !isDarkMode.value;
    }

    function newConversation() {
      const id = crypto.randomUUID();
      activeConversationId.value = id;
      localMessages.value[id] = [];
      streamingContent.value = '';
    }

    function saveModel() {
      console.log("Model changed to:", selectedModel.value);
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
      isStreaming.value = true;
      streamingContent.value = '';

      await nextTick();
      scrollToBottom();

      try {
        const response = await fetch('/api/chat', {
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

    return {
      conversations, activeConversationId, currentMessages, inputMessage, isStreaming, streamingContent,
      chatArea, showConfig, selectedModel, weatherData, trafficAlerts, suggestedQuestions, isDarkMode,
      showDeleteModal, convToDelete,
      newConversation, selectConversation, deleteConversation, confirmDelete, saveModel, sendMessage, sendSuggestion, 
      getInfractionData, getGravityClass, getNeedleAngle, formatMessage, toggleTheme
    };
  }
};
</script>

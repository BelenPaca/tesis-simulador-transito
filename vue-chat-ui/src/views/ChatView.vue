<template>
  <div class="app-layout" :class="{ 'dark-theme': isDarkMode }">
    
    <!-- Custom Delete Modal -->
    <transition name="fade">
      <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
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

    <!-- Model Info Modal (Centro de pantalla) -->
    <transition name="fade">
      <div v-if="showConfig" class="modal-overlay" @click.self="showConfig = false">
        <div class="modal-box model-modal-box">
          <div class="modal-icon">ℹ️</div>
          <h3>Información del Modelo</h3>
          
          <div class="model-badge-container">
            <span class="model-badge-name">gemini-3.1-flash-lite</span>
            <span class="model-badge-status">● Activo</span>
          </div>

          <p class="model-modal-desc">
            Modelo optimizado para procesamiento de documentos jurídicos y consulta RAG.
          </p>

          <div class="legal-framework-box">
            <div class="legal-framework-title">⚖️ Marco Legal Aplicado:</div>
            <ul class="legal-framework-list">
              <li>📜 Código Orgánico Integral Penal (COIP)</li>
              <li>🚗 Ley de Tránsito y su Reglamento</li>
              <li>💼 Código del Trabajo</li>
              <li>⚖️ COGEP</li>
              <li>🇪🇨 Constitución de la República del Ecuador</li>
            </ul>
          </div>

          <div class="modal-actions" style="margin-top: 20px;">
            <button class="btn-cancel" style="background: var(--accent-green); color: white; width: 100%;" @click="showConfig = false">Entendido</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- ══════════ LEFT COLUMN (Sidebar) ══════════ -->
    <aside class="sidebar">
      <div class="brand-header" @click="$router.push('/')" style="cursor: pointer;" title="Volver al Inicio">
        <div class="brand-icon">
          <img :src="carrosLogo" alt="Logo" style="width: 28px; height: auto;" />
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

        <div class="nav-item model-info-nav" style="cursor: pointer;" @click="showConfig = true">
          ℹ️ Información del Modelo
        </div>
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
               <span class="typing-dot" v-if="!streamingContent">...</span>
             </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="input-area">
        <div class="input-container">
          <textarea
              ref="inputTextarea"
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
          Información generada por IA. Valida los resultados con un especialista en tránsito.
        </div>
      </div>
    </main>

    <!-- ══════════ RIGHT PANEL (TOOLS) ══════════ -->
    <aside class="right-panel">
      <!-- Weather Widget (Detección dinámica en todo Ecuador) -->
      <div class="widget-card weather">
        <div class="widget-title-row">
          <div class="widget-title-text">
            <span>Clima</span>
            <span style="color: #6ee7b7; font-size: 30px;">●</span>
          </div>
          <button class="refresh-loc-btn" @click="fetchWeather" title="Redetectar ubicación en Ecuador">
            <span :class="{ 'spin-icon': isLocatingWeather }">🔄</span>
          </button>
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
            <div style="display: flex; flex-direction: column;">
              <span style="font-weight: 600; font-size: 13px;">{{ route.title }}</span>
              <span :style="{ color: route.trafficStatus.color, fontSize: '11px', marginTop: '2px', fontWeight: '500' }">
                {{ route.trafficStatus.text }}
              </span>
            </div>
            <div style="display: flex; align-items: center; gap: 4px;">
              <span style="font-weight: 800; font-size: 14px; color: var(--text-primary);">{{ route.timeText }}</span>
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

      <!-- Mapa de Tráfico en Vivo (TomTom Option 2) -->
      <div class="widget-card">
        <div class="widget-title">
          <span>Mapa de Tráfico</span>
          <span class="see-all">En vivo (TomTom)</span>
        </div>
        <div class="tomtom-map-wrapper">
          <div id="tomtom-map" ref="tomtomMapRef" style="width: 100%; height: 210px; border-radius: 12px; overflow: hidden; background: #0f172a; position: relative;">
            <div v-if="!isMapLoaded" style="display: flex; align-items: center; justify-content: center; height: 100%; color: #94a3b8; font-size: 12px;">
              ⏳ Cargando mapa de tráfico...
            </div>
          </div>
        </div>
      </div>
    </aside>

  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue';
import carrosLogo from '../assets/carros.png';

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
    const showConfig = ref(false);
    const selectedModel = ref('gemini-3.1-flash-lite');
    const weatherData = ref(null);
    const weatherLocationName = ref('Detectando...');
    const isLocatingWeather = ref(false);
    const trafficAlerts = ref([]);
    const isDarkMode = ref(false);

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
                const minutes = Math.round(summary.travelTimeInSeconds / 60);
                const delayMin = Math.round((summary.trafficDelayInSeconds || 0) / 60);
                let trafficStatus = { text: '🟢 Fluido', color: '#10b981' };
                if (delayMin > 5) {
                  trafficStatus = { text: `🔴 +${delayMin}m tráfico`, color: '#ef4444' };
                } else if (delayMin > 1) {
                  trafficStatus = { text: `🟡 +${delayMin}m moderado`, color: '#f59e0b' };
                }
                return {
                  title: d.title,
                  timeText: `${minutes}m`,
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
        scrollToResponseStart();
      }
    }

    function sendSuggestion(text) {
      inputMessage.value = text;
      sendMessage();
    }

    function scrollToBottom() {
      if (chatArea.value) chatArea.value.scrollTop = chatArea.value.scrollHeight;
    }

    function scrollToResponseStart() {
      if (!chatArea.value) return;

      const setPos = () => {
        if (!chatArea.value) return;
        const wrappers = chatArea.value.querySelectorAll('.message-wrapper');
        if (!wrappers || wrappers.length === 0) return;

        // El último wrapper es la respuesta del asistente (con su Dashboard si aplica)
        const lastWrapper = wrappers[wrappers.length - 1];

        if (lastWrapper) {
          const targetRect = lastWrapper.getBoundingClientRect();
          const chatAreaRect = chatArea.value.getBoundingClientRect();
          const relativeTop = targetRect.top - chatAreaRect.top + chatArea.value.scrollTop;
          chatArea.value.scrollTop = Math.max(0, relativeTop - 12);
        }
      };

      setPos();
      requestAnimationFrame(setPos);
      setTimeout(setPos, 50);
      setTimeout(setPos, 150);
      setTimeout(setPos, 300);
      setTimeout(setPos, 600);
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
      showDeleteModal, convToDelete, weatherLocationName, isLocatingWeather,
      weatherCondition, fetchWeather, routeEstimates, isLoadingRoutes, fetchRoutesInfo,
      tomtomMapRef, isMapLoaded, initTomTomMap, inputTextarea, isResettingChat,
      newConversation, selectConversation, deleteConversation, confirmDelete, sendMessage, sendSuggestion, 
      getInfractionData, getGravityClass, getNeedleAngle, formatMessage, toggleTheme, carrosLogo,
      scrollToResponseStart
    };
  }
};
</script>

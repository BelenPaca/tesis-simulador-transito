<template>
  <div class="landing-page">
    <div class="landing-background"></div>
    
    <div class="landing-content">
      <div class="glass-card">
        <div class="brand-header-landing">
          <div class="brand-icon-landing">
            <img :src="carrosLogo" alt="Logo" />
          </div>
          <div class="brand-text-landing">
            <span class="brand-subtitle-landing">ASISTENTE</span>
            <span class="brand-title-landing">TransiAI</span>
            <span class="brand-slogan-landing">Información que te mueve <span class="dot"></span></span>
          </div>
        </div>
        
        <div class="welcome-message">
          <h1>¡Bienvenido!</h1>
          <p>Tu asistente inteligente para Leyes de Tránsito de forma <strong>segura</strong>, <strong>rápida</strong> y <strong>eficiente</strong>.</p>
        </div>
        
        <div class="action-container">
          <button v-if="!isLoading" class="start-btn" @click="startExperience">
            Iniciar Conversación
          </button>
          <div v-else class="loading-container">
            <span class="loading-text">Cargando tu experiencia...</span>
            <div class="progress-bar-bg">
              <div class="progress-bar-fill" :style="{ width: progress + '%' }"></div>
            </div>
            <span class="progress-text">{{ progress }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import carrosLogo from '../assets/carros.png'

const router = useRouter()
const isLoading = ref(false)
const progress = ref(0)

const startExperience = () => {
  isLoading.value = true
  progress.value = 0
  
  const interval = setInterval(() => {
    progress.value += Math.floor(Math.random() * 15) + 5
    if (progress.value >= 100) {
      progress.value = 100
      clearInterval(interval)
      setTimeout(() => {
        router.push('/chat')
      }, 400)
    }
  }, 150)
}
</script>

<style scoped>
.landing-page {
  position: relative;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background-color: #e0f2fe; /* light blue fallback */
}

.landing-background {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background-image: url('/fondo_quito.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: 1;
}

.landing-content {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 600px;
  padding: 20px;
  display: flex;
  justify-content: center;
}

.floating-robot-landing {
  position: absolute;
  left: -80px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 140px;
  filter: drop-shadow(0 15px 15px rgba(0,0,0,0.2));
  animation: float-bot 4s ease-in-out infinite;
  z-index: 20;
}

@keyframes float-bot {
  0% { transform: translateY(0px) rotate(-5deg); }
  50% { transform: translateY(-15px) rotate(5deg); }
  100% { transform: translateY(0px) rotate(-5deg); }
}

.glass-card {
  background: rgba(255, 255, 255, 0.45);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 30px;
  padding: 50px 40px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.brand-header-landing {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 40px;
}

.brand-icon-landing {
  width: 120px;
  height: 120px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 20px rgba(0,0,0,0.05);
  margin-bottom: 24px;
}
.brand-icon-landing img {
  width: 75px;
  height: auto;
}

@keyframes float-car {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-4px); }
  100% { transform: translateY(0px); }
}

.brand-text-landing {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.brand-subtitle-landing {
  font-size: 14px;
  color: #0db37b;
  font-weight: 800;
  letter-spacing: 2px;
}

.brand-title-landing {
  font-size: 28px;
  font-weight: 900;
  color: #1e293b;
  margin: 4px 0;
}

.brand-slogan-landing {
  font-size: 14px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 6px;
}
.dot {
  width: 8px;
  height: 8px;
  background: #0db37b;
  border-radius: 50%;
  display: inline-block;
}

.welcome-message {
  margin-bottom: 50px;
}
.welcome-message h1 {
  font-size: 36px;
  color: #0f172a;
  margin-bottom: 12px;
}
.welcome-message p {
  font-size: 18px;
  color: #475569;
  line-height: 1.5;
}
.welcome-message strong {
  color: #0db37b;
}

.action-container {
  width: 100%;
  min-height: 70px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.start-btn {
  background: linear-gradient(135deg, #0fcf8c, #099464);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 18px 40px;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 10px 25px rgba(13, 179, 123, 0.4);
  transition: transform 0.2s, box-shadow 0.2s;
  width: 100%;
  max-width: 350px;
}
.start-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 30px rgba(13, 179, 123, 0.5);
}

.loading-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.loading-text {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 12px;
  font-weight: 600;
}

.progress-bar-bg {
  width: 100%;
  max-width: 400px;
  height: 8px;
  background: rgba(0,0,0,0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-bar-fill {
  height: 100%;
  background: #0db37b;
  border-radius: 4px;
  transition: width 0.15s ease-out;
}

.progress-text {
  font-size: 13px;
  color: #0db37b;
  font-weight: 700;
}
</style>

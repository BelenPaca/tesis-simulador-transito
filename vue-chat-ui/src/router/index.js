import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '../views/LandingView.vue'
import ChatView from '../views/ChatView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: LandingView
    },
    {
      path: '/chat',
      name: 'chat',
      component: ChatView
    }
  ]
})

let isInitialLoad = true

router.beforeEach((to, from, next) => {
  if (isInitialLoad) {
    isInitialLoad = false
    if (to.path !== '/') {
      return next('/')
    }
  }
  next()
})

export default router

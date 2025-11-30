import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/Login.vue'
import AdminDash from '../components/AdminDash.vue'
import DoctorDash from '../components/DoctorDash.vue'
import PatientDash from '../components/PatientDash.vue'

const routes = [
  { path: '/', component: Login },
  { path: '/admin', component: AdminDash },
  { path: '/doctor', component: DoctorDash },
  { path: '/patient', component: PatientDash }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
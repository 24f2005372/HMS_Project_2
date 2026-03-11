<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4" v-if="user">
      <div class="container-fluid px-4">
        <span class="navbar-brand fw-bold">🏥 HMS Portal</span>
        <div class="d-flex align-items-center gap-3">
          <span class="text-white small">
            Logged in as <strong>{{ user.username }}</strong>
            <span class="badge ms-1" :class="roleBadge(user.role)">{{ user.role }}</span>
          </span>
          <button @click="logout" class="btn btn-outline-danger btn-sm">Logout</button>
        </div>
      </div>
    </nav>
    <router-view @login-success="setUser"/>
  </div>
</template>

<script>
export default {
  data() { return { user: null } },
  mounted() {
    const stored = localStorage.getItem('user')
    if (stored) this.user = JSON.parse(stored)
  },
  methods: {
    setUser(userData) {
      this.user = userData
      localStorage.setItem('user', JSON.stringify(userData))
    },
    logout() {
      this.user = null
      localStorage.removeItem('user')
      this.$router.push('/')
    },
    roleBadge(role) {
      return role === 'admin' ? 'bg-danger' : role === 'doctor' ? 'bg-info' : 'bg-success'
    }
  }
}
</script>

<style>
#app { font-family: 'Segoe UI', sans-serif; }
.nav-link { cursor: pointer; }
</style>

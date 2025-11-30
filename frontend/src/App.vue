<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4" v-if="user">
      <div class="container">
        <span class="navbar-brand">🏥 HMS Project</span>
        <div class="d-flex align-items-center">
          <span class="text-white me-3">Welcome, {{ user.username }} ({{ user.role }})</span>
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
    // [FIX] Persistent Login Check
    const stored = localStorage.getItem('user');
    if (stored) {
      this.user = JSON.parse(stored);
    }
  },
  methods: {
    setUser(userData) { 
      this.user = userData;
      localStorage.setItem('user', JSON.stringify(userData));
    },
    logout() {
      this.user = null;
      localStorage.removeItem('user');
      this.$router.push('/');
    }
  }
}
</script>

<style>
#app { font-family: sans-serif; }
</style>
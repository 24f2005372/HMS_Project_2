<template>
  <div id="app">
    <nav v-if="user">
      <span>Welcome, {{ user.username }}</span>
      <button @click="logout">Logout</button>
    </nav>
    <router-view @login-success="setUser"/>
  </div>
</template>

<script>
export default {
  data() { return { user: null } },
  methods: {
    setUser(userData) { this.user = userData },
    logout() {
      this.user = null;
      this.$router.push('/');
    }
  }
}
</script>

<style>
#app { font-family: sans-serif; padding: 20px; }
nav { background: #eee; padding: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; }
button { cursor: pointer; padding: 5px 10px; }
input { display: block; margin: 10px 0; padding: 8px; width: 100%; max-width: 300px; }
.card { border: 1px solid #ccc; padding: 15px; margin: 10px 0; border-radius: 5px; }
.badge { background: #007bff; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; }
</style>
<template>
  <div>
    <h2>HMS Login</h2>
    <input v-model="username" placeholder="Username" />
    <input v-model="password" type="password" placeholder="Password" />
    <button @click="login">Login</button>
    
    <hr>
    <h3>New Patient? Register</h3>
    <input v-model="regUser" placeholder="New Username" />
    <input v-model="regPass" type="password" placeholder="New Password" />
    <button @click="register">Register</button>
    <p>{{ message }}</p>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() { return { username: '', password: '', regUser: '', regPass: '', message: '' } },
  methods: {
    async login() {
      try {
        const res = await axios.post('http://127.0.0.1:5000/api/login', {
          username: this.username, password: this.password
        });
        this.$emit('login-success', res.data);
        if (res.data.role === 'admin') this.$router.push('/admin');
        else if (res.data.role === 'doctor') this.$router.push('/doctor');
        else this.$router.push('/patient');
      } catch (e) { this.message = 'Invalid Credentials'; }
    },
    async register() {
      try {
        await axios.post('http://127.0.0.1:5000/api/register', {
          username: this.regUser, password: this.regPass
        });
        this.message = 'Registered! Please Login.';
      } catch (e) { this.message = 'Error Registering'; }
    }
  }
}
</script>
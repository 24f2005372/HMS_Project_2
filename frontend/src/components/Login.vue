<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-5">
        
        <div class="card shadow mb-4">
          <div class="card-header bg-primary text-white text-center">
            <h4>HMS Login</h4>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label">Username</label>
              <input v-model="username" class="form-control" placeholder="Enter username">
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input v-model="password" type="password" class="form-control" placeholder="Enter password">
            </div>
            <button @click="login" class="btn btn-primary w-100">Login</button>
          </div>
        </div>

        <div class="card shadow">
          <div class="card-header bg-success text-white text-center">
            <h4>New Patient? Register</h4>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <input v-model="regUser" class="form-control" placeholder="New Username">
            </div>
            <div class="mb-3">
              <input v-model="regPass" type="password" class="form-control" placeholder="New Password">
            </div>
            <button @click="register" class="btn btn-success w-100">Register</button>
            <p class="text-center text-danger mt-2" v-if="message">{{ message }}</p>
          </div>
        </div>

      </div>
    </div>
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
        
        // [FIX] Save User to Browser Storage Immediately
        localStorage.setItem('user', JSON.stringify(res.data));
        
        // Notify Parent
        this.$emit('login-success', res.data);
        
        // Redirect
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
        const res = await axios.post('http://127.0.0.1:5000/api/login', {
          username: this.regUser, password: this.regPass
        });
        localStorage.setItem('user', JSON.stringify(res.data));
        this.$emit('login-success', res.data);
        this.$router.push('/patient');
      } catch (e) { this.message = 'Error Registering (Username might exist)'; }
    }
  }
}
</script>
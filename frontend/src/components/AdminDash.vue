<template>
  <div>
    <h2>Admin Dashboard</h2>
    <div class="stats">
      <div class="card">Doctors: {{ stats.doctors }}</div>
      <div class="card">Patients: {{ stats.patients }}</div>
      <div class="card">Appointments: {{ stats.appointments }}</div>
    </div>

    <h3>Manage Doctors</h3>
    <input v-model="newDocName" placeholder="Username" />
    <input v-model="newDocPass" placeholder="Password" />
    <input v-model="newDocSpec" placeholder="Specialization" />
    <button @click="addDoctor">Add Doctor</button>

    <div v-for="doc in doctors" :key="doc.id" class="card">
      {{ doc.username }} - {{ doc.spec }}
      <button @click="deleteDoctor(doc.id)" style="background: red; color: white;">Delete</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() { return { stats: {}, doctors: [], newDocName: '', newDocPass: '', newDocSpec: '' } },
  async mounted() {
    const s = await axios.get('http://127.0.0.1:5000/api/admin/dashboard');
    this.stats = s.data;
    this.loadDocs();
  },
  methods: {
    async loadDocs() {
      const d = await axios.get('http://127.0.0.1:5000/api/doctors');
      this.doctors = d.data;
    },
    async addDoctor() {
      await axios.post('http://127.0.0.1:5000/api/doctors', {
        username: this.newDocName, password: this.newDocPass, specialization: this.newDocSpec
      });
      this.loadDocs();
    },
    async deleteDoctor(id) {
      await axios.delete(`http://127.0.0.1:5000/api/doctor/${id}`);
      this.loadDocs();
    }
  }
}
</script>
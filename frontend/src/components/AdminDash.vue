<template>
  <div class="container mt-4">
    <h2 class="mb-4">🏥 Admin Dashboard</h2>
    
    <div class="row mb-4">
      <div class="col-md-4"><div class="card bg-primary text-white p-3 text-center"><h3>{{ stats.doctors }}</h3><small>Doctors</small></div></div>
      <div class="col-md-4"><div class="card bg-success text-white p-3 text-center"><h3>{{ stats.patients }}</h3><small>Patients</small></div></div>
      <div class="col-md-4"><div class="card bg-warning text-dark p-3 text-center"><h3>{{ stats.appointments }}</h3><small>Appointments</small></div></div>
    </div>

    <div class="row">
      <div class="col-md-4">
        <div class="card shadow">
          <div class="card-header bg-dark text-white">Add New Doctor</div>
          <div class="card-body">
            <input v-model="newDocName" class="form-control mb-2" placeholder="Username">
            <input v-model="newDocPass" class="form-control mb-2" placeholder="Password">
            <input v-model="newDocSpec" class="form-control mb-2" placeholder="Specialization">
            <button @click="addDoctor" class="btn btn-success w-100">Add Doctor</button>
          </div>
        </div>
      </div>

      <div class="col-md-8">
        <div class="card shadow">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span>Doctor List</span>
            <input v-model="search" @input="loadDocs" placeholder="Search..." class="form-control form-control-sm w-50">
          </div>
          <div class="card-body">
            <table class="table table-striped">
              <thead><tr><th>Name</th><th>Spec</th><th>Actions</th></tr></thead>
              <tbody>
                <tr v-for="doc in doctors" :key="doc.id">
                  <td>{{ doc.username }}</td>
                  <td>{{ doc.spec }}</td>
                  <td>
                    <button @click="deleteDoctor(doc.id)" class="btn btn-danger btn-sm">Delete</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() { return { stats: {}, doctors: [], newDocName: '', newDocPass: '', newDocSpec: '', search: '' } },
  async mounted() {
    this.refresh();
  },
  methods: {
    async refresh() {
      const s = await axios.get('http://127.0.0.1:5000/api/admin/dashboard');
      this.stats = s.data;
      this.loadDocs();
    },
    async loadDocs() {
      const d = await axios.get(`http://127.0.0.1:5000/api/doctors?search=${this.search}`);
      this.doctors = d.data;
    },
    async addDoctor() {
      await axios.post('http://127.0.0.1:5000/api/doctors', {
        username: this.newDocName, password: this.newDocPass, specialization: this.newDocSpec
      });
      this.newDocName = ''; this.newDocPass = ''; this.newDocSpec = '';
      this.refresh();
    },
    async deleteDoctor(id) {
      if(confirm('Are you sure?')) {
        await axios.delete(`http://127.0.0.1:5000/api/doctor/${id}`);
        this.refresh();
      }
    }
  }
}
</script>
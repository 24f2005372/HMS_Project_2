<template>
  <div class="container mt-4">
    <h2 class="mb-4">👤 Patient Dashboard</h2>

    <div class="row">
      <div class="col-md-5">
        <div class="card shadow mb-4">
          <div class="card-header bg-primary text-white">Book Appointment</div>
          <div class="card-body">
            <input v-model="search" @input="loadDoctors" class="form-control mb-3" placeholder="Search Doctor or Spec...">
            
            <label>Select Doctor:</label>
            <select v-model="selectedDoc" class="form-select mb-3">
              <option v-for="doc in doctors" :key="doc.id" :value="doc.id">
                Dr. {{ doc.username }} ({{ doc.spec }})
              </option>
            </select>
            
            <input type="date" v-model="date" class="form-control mb-2">
            <input type="time" v-model="time" class="form-control mb-2">
            
            <button @click="book" class="btn btn-primary w-100">Book Now</button>
            
            <div v-if="msg" class="alert alert-info mt-2">{{ msg }}</div>
          </div>
        </div>
        
        <div class="card shadow">
            <div class="card-body">
                <button @click="exportCSV" class="btn btn-secondary w-100">📂 Export History (CSV)</button>
            </div>
        </div>
      </div>

      <div class="col-md-7">
        <div class="card shadow">
          <div class="card-header">My Medical History</div>
          <div class="card-body">
            <table class="table table-bordered">
              <thead><tr><th>Date</th><th>Dr.</th><th>Status</th><th>Action</th></tr></thead>
              <tbody>
                <tr v-for="appt in appts" :key="appt.id">
                  <td>{{ appt.date }}<br><small>{{ appt.time }}</small></td>
                  <td>{{ appt.doctor }}</td>
                  <td>
                    <span v-if="appt.status=='Completed'" class="badge bg-success">Completed</span>
                    <span v-else-if="appt.status=='Cancelled'" class="badge bg-danger">Cancelled</span>
                    <span v-else class="badge bg-primary">Booked</span>
                  </td>
                  <td>
                    <button v-if="appt.status=='Booked'" @click="cancelAppt(appt.id)" class="btn btn-danger btn-sm">Cancel</button>
                    <div v-if="appt.status=='Completed'">
                        <small><strong>Dx:</strong> {{ appt.diagnosis }}</small>
                    </div>
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
  data() { 
      return { 
          doctors: [], appts: [], selectedDoc: null, date: '', time: '', search: '', msg: '', 
          currentUser: null // [FIX] Local user state
      } 
  },
  async mounted() {
    // [FIX] Load User from Storage immediately on load
    const stored = localStorage.getItem('user');
    if (stored) {
        this.currentUser = JSON.parse(stored);
    }
    this.loadDoctors();
    this.loadAppts();
  },
  methods: {
    async loadDoctors() {
      const d = await axios.get(`http://127.0.0.1:5000/api/doctors?search=${this.search}`);
      this.doctors = d.data;
    },

    async loadAppts() {
        if (this.currentUser && this.currentUser.id) {
            const a = await axios.get(`http://127.0.0.1:5000/api/patient/appointments/${this.currentUser.id}`);
            this.appts = a.data;
        }
    },

    async book() {
        try {
            // [FIX] Check for user existence
            if (!this.currentUser) {
                this.msg = "Session Expired. Please Logout and Login again.";
                return;
            }
            if (!this.selectedDoc || !this.date || !this.time) {
                this.msg = "Please fill all fields!";
                return;
            }

            await axios.post('http://127.0.0.1:5000/api/patient/book', {
                user_id: this.currentUser.id, 
                doctor_id: this.selectedDoc, 
                date: this.date, 
                time: this.time
            });
            this.msg = 'Booked Successfully!';
            this.loadAppts();
        } catch(e) { 
            this.msg = e.response && e.response.data ? e.response.data.message : 'Slot Already Taken!'; 
        }
    },

    async cancelAppt(id) {
        if(confirm('Cancel this appointment?')) {
            await axios.delete(`http://127.0.0.1:5000/api/patient/cancel/${id}`);
            this.loadAppts();
        }
    },

    async exportCSV() {
        if (!this.currentUser) return;
        const res = await axios.get(`http://127.0.0.1:5000/api/export_csv/${this.currentUser.id}`);
        alert(res.data.message);
    }
  }
}
</script>
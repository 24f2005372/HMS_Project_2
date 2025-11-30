<template>
  <div class="container mt-4">
    <h2 class="mb-4">🩺 Doctor Dashboard</h2>
    
    <div class="row">
      <div class="col-md-12">
        <div v-if="appts.length === 0" class="alert alert-info">No appointments assigned.</div>
        
        <div class="row">
            <div v-for="appt in appts" :key="appt.id" class="col-md-6 mb-4">
                <div class="card shadow h-100">
                    <div class="card-header d-flex justify-content-between align-items-center bg-light">
                        <strong>{{ appt.patient }}</strong>
                        <button @click="viewHistory(appt.patient_id)" class="btn btn-sm btn-outline-info">📜 History</button>
                    </div>
                    <div class="card-body">
                        <p class="mb-1">📅 {{ appt.date }} at {{ appt.time }}</p>
                        
                        <div v-if="appt.status === 'Booked'">
                            <span class="badge bg-primary mb-3">Booked</span>
                            <hr>
                            <label>Diagnosis:</label>
                            <textarea v-model="appt.dx" class="form-control mb-2"></textarea>
                            <label>Prescription:</label>
                            <textarea v-model="appt.rx" class="form-control mb-2"></textarea>
                            <button @click="complete(appt)" class="btn btn-success w-100">Complete Visit</button>
                        </div>

                        <div v-else-if="appt.status === 'Cancelled'">
                             <div class="alert alert-danger p-2 mt-2">🚫 Appointment Cancelled</div>
                        </div>

                        <div v-else>
                            <div class="alert alert-success p-2 mt-2">✅ Visit Completed</div>
                            <hr>
                            <small><strong>Dx:</strong> {{ appt.diagnosis }}</small><br>
                            <small><strong>Rx:</strong> {{ appt.prescription }}</small>
                        </div>

                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>

    <div v-if="showHistory" class="modal d-block" style="background: rgba(0,0,0,0.5)">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Patient Medical History</h5>
                    <button @click="showHistory = false" class="btn-close"></button>
                </div>
                <div class="modal-body">
                    <ul class="list-group">
                        <li v-for="h in history" :key="h.date" class="list-group-item">
                            <small>{{ h.date }} (Dr. {{ h.doctor }})</small><br>
                            <strong>{{ h.diagnosis }}</strong>
                        </li>
                        <li v-if="history.length===0" class="list-group-item text-center">No completed past visits.</li>
                    </ul>
                </div>
                <div class="modal-footer">
                    <button @click="showHistory = false" class="btn btn-secondary">Close</button>
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
          appts: [], 
          showHistory: false, 
          history: [],
          currentUser: null // [FIX] Store user locally
      } 
  },
  async mounted() {
    // [FIX] Force load user from storage immediately
    const stored = localStorage.getItem('user');
    if (stored) {
        this.currentUser = JSON.parse(stored);
        this.loadAppts();
    }
  },
  methods: {
    async loadAppts() {
        if (this.currentUser && this.currentUser.id) {
            try {
                // Fetch appointments using the saved User ID
                const a = await axios.get(`http://127.0.0.1:5000/api/doctor/appointments/${this.currentUser.id}`);
                // Add local fields for the input boxes
                this.appts = a.data.map(x => ({...x, dx: '', rx: ''}));
            } catch (e) {
                console.error("Error loading appointments:", e);
            }
        }
    },
    async complete(appt) {
        await axios.post(`http://127.0.0.1:5000/api/doctor/complete/${appt.id}`, {
            diagnosis: appt.dx, prescription: appt.rx
        });
        appt.status = 'Completed';
        appt.diagnosis = appt.dx;
        appt.prescription = appt.rx;
    },
    async viewHistory(patientId) {
        const res = await axios.get(`http://127.0.0.1:5000/api/patient/history/${patientId}`);
        this.history = res.data;
        this.showHistory = true;
    }
  }
}
</script>
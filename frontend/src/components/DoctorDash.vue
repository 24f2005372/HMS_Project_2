<template>
  <div class="container-fluid mt-4 px-4">
    <h2 class="mb-4">🩺 Doctor Dashboard — Dr. {{ currentUser?.username }}</h2>

    <ul class="nav nav-tabs mb-4">
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='appointments'}" @click="tab='appointments'" href="#">Appointments</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='patients'}" @click="tab='patients'" href="#">My Patients</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='availability'}" @click="tab='availability'" href="#">Set Availability</a></li>
    </ul>

    <!-- APPOINTMENTS TAB -->
    <div v-if="tab==='appointments'">
      <div class="d-flex gap-2 mb-3">
        <button @click="apptFilter='all'; loadAppts()" :class="apptFilter==='all'?'btn btn-primary':'btn btn-outline-primary'" class="btn btn-sm">All</button>
        <button @click="apptFilter='today'; loadAppts()" :class="apptFilter==='today'?'btn btn-primary':'btn btn-outline-primary'" class="btn btn-sm">Today</button>
        <button @click="apptFilter='week'; loadAppts()" :class="apptFilter==='week'?'btn btn-primary':'btn btn-outline-primary'" class="btn btn-sm">This Week</button>
      </div>

      <div v-if="appts.length === 0" class="alert alert-info">No appointments found.</div>

      <div class="row">
        <div v-for="appt in appts" :key="appt.id" class="col-md-6 mb-4">
          <div class="card shadow h-100">
            <div class="card-header d-flex justify-content-between align-items-center bg-light">
              <strong>👤 {{ appt.patient }}</strong>
              <div>
                <span :class="statusBadge(appt.status)" class="me-2">{{ appt.status }}</span>
                <button @click="viewHistory(appt.patient_id)" class="btn btn-sm btn-outline-info">📜 History</button>
              </div>
            </div>
            <div class="card-body">
              <p class="mb-2">📅 {{ appt.date }} at ⏰ {{ appt.time }}</p>

              <div v-if="appt.status === 'Booked'">
                <hr>
                <div class="mb-2">
                  <label class="form-label fw-bold">Diagnosis</label>
                  <textarea v-model="appt.dx" class="form-control form-control-sm" rows="2"></textarea>
                </div>
                <div class="mb-2">
                  <label class="form-label fw-bold">Prescription</label>
                  <textarea v-model="appt.rx" class="form-control form-control-sm" rows="2"></textarea>
                </div>
                <div class="mb-2">
                  <label class="form-label fw-bold">Notes</label>
                  <textarea v-model="appt.notes_input" class="form-control form-control-sm" rows="2"></textarea>
                </div>
                <div class="mb-3">
                  <label class="form-label fw-bold">Next Visit Date</label>
                  <input type="date" v-model="appt.next_visit_input" class="form-control form-control-sm">
                </div>
                <div class="d-flex gap-2">
                  <button @click="completeAppt(appt)" class="btn btn-success btn-sm flex-fill">✅ Complete Visit</button>
                  <button @click="cancelAppt(appt.id)" class="btn btn-danger btn-sm flex-fill">❌ Cancel</button>
                </div>
              </div>

              <div v-else-if="appt.status === 'Completed'" class="mt-2">
                <div class="alert alert-success py-2 mb-2">✅ Visit Completed</div>
                <small><strong>Dx:</strong> {{ appt.diagnosis }}</small><br>
                <small><strong>Rx:</strong> {{ appt.prescription }}</small><br>
                <small v-if="appt.notes"><strong>Notes:</strong> {{ appt.notes }}</small><br>
                <small v-if="appt.next_visit"><strong>Next Visit:</strong> {{ appt.next_visit }}</small>
              </div>

              <div v-else class="alert alert-danger py-2 mt-2">🚫 Cancelled</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- PATIENTS TAB -->
    <div v-if="tab==='patients'">
      <div class="card shadow">
        <div class="card-header">Assigned Patients</div>
        <div class="card-body p-0">
          <table class="table table-hover mb-0">
            <thead class="table-light"><tr><th>Name</th><th>Phone</th><th>DOB</th><th>Blood Group</th><th>Action</th></tr></thead>
            <tbody>
              <tr v-for="p in patients" :key="p.id">
                <td>{{ p.username }}</td>
                <td>{{ p.phone || '—' }}</td>
                <td>{{ p.dob || '—' }}</td>
                <td>{{ p.blood_group || '—' }}</td>
                <td><button @click="viewHistory(p.id)" class="btn btn-sm btn-outline-info">📜 History</button></td>
              </tr>
              <tr v-if="patients.length === 0"><td colspan="5" class="text-center text-muted">No patients yet.</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- AVAILABILITY TAB -->
    <div v-if="tab==='availability'">
      <div class="card shadow">
        <div class="card-header">Set Availability (Next 7 Days)</div>
        <div class="card-body">
          <p class="text-muted small">Set your available time slots for the next 7 days. Each day can have one slot (or leave blank to mark unavailable).</p>
          <table class="table table-bordered">
            <thead class="table-light"><tr><th>Date</th><th>Start Time</th><th>End Time</th></tr></thead>
            <tbody>
              <tr v-for="slot in availabilitySlots" :key="slot.date">
                <td><strong>{{ slot.date }}</strong></td>
                <td><input type="time" v-model="slot.start_time" class="form-control form-control-sm"></td>
                <td><input type="time" v-model="slot.end_time" class="form-control form-control-sm"></td>
              </tr>
            </tbody>
          </table>
          <button @click="saveAvailability" class="btn btn-primary mt-2">💾 Save Availability</button>
          <div v-if="availMsg" class="alert alert-success mt-2 py-1">{{ availMsg }}</div>
        </div>
      </div>
    </div>

    <!-- History Modal -->
    <div v-if="showHistory" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Patient Medical History</h5>
            <button @click="showHistory=false" class="btn-close"></button>
          </div>
          <div class="modal-body">
            <div v-if="history.length === 0" class="text-center text-muted">No completed visits on record.</div>
            <div v-for="(h, i) in history" :key="i" class="card mb-2">
              <div class="card-body py-2">
                <div class="d-flex justify-content-between"><strong>{{ h.date }}</strong><span class="badge bg-success">Completed</span></div>
                <div><strong>Dr. {{ h.doctor }}</strong></div>
                <div><small><strong>Dx:</strong> {{ h.diagnosis }}</small></div>
                <div><small><strong>Rx:</strong> {{ h.prescription }}</small></div>
                <div v-if="h.notes"><small><strong>Notes:</strong> {{ h.notes }}</small></div>
                <div v-if="h.next_visit"><small><strong>Next Visit:</strong> {{ h.next_visit }}</small></div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="showHistory=false" class="btn btn-secondary">Close</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios'
const API = 'http://127.0.0.1:5000/api'

export default {
  data() {
    return {
      tab: 'appointments', apptFilter: 'all',
      appts: [], patients: [], availabilitySlots: [],
      showHistory: false, history: [], availMsg: '',
      currentUser: null
    }
  },
  async mounted() {
    const stored = localStorage.getItem('user')
    if (stored) { this.currentUser = JSON.parse(stored) }
    this.generateAvailabilitySlots()
    await this.loadAppts()
    await this.loadPatients()
    await this.loadExistingAvailability()
  },
  methods: {
    headers() { return { Authorization: `Bearer ${this.currentUser?.token}` } },
    async loadAppts() {
      if (!this.currentUser) return
      const r = await axios.get(`${API}/doctor/appointments/${this.currentUser.id}?filter=${this.apptFilter}`)
      this.appts = r.data.map(x => ({ ...x, dx: '', rx: '', notes_input: '', next_visit_input: '' }))
    },
    async loadPatients() {
      if (!this.currentUser) return
      const r = await axios.get(`${API}/doctor/patients/${this.currentUser.id}`)
      this.patients = r.data
    },
    async completeAppt(appt) {
      await axios.post(`${API}/doctor/complete/${appt.id}`, {
        diagnosis: appt.dx, prescription: appt.rx,
        notes: appt.notes_input, next_visit: appt.next_visit_input
      })
      await this.loadAppts()
    },
    async cancelAppt(id) {
      if (!confirm('Cancel this appointment?')) return
      await axios.post(`${API}/doctor/cancel/${id}`)
      await this.loadAppts()
    },
    async viewHistory(patientId) {
      const r = await axios.get(`${API}/patient/history/${patientId}`)
      this.history = r.data
      this.showHistory = true
    },
    generateAvailabilitySlots() {
      const slots = []
      const today = new Date()
      for (let i = 0; i < 7; i++) {
        const d = new Date(today)
        d.setDate(today.getDate() + i)
        const dateStr = d.toISOString().split('T')[0]
        slots.push({ date: dateStr, start_time: '09:00', end_time: '17:00' })
      }
      this.availabilitySlots = slots
    },
    async loadExistingAvailability() {
      if (!this.currentUser) return
      try {
        const r = await axios.get(`${API}/doctor/availability/${this.currentUser.id}`)
        const existing = r.data
        this.availabilitySlots = this.availabilitySlots.map(slot => {
          const found = existing.find(e => e.date === slot.date)
          return found ? { ...slot, start_time: found.start_time, end_time: found.end_time } : slot
        })
      } catch(e) {}
    },
    async saveAvailability() {
      if (!this.currentUser) return
      const payload = this.availabilitySlots.filter(s => s.start_time && s.end_time)
      await axios.post(`${API}/doctor/availability/${this.currentUser.id}`, payload)
      this.availMsg = 'Availability saved!'
      setTimeout(() => { this.availMsg = '' }, 3000)
    },
    statusBadge(s) {
      return s === 'Completed' ? 'badge bg-success' : s === 'Cancelled' ? 'badge bg-danger' : 'badge bg-primary'
    }
  }
}
</script>

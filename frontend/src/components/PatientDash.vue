<template>
  <div class="container-fluid mt-4 px-4">
    <h2 class="mb-4">👤 Patient Dashboard — {{ currentUser?.username }}</h2>

    <ul class="nav nav-tabs mb-4">
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='book'}" @click="tab='book'" href="#">Book Appointment</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='appointments'}" @click="tab='appointments'" href="#">My Appointments</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='departments'}" @click="tab='departments'" href="#">Departments & Doctors</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='profile'}" @click="loadProfile(); tab='profile'" href="#">My Profile</a></li>
    </ul>

    <!-- BOOK APPOINTMENT TAB -->
    <div v-if="tab==='book'">
      <div class="row">
        <div class="col-md-5">
          <div class="card shadow mb-4">
            <div class="card-header bg-primary text-white">Book New Appointment</div>
            <div class="card-body">
              <input v-model="search" @input="loadDoctors" class="form-control mb-3" placeholder="🔍 Search Doctor or Specialization...">
              <label class="form-label">Select Doctor</label>
              <select v-model="selectedDoc" @change="loadDocAvailability" class="form-select mb-3">
                <option value="">-- Select --</option>
                <option v-for="doc in doctors" :key="doc.id" :value="doc.id">
                  Dr. {{ doc.username }} ({{ doc.spec }}) — {{ doc.department || 'No Dept' }}
                </option>
              </select>
              <div v-if="selectedDoc && docAvailability.length > 0" class="mb-3">
                <label class="form-label">Available Slots</label>
                <select v-model="selectedSlot" class="form-select mb-2">
                  <option value="">-- Select Slot --</option>
                  <option v-for="s in docAvailability" :key="s.date+s.start_time" :value="s">
                    {{ s.date }} ({{ s.start_time }} – {{ s.end_time }})
                  </option>
                </select>
              </div>
              <div v-if="selectedDoc && docAvailability.length === 0" class="alert alert-warning py-2">No available slots for this doctor. Ask them to set availability.</div>
              <label class="form-label">Date</label>
              <input type="date" v-model="date" class="form-control mb-2">
              <label class="form-label">Time</label>
              <input type="time" v-model="time" class="form-control mb-3">
              <button @click="book" class="btn btn-primary w-100">📅 Book Now</button>
              <div v-if="msg" class="alert mt-2 py-2" :class="msgType">{{ msg }}</div>
            </div>
          </div>
        </div>
        <div class="col-md-7" v-if="selectedDoc">
          <div class="card shadow" v-for="doc in doctors.filter(d=>d.id===selectedDoc)" :key="doc.id">
            <div class="card-header bg-light"><strong>Doctor Profile</strong></div>
            <div class="card-body">
              <h5>Dr. {{ doc.username }}</h5>
              <p><strong>Specialization:</strong> {{ doc.spec }}</p>
              <p><strong>Department:</strong> {{ doc.department || '—' }}</p>
              <p><strong>Experience:</strong> {{ doc.experience }} years</p>
              <p v-if="doc.bio"><strong>Bio:</strong> {{ doc.bio }}</p>
              <p v-if="doc.phone"><strong>Contact:</strong> {{ doc.phone }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MY APPOINTMENTS TAB -->
    <div v-if="tab==='appointments'">
      <div class="mb-3">
        <button @click="exportCSV" class="btn btn-outline-secondary btn-sm">📂 Export Treatment History (CSV)</button>
      </div>
      <div class="card shadow">
        <div class="card-header">My Appointments & History</div>
        <div class="card-body p-0">
          <table class="table table-hover mb-0">
            <thead class="table-light"><tr><th>Date</th><th>Time</th><th>Doctor</th><th>Spec</th><th>Status</th><th>Treatment</th><th>Actions</th></tr></thead>
            <tbody>
              <tr v-for="appt in appts" :key="appt.id">
                <td>{{ appt.date }}</td>
                <td>{{ appt.time }}</td>
                <td>{{ appt.doctor }}</td>
                <td>{{ appt.spec }}</td>
                <td><span :class="statusBadge(appt.status)">{{ appt.status }}</span></td>
                <td>
                  <div v-if="appt.status==='Completed'">
                    <small><strong>Dx:</strong> {{ appt.diagnosis || '—' }}</small><br>
                    <small><strong>Rx:</strong> {{ appt.prescription || '—' }}</small>
                    <div v-if="appt.next_visit"><small><strong>Next:</strong> {{ appt.next_visit }}</small></div>
                  </div>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>
                  <button v-if="appt.status==='Booked'" @click="openReschedule(appt)" class="btn btn-warning btn-sm me-1">Reschedule</button>
                  <button v-if="appt.status==='Booked'" @click="cancelAppt(appt.id)" class="btn btn-danger btn-sm">Cancel</button>
                </td>
              </tr>
              <tr v-if="appts.length===0"><td colspan="7" class="text-center text-muted py-4">No appointments yet.</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- DEPARTMENTS & DOCTORS TAB -->
    <div v-if="tab==='departments'">
      <div class="row g-3">
        <div v-for="dept in departments" :key="dept.id" class="col-md-4">
          <div class="card shadow h-100">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
              <strong>{{ dept.name }}</strong>
              <span class="badge bg-light text-dark">{{ dept.doctors_count }} doctors</span>
            </div>
            <div class="card-body">
              <p class="text-muted small">{{ dept.description }}</p>
              <button @click="viewDeptDoctors(dept.name)" class="btn btn-outline-primary btn-sm">View Doctors</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="deptDoctors.length > 0" class="mt-4">
        <h5>Doctors in {{ selectedDept }}</h5>
        <div class="row g-3">
          <div v-for="doc in deptDoctors" :key="doc.id" class="col-md-4">
            <div class="card shadow">
              <div class="card-body">
                <h6>Dr. {{ doc.username }}</h6>
                <p class="mb-1 small"><strong>Spec:</strong> {{ doc.spec }}</p>
                <p class="mb-1 small" v-if="doc.experience"><strong>Experience:</strong> {{ doc.experience }} yrs</p>
                <p class="mb-2 small" v-if="doc.bio">{{ doc.bio }}</p>
                <button @click="selectedDoc=doc.id; loadDocAvailability(); tab='book'" class="btn btn-primary btn-sm">Book Appointment</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- PROFILE TAB -->
    <div v-if="tab==='profile'">
      <div class="card shadow mx-auto" style="max-width:500px">
        <div class="card-header bg-dark text-white">Edit My Profile</div>
        <div class="card-body">
          <div class="mb-2"><label class="form-label">Username</label><input :value="currentUser?.username" class="form-control" disabled></div>
          <div class="mb-2"><label class="form-label">Email</label><input v-model="profile.email" class="form-control"></div>
          <div class="mb-2"><label class="form-label">Phone</label><input v-model="profile.phone" class="form-control"></div>
          <div class="mb-2"><label class="form-label">Address</label><input v-model="profile.address" class="form-control"></div>
          <div class="mb-2"><label class="form-label">Date of Birth</label><input type="date" v-model="profile.dob" class="form-control"></div>
          <div class="mb-3"><label class="form-label">Blood Group</label><input v-model="profile.blood_group" class="form-control" placeholder="e.g. A+"></div>
          <button @click="saveProfile" class="btn btn-success w-100">💾 Save Profile</button>
          <div v-if="profileMsg" class="alert alert-success mt-2 py-1">{{ profileMsg }}</div>
        </div>
      </div>
    </div>

    <!-- Reschedule Modal -->
    <div v-if="rescheduleModal" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title">Reschedule Appointment</h5><button @click="rescheduleModal=false" class="btn-close"></button></div>
          <div class="modal-body">
            <label class="form-label">New Date</label>
            <input type="date" v-model="rescheduleDate" class="form-control mb-3">
            <label class="form-label">New Time</label>
            <input type="time" v-model="rescheduleTime" class="form-control">
            <div v-if="rescheduleMsg" class="alert alert-danger mt-3 py-2">{{ rescheduleMsg }}</div>
          </div>
          <div class="modal-footer">
            <button @click="confirmReschedule" class="btn btn-warning">Reschedule</button>
            <button @click="rescheduleModal=false; rescheduleMsg=''" class="btn btn-secondary">Cancel</button>
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
      tab: 'book', currentUser: null,
      doctors: [], appts: [], departments: [], deptDoctors: [], selectedDept: '',
      docAvailability: [], selectedSlot: null,
      search: '', selectedDoc: null, date: '', time: '',
      msg: '', msgType: 'alert-info',
      profile: { email:'', phone:'', address:'', dob:'', blood_group:'' },
      profileMsg: '',
      rescheduleModal: false, rescheduleApptId: null,
      rescheduleDate: '', rescheduleTime: '', rescheduleMsg: ''
    }
  },
  async mounted() {
    const stored = localStorage.getItem('user')
    if (stored) this.currentUser = JSON.parse(stored)
    await this.loadDoctors()
    await this.loadAppts()
    await this.loadDepartments()
  },
  methods: {
    async loadDoctors() {
      const r = await axios.get(`${API}/doctors?search=${this.search}`)
      this.doctors = r.data.filter(d => !d.is_blacklisted)
    },
    async loadAppts() {
      if (!this.currentUser) return
      const r = await axios.get(`${API}/patient/appointments/${this.currentUser.id}`)
      this.appts = r.data
    },
    async loadDepartments() {
      const r = await axios.get(`${API}/departments`)
      this.departments = r.data
    },
    async loadDocAvailability() {
      if (!this.selectedDoc) return
      const r = await axios.get(`${API}/doctor/${this.selectedDoc}/availability`)
      this.docAvailability = r.data
    },
    viewDeptDoctors(deptName) {
      this.selectedDept = deptName
      this.deptDoctors = this.doctors.filter(d => d.department === deptName)
    },
    async book() {
      if (!this.selectedDoc || !this.date || !this.time) {
        this.msg = 'Please fill in all fields'; this.msgType = 'alert-warning'; return
      }
      try {
        await axios.post(`${API}/patient/book`, {
          user_id: this.currentUser.id, doctor_id: this.selectedDoc,
          date: this.date, time: this.time
        })
        this.msg = '✅ Appointment booked successfully!'; this.msgType = 'alert-success'
        this.selectedDoc = null; this.date = ''; this.time = ''
        await this.loadAppts()
      } catch(e) {
        this.msg = e.response?.data?.message || 'Slot already taken'
        this.msgType = 'alert-danger'
      }
    },
    async cancelAppt(id) {
      if (!confirm('Cancel this appointment?')) return
      await axios.post(`${API}/patient/cancel/${id}`)
      await this.loadAppts()
    },
    openReschedule(appt) {
      this.rescheduleApptId = appt.id
      this.rescheduleDate = appt.date
      this.rescheduleTime = appt.time
      this.rescheduleModal = true
    },
    async confirmReschedule() {
      try {
        await axios.put(`${API}/patient/reschedule/${this.rescheduleApptId}`, {
          date: this.rescheduleDate, time: this.rescheduleTime
        })
        this.rescheduleModal = false
        this.rescheduleMsg = ''
        await this.loadAppts()
      } catch(e) {
        this.rescheduleMsg = e.response?.data?.message || 'New slot is already booked'
      }
    },
    async loadProfile() {
      if (!this.currentUser) return
      const r = await axios.get(`${API}/patient/profile/${this.currentUser.id}`)
      this.profile = r.data
    },
    async saveProfile() {
      await axios.put(`${API}/patient/profile/${this.currentUser.id}`, this.profile)
      this.profileMsg = '✅ Profile updated!'
      setTimeout(() => { this.profileMsg = '' }, 3000)
    },
    async exportCSV() {
      if (!this.currentUser) return
      const r = await axios.get(`${API}/export_csv/${this.currentUser.id}`)
      alert(r.data.message)
    },
    statusBadge(s) {
      return s === 'Completed' ? 'badge bg-success' : s === 'Cancelled' ? 'badge bg-danger' : 'badge bg-primary'
    }
  }
}
</script>

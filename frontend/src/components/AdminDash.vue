<template>
  <div class="container-fluid mt-4 px-4">
    <h2 class="mb-4">🏥 Admin Dashboard</h2>

    <!-- Stats Row -->
    <div class="row g-3 mb-4">
      <div class="col-md-3"><div class="card bg-primary text-white text-center p-3"><h3>{{ stats.doctors }}</h3><small>Doctors</small></div></div>
      <div class="col-md-3"><div class="card bg-success text-white text-center p-3"><h3>{{ stats.patients }}</h3><small>Patients</small></div></div>
      <div class="col-md-3"><div class="card bg-warning text-dark text-center p-3"><h3>{{ stats.appointments }}</h3><small>Total Appointments</small></div></div>
      <div class="col-md-3"><div class="card bg-info text-white text-center p-3"><h3>{{ stats.completed }}</h3><small>Completed</small></div></div>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-tabs mb-4">
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='doctors'}" @click="tab='doctors'" href="#">Doctors</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='patients'}" @click="tab='patients'" href="#">Patients</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='appointments'}" @click="tab='appointments'" href="#">All Appointments</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='departments'}" @click="tab='departments'" href="#">Departments</a></li>
    </ul>

    <!-- DOCTORS TAB -->
    <div v-if="tab==='doctors'">
      <div class="row mb-3">
        <div class="col-md-5">
          <div class="card shadow">
            <div class="card-header bg-dark text-white">Add New Doctor</div>
            <div class="card-body">
              <input v-model="newDoc.username" class="form-control mb-2" placeholder="Username">
              <input v-model="newDoc.password" type="password" class="form-control mb-2" placeholder="Password">
              <input v-model="newDoc.email" class="form-control mb-2" placeholder="Email">
              <input v-model="newDoc.specialization" class="form-control mb-2" placeholder="Specialization">
              <input v-model="newDoc.experience" type="number" class="form-control mb-2" placeholder="Experience (years)">
              <select v-model="newDoc.department_id" class="form-select mb-2">
                <option value="">Select Department</option>
                <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
              </select>
              <textarea v-model="newDoc.bio" class="form-control mb-2" placeholder="Bio / Profile" rows="2"></textarea>
              <button @click="addDoctor" class="btn btn-success w-100">➕ Add Doctor</button>
              <div v-if="docMsg" class="alert alert-info mt-2 py-1">{{ docMsg }}</div>
            </div>
          </div>
        </div>
        <div class="col-md-7">
          <div class="card shadow">
            <div class="card-header d-flex justify-content-between align-items-center">
              <span>Registered Doctors</span>
              <input v-model="docSearch" @input="loadDoctors" class="form-control form-control-sm w-50" placeholder="Search name / specialization...">
            </div>
            <div class="card-body p-0">
              <table class="table table-hover mb-0">
                <thead class="table-light"><tr><th>Name</th><th>Spec</th><th>Dept</th><th>Status</th><th>Actions</th></tr></thead>
                <tbody>
                  <tr v-for="doc in doctors" :key="doc.id" :class="{'table-danger': doc.is_blacklisted}">
                    <td>{{ doc.username }}</td>
                    <td>{{ doc.spec }}</td>
                    <td>{{ doc.department || '—' }}</td>
                    <td><span :class="doc.is_blacklisted ? 'badge bg-danger' : 'badge bg-success'">{{ doc.is_blacklisted ? 'Blacklisted' : 'Active' }}</span></td>
                    <td>
                      <button @click="openEditDoctor(doc)" class="btn btn-warning btn-sm me-1">Edit</button>
                      <button @click="toggleBlacklist(doc.id,'doctor')" class="btn btn-sm me-1" :class="doc.is_blacklisted ? 'btn-success' : 'btn-secondary'">{{ doc.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}</button>
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

    <!-- PATIENTS TAB -->
    <div v-if="tab==='patients'">
      <div class="card shadow">
        <div class="card-header d-flex justify-content-between align-items-center">
          <span>Registered Patients</span>
          <input v-model="patSearch" @input="loadPatients" class="form-control form-control-sm w-50" placeholder="Search name / phone / email...">
        </div>
        <div class="card-body p-0">
          <table class="table table-hover mb-0">
            <thead class="table-light"><tr><th>Name</th><th>Email</th><th>Phone</th><th>Blood Group</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
              <tr v-for="p in patients" :key="p.id" :class="{'table-danger': p.is_blacklisted}">
                <td>{{ p.username }}</td>
                <td>{{ p.email || '—' }}</td>
                <td>{{ p.phone || '—' }}</td>
                <td>{{ p.blood_group || '—' }}</td>
                <td><span :class="p.is_blacklisted ? 'badge bg-danger' : 'badge bg-success'">{{ p.is_blacklisted ? 'Blacklisted' : 'Active' }}</span></td>
                <td>
                  <button @click="openEditPatient(p)" class="btn btn-warning btn-sm me-1">Edit</button>
                  <button @click="toggleBlacklist(p.id,'patient')" class="btn btn-sm" :class="p.is_blacklisted ? 'btn-success' : 'btn-secondary'">{{ p.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- APPOINTMENTS TAB -->
    <div v-if="tab==='appointments'">
      <div class="card shadow">
        <div class="card-header">All Appointments</div>
        <div class="card-body p-0">
          <table class="table table-hover mb-0">
            <thead class="table-light"><tr><th>ID</th><th>Patient</th><th>Doctor</th><th>Date</th><th>Time</th><th>Status</th><th>Diagnosis</th></tr></thead>
            <tbody>
              <tr v-for="a in appointments" :key="a.id">
                <td>{{ a.id }}</td>
                <td>{{ a.patient }}</td>
                <td>{{ a.doctor }}</td>
                <td>{{ a.date }}</td>
                <td>{{ a.time }}</td>
                <td><span :class="statusBadge(a.status)">{{ a.status }}</span></td>
                <td>{{ a.diagnosis || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- DEPARTMENTS TAB -->
    <div v-if="tab==='departments'">
      <div class="row">
        <div class="col-md-4">
          <div class="card shadow">
            <div class="card-header bg-dark text-white">Add Department</div>
            <div class="card-body">
              <input v-model="newDept.name" class="form-control mb-2" placeholder="Department Name">
              <textarea v-model="newDept.description" class="form-control mb-2" placeholder="Description" rows="2"></textarea>
              <button @click="addDepartment" class="btn btn-success w-100">Add</button>
            </div>
          </div>
        </div>
        <div class="col-md-8">
          <div class="card shadow">
            <div class="card-header">Departments</div>
            <div class="card-body p-0">
              <table class="table mb-0">
                <thead class="table-light"><tr><th>Name</th><th>Description</th><th>Doctors</th></tr></thead>
                <tbody>
                  <tr v-for="d in departments" :key="d.id">
                    <td><strong>{{ d.name }}</strong></td>
                    <td>{{ d.description }}</td>
                    <td>{{ d.doctors_count }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Doctor Modal -->
    <div v-if="editDocModal" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog"><div class="modal-content">
        <div class="modal-header"><h5 class="modal-title">Edit Doctor</h5><button @click="editDocModal=false" class="btn-close"></button></div>
        <div class="modal-body">
          <input v-model="editDoc.username" class="form-control mb-2" placeholder="Username">
          <input v-model="editDoc.email" class="form-control mb-2" placeholder="Email">
          <input v-model="editDoc.spec" class="form-control mb-2" placeholder="Specialization">
          <input v-model="editDoc.experience" type="number" class="form-control mb-2" placeholder="Experience (years)">
          <input v-model="editDoc.phone" class="form-control mb-2" placeholder="Phone">
          <textarea v-model="editDoc.bio" class="form-control mb-2" placeholder="Bio" rows="2"></textarea>
          <select v-model="editDoc.department_id" class="form-select mb-2">
            <option value="">Select Department</option>
            <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
          </select>
        </div>
        <div class="modal-footer">
          <button @click="saveEditDoctor" class="btn btn-success">Save</button>
          <button @click="editDocModal=false" class="btn btn-secondary">Cancel</button>
        </div>
      </div></div>
    </div>

    <!-- Edit Patient Modal -->
    <div v-if="editPatModal" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog"><div class="modal-content">
        <div class="modal-header"><h5 class="modal-title">Edit Patient</h5><button @click="editPatModal=false" class="btn-close"></button></div>
        <div class="modal-body">
          <input v-model="editPat.email" class="form-control mb-2" placeholder="Email">
          <input v-model="editPat.phone" class="form-control mb-2" placeholder="Phone">
          <input v-model="editPat.address" class="form-control mb-2" placeholder="Address">
          <input v-model="editPat.dob" type="date" class="form-control mb-2" placeholder="Date of Birth">
          <input v-model="editPat.blood_group" class="form-control mb-2" placeholder="Blood Group">
        </div>
        <div class="modal-footer">
          <button @click="saveEditPatient" class="btn btn-success">Save</button>
          <button @click="editPatModal=false" class="btn btn-secondary">Cancel</button>
        </div>
      </div></div>
    </div>

  </div>
</template>

<script>
import axios from 'axios'
const API = 'http://127.0.0.1:5000/api'

export default {
  data() {
    return {
      tab: 'doctors', stats: {}, doctors: [], patients: [], appointments: [], departments: [],
      docSearch: '', patSearch: '', docMsg: '',
      newDoc: { username:'', password:'', email:'', specialization:'', experience:0, department_id:'', bio:'' },
      newDept: { name:'', description:'' },
      editDocModal: false, editDoc: {}, editDocId: null,
      editPatModal: false, editPat: {}, editPatId: null,
    }
  },
  computed: {
    token() { const u = JSON.parse(localStorage.getItem('user')||'{}'); return u.token || '' }
  },
  async mounted() {
    await this.refresh()
  },
  methods: {
    headers() { return { Authorization: `Bearer ${this.token}` } },
    async refresh() {
      const s = await axios.get(`${API}/admin/dashboard`, { headers: this.headers() })
      this.stats = s.data
      await this.loadDoctors()
      await this.loadPatients()
      await this.loadAppointments()
      await this.loadDepartments()
    },
    async loadDoctors() {
      const r = await axios.get(`${API}/doctors?search=${this.docSearch}`, { headers: this.headers() })
      this.doctors = r.data
    },
    async loadPatients() {
      const r = await axios.get(`${API}/admin/patients?search=${this.patSearch}`, { headers: this.headers() })
      this.patients = r.data
    },
    async loadAppointments() {
      const r = await axios.get(`${API}/admin/appointments`, { headers: this.headers() })
      this.appointments = r.data
    },
    async loadDepartments() {
      const r = await axios.get(`${API}/departments`)
      this.departments = r.data
    },
    async addDoctor() {
      try {
        await axios.post(`${API}/doctors`, this.newDoc, { headers: this.headers() })
        this.docMsg = 'Doctor added!'
        this.newDoc = { username:'', password:'', email:'', specialization:'', experience:0, department_id:'', bio:'' }
        await this.loadDoctors()
      } catch(e) { this.docMsg = e.response?.data?.message || 'Error' }
    },
    async deleteDoctor(id) {
      if (!confirm('Permanently delete this doctor?')) return
      await axios.delete(`${API}/doctor/${id}`, { headers: this.headers() })
      await this.loadDoctors()
    },
    async toggleBlacklist(id, type) {
      const url = type === 'doctor' ? `${API}/doctor/${id}/blacklist` : `${API}/admin/patient/${id}/blacklist`
      await axios.post(url, {}, { headers: this.headers() })
      type === 'doctor' ? await this.loadDoctors() : await this.loadPatients()
    },
    openEditDoctor(doc) {
      this.editDocId = doc.id
      this.editDoc = { username: doc.username, email: doc.email, spec: doc.spec,
                       experience: doc.experience, phone: doc.phone, bio: doc.bio, department_id: doc.department_id }
      this.editDocModal = true
    },
    async saveEditDoctor() {
      await axios.put(`${API}/doctor/${this.editDocId}`, this.editDoc, { headers: this.headers() })
      this.editDocModal = false
      await this.loadDoctors()
    },
    openEditPatient(p) {
      this.editPatId = p.id
      this.editPat = { email: p.email, phone: p.phone, address: p.address, dob: p.dob, blood_group: p.blood_group }
      this.editPatModal = true
    },
    async saveEditPatient() {
      await axios.put(`${API}/admin/patient/${this.editPatId}`, this.editPat, { headers: this.headers() })
      this.editPatModal = false
      await this.loadPatients()
    },
    async addDepartment() {
      await axios.post(`${API}/departments`, this.newDept, { headers: this.headers() })
      this.newDept = { name:'', description:'' }
      await this.loadDepartments()
    },
    statusBadge(s) {
      return s === 'Completed' ? 'badge bg-success' : s === 'Cancelled' ? 'badge bg-danger' : 'badge bg-primary'
    }
  }
}
</script>

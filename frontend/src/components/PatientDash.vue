<template>
  <div>
    <h2>Patient Dashboard</h2>
    
    <h3>Book Appointment</h3>
    <select v-model="selectedDoc">
        <option v-for="doc in doctors" :key="doc.id" :value="doc.id">Dr. {{ doc.username }} ({{ doc.spec }})</option>
    </select>
    <input type="date" v-model="date" />
    <input type="time" v-model="time" />
    <button @click="book">Book Now</button>
    <p>{{ msg }}</p>

    <h3>My History</h3>
    <div v-for="appt in appts" :key="appt.id" class="card">
      <b>Dr. {{ appt.doctor }}</b> | {{ appt.date }} @ {{ appt.time }} <span class="badge">{{ appt.status }}</span>
      <div v-if="appt.status === 'Completed'">
        <p>Dx: {{ appt.diagnosis }}</p>
        <p>Rx: {{ appt.prescription }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() { return { doctors: [], appts: [], selectedDoc: null, date: '', time: '', msg: '' } },
  async mounted() {
    const d = await axios.get('http://127.0.0.1:5000/api/doctors');
    this.doctors = d.data;
    this.loadAppts();
  },
  methods: {
    async loadAppts() {
        // In real app, get ID from stored user. For demo, we assume the backend knows or we pass it
        // Note: For simplicity in "One Shot", ensuring Login.vue passed the ID to parent is key. 
        // We will fetch assuming User ID 1 for now if not connected, but let's connect it properly.
        // Actually, let's just ask user to Re-Login if ID missing or handle simple.
        const userId = this.$parent.user ? this.$parent.user.id : 0; 
        if(userId) {
            const a = await axios.get(`http://127.0.0.1:5000/api/patient/appointments/${userId}`);
            this.appts = a.data;
        }
    },
    async book() {
        try {
            const userId = this.$parent.user.id;
            await axios.post('http://127.0.0.1:5000/api/patient/book', {
                user_id: userId, doctor_id: this.selectedDoc, date: this.date, time: this.time
            });
            this.msg = 'Booked!';
            this.loadAppts();
        } catch(e) { this.msg = 'Slot Taken'; }
    }
  }
}
</script>
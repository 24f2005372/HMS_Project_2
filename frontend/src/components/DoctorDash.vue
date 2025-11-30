<template>
  <div>
    <h2>Doctor Dashboard</h2>
    <div v-for="appt in appts" :key="appt.id" class="card">
      <b>Patient: {{ appt.patient }}</b> | {{ appt.date }} @ {{ appt.time }}
      <span class="badge">{{ appt.status }}</span>
      
      <div v-if="appt.status === 'Booked'">
        <input v-model="appt.dx" placeholder="Diagnosis" />
        <input v-model="appt.rx" placeholder="Prescription" />
        <button @click="complete(appt)">Complete</button>
      </div>
      <div v-else>
        <p>Dx: {{ appt.diagnosis }}</p>
        <p>Rx: {{ appt.prescription }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() { return { appts: [] } },
  async mounted() {
    const userId = this.$parent.user ? this.$parent.user.id : 0;
    if(userId) {
        const a = await axios.get(`http://127.0.0.1:5000/api/doctor/appointments/${userId}`);
        this.appts = a.data.map(x => ({...x, dx: '', rx: ''})); // Add temp fields
    }
  },
  methods: {
    async complete(appt) {
        await axios.post(`http://127.0.0.1:5000/api/doctor/complete/${appt.id}`, {
            diagnosis: appt.dx, prescription: appt.rx
        });
        appt.status = 'Completed';
        appt.diagnosis = appt.dx;
        appt.prescription = appt.rx;
    }
  }
}
</script>
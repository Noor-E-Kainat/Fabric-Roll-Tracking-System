<template>
  <v-container>
    <v-btn color="primary" @click="fetchData">
      Load Fabric Rolls
    </v-btn>

<v-table v-if="rolls.length" class="mt-4">
  <thead>
    <tr>
      <th>Select</th>
      <th>Roll ID</th>
      <th>Barcode</th>
      <th>Status</th>
    </tr>
  </thead>

  <tbody>
    <tr v-for="item in rolls" :key="item.id">
      <td>
        <v-checkbox
          v-model="selected"
          :value="item.id"
          hide-details
        />
      </td>

      <td>{{ item.roll_id }}</td>
      <td>{{ item.barcode }}</td>
      <td>{{ item.status }}</td>
    </tr>
  </tbody>
</v-table>

    <v-btn
      v-if="selected.length"
      color="success"
      class="mt-4"
      @click="submitSelected"
    >
      Send to TGMS
    </v-btn>
    <h2 class="mt-6">TGMS Waiting to Receive</h2>

<v-btn color="secondary" class="mt-2" @click="fetchTgmsRolls">
  Load TGMS Waiting Rolls
</v-btn>

<v-table v-if="tgmsRolls.length" class="mt-4">
  <thead>
    <tr>
      <th>Roll ID</th>
      <th>Barcode</th>
      <th>TKMS Status</th>
      <th>TGMS Status</th>
      <th>Sent At</th>
    </tr>
  </thead>

  <tbody>
    <tr v-for="item in tgmsRolls" :key="item.tgms_id">
      <td>{{ item.roll_id }}</td>
      <td>{{ item.barcode }}</td>
      <td>{{ item.tkms_status }}</td>
      <td>{{ item.tgms_status }}</td>
      <td>{{ item.sent_at }}</td>
    </tr>
  </tbody>
</v-table>
  </v-container>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      rolls: [],
      tgmsRolls: [],
      selected: [],
      headers: [
        { title: "Roll ID", key: "roll_id" },
        { title: "Barcode", key: "barcode" },
        { title: "Status", key: "status" }
      ]
    };
  },
  mounted() {
  this.fetchData();
  this.fetchTgmsRolls();
},
  methods: {
    async fetchTgmsRolls() {
  const res = await axios.get("http://127.0.0.1:8000/tgms/waiting-rolls");
  this.tgmsRolls = res.data.data;
},
    async fetchData() {
      const res = await axios.get("http://127.0.0.1:8000/tkms/fabric-rolls");
      this.rolls = res.data.data;
    },

async submitSelected() {
  if (this.selected.length === 0) {
    alert("Please select at least one roll");
    return;
  }

  try {
    const res = await axios.post("http://127.0.0.1:8000/tkms/send-to-tgms", {
      roll_ids: this.selected
    });

    alert(res.data.message);

    this.selected = [];
    await this.fetchData();
    await this.fetchTgmsRolls();

  } catch (err) {
    console.log(err);
    alert("Failed to send rolls to TGMS");
  }
}
  }
};
</script>
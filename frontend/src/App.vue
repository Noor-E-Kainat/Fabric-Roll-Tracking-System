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
  </v-container>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      rolls: [],
      selected: [],
      headers: [
        { title: "Roll ID", key: "roll_id" },
        { title: "Barcode", key: "barcode" },
        { title: "Status", key: "status" }
      ]
    };
  },
  methods: {
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

  } catch (err) {
    console.log(err);
    alert("Failed to send rolls to TGMS");
  }
}
  }
};
</script>
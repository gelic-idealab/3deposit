<template>
  <card class="card" :title="title">
    <div>
      <ul class="list-unstyled team-members">
        <li>
          <div class="row" v-for="member in members" :key="member.name">
            <div class="col-3">
              <div class="avatar">
                <img :src="member.image" alt="Circle Image" class="rounded img-fluid">
              </div>
            </div>
            <div class="col-6">
              {{member.name}}
              <br>
              <span :class="getStatusClass(member.status)">
                <small>{{member.status}}</small>
              </span>
            </div>

            <div class="col-3">
              <p-button type="success" outline icon>
                <i class="fa fa-paper-plane"></i>
              </p-button>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </card>
</template>

<script>
export default {
  data() {
    return {
      title: "Team Westeros",
      members: [
        {
          image: require("@/assets/img/faces/face-0.jpg"),
          name: "Arya",
          status: "Offline"
        },
        {
          image: require("@/assets/img/faces/face-1.jpg"),
          name: "Bran",
          status: "Offline"
        },
        {
          image: require("@/assets/img/faces/face-1.jpg"),
          name: "Khaleesi",
          status: "Dead"
        },
        {
          image: require("@/assets/img/faces/face-1.jpg"),
          name: "Sansa",
          status: "Alive"
        }
      ]
    };
  },
  methods: {
    getStatusClass(status) {
      switch (status) {
        case "Offline":
          return "text-muted";
        case "Alive":
          return "text-success";
        case "Dead":
          return "text-danger";
        default:
          return "text-success";
      }
    }
  }
};
</script>
<style>
</style>

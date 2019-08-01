<template>
  <card class="card" :title="title">
    <div>
      <ul class="list-unstyled team-members">
        <li>
          <div class="row" v-for="user in users" :key="user.id">
            <div class="col-3">
              <div class="avatar">
                <img :src="default_user_img" class="rounded img-fluid">
              </div>
            </div>
            <div class="col-6">
              {{user.username}}
              <br>
              <span :class="getStatusClass(user.role)">
                <small>{{user.role}}</small>
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
import axios from 'axios';

export default {
  data() {
    return {
      title: "Users",
      users: [],
      default_user_img: require("@/assets/img/faces/face-1.jpg")
    };
  },
  methods: {
    getStatusClass(role) {
      switch (role) {
        case "user":
          return "text-muted";
        case "admin":
          return "text-success";
        case "none":
          return "text-danger";
        default:
          return "text-muted";
      }
    }
  },
  mounted() {
    axios.get('../api/users')
    .then(response => {
      this.users = response.data.users;
    },
    error => {
      if (error.response.status === 401) {
        window.location.href = '../api/login';
      }
    });
  }
}

</script>
<style>
</style>

<template>
  <card class="card" :title="title">
    <div>
      <ul class="list-unstyled team-members">
        <li>
          <div class="row" v-for="user in users" :key="user.id">
            <div class="col-1">
              <div class="avatar">
                <img :src="default_user_img" class="rounded img-fluid">
              </div>
            </div>
            <div class="col-1">
              {{user.id}}
            </div>
            <div class="col-2">
              {{user.username}}
              <br>
              <span :class="getStatusClass(user.role)">
                <small>{{user.role}}</small>
              </span>
            </div>
            <div class="col-4">
              {{user.email}}
            </div>  
            <div class="col-2">
              {{user.role}}
            </div>
            <!-- <div v-if="user.role != 'admin'" class="col"> -->
            <div class="col-2">
              <p-button @click.native="editUser(user.username)" type="primary" outline icon>
                <i class="fa fa-edit"></i>
              </p-button>
              <p-button @click.native="deleteUser(user.username)" type="danger" outline icon v-if="user.username != current_user.username">
                <i class="fa fa-trash"></i>
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
    }
  },
  props: {
    current_user: Object
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
    },
    deleteUser(username) {
      axios.delete('../api/users', {data: {username: username}})
      .then(response => {
        console.log(response)
      });
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

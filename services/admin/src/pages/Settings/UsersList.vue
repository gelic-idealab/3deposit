<template>
<div>
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
              <p-button @click.native="editUser(user)" type="primary" outline icon>
                <i class="fa fa-edit"></i>
              </p-button>
              <!-- <p-button @click.native="deleteUser(user.username)" type="danger" outline icon v-if="user.username != current_user.username">
                <i class="fa fa-trash"></i>
              </p-button> -->
            </div>
          </div>
        </li>
      </ul>
    </div>
  </card>

  <div v-if="showEditUserModal">
    <transition name="modal">
    <div class="modal-mask">
    <div class="modal-wrapper">
        <div class="modal-container text-center">

        <div class="modal-header text-center">
            <slot name="header" class="text-center">Edit User: {{userBeingEdited.username}}</slot>
        </div>

        <div class="modal-body">
            <b-form @submit="updateUser">
              <p>User Email</p>
                <b-input class="mb-3" v-model="userBeingEdited.email" required></b-input>
                <p>User Role</p>
                <b-form-select
                    id="userRole"
                    class="mb-3 mr-sm-2"
                    label="User Role"
                    :options="roles"
                    :value="userBeingEdited.role"
                    v-model="userBeingEdited.role"
                ></b-form-select>
                <b-button class="mr-2" type="submit" variant="primary">Save</b-button>
                <b-button v-on:click="toggleModal">Cancel</b-button>
            </b-form>
        </div>

        <div class="modal-footer">
          <p><b>Delete User - Warning!<b></p>
          <b-button variant="danger" v-on:click="deleteUser(userBeingEdited.username)">Delete</b-button>
        </div>
        </div>
    </div>
    </div>
    </transition>
  </div>

</div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      title: "Users",
      users: [],
      default_user_img: require("@/assets/img/faces/face-0.jpg"),
      showEditUserModal: false,
      userBeingEdited: {},
      roles: [
        'admin',
        'user'
      ]
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
    getUsers() {
      axios.get('../api/users')
      .then(response => {
        this.users = response.data.users;
      });
    },
    toggleModal() {
      this.showEditUserModal = !this.showEditUserModal;
    },
    editUser(user) {
      this.userBeingEdited = user;
      this.toggleModal();
    },
    deleteUser(username) {
      this.toggleModal();
      axios.delete('../api/users', {data: {username: username}})
      .then(response => {
        console.log(response)
      })
      .then( () => {
        this.getUsers();
      })
    },
    updateUser() {
      this.toggleModal();
      axios.patch('../api/users', {user: this.userBeingEdited})
      .then(response => {
        console.log(response.data)
      })
      .then( () => {
        this.getUsers();
      })
    }
  },
  mounted() {
    this.getUsers()
  }
}

</script>
<style>
</style>

<template>
  <card class="card" title="Deposit Form">
    <div>
      <form @submit.prevent>
        <div class="row">
          <div class="col-md-6">
            <fg-input type="text"
                      label="Service Name"
                      placeholder="Paper dashboard"
                      v-model="user.name">
            </fg-input>
          </div>
          <div class="col-md-6">
            <fg-input type="text"
                      label="Endpoint URL"
                      placeholder="URL"
                      v-model="user.endpoint">
            </fg-input>
          </div>
        </div>

        <div class="row">
          <div class="col-md-6">
            <fg-input type="text"
                      label="Access Key"
                      placeholder="Access Key"
                      v-model="user.config.auth.access_key">
            </fg-input>
          </div>
          <div class="col-md-6">
            <fg-input type="text"
                      label="Secret Key"
                      placeholder="Secret Key"
                      v-model="user.config.auth.secret_key">
            </fg-input>     
          </div>
        </div>

        <div class="text-center">
          <p-button type="info"
                    round
                    @click.native.prevent="updateProfile">
            Update Profile
          </p-button>
        </div>
        <div class="clearfix"></div>
      </form>
    </div>
  </card>
</template>
<script>
import axios from 'axios'
// import AddServiceFormVue from '../pages/UserProfile/AddServiceForm.vue';

export default {
  // name: AddServiceForm,
  data() {
    return {
      user: {
        name: '',
        endpoint: '',
        config: {
          auth: {
            access_key: "AKIAIOSFODNN7GRAINGER",
            secret_key: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYGRAINGERKEY"
          }
        }
      }
    };
  },
  methods: {
    updateProfile() {
      axios
      .post('http://localhost:8080/services/configs',this.user)
      .then(response => (console.log(response)));
    }
  }
};
</script>
<style>
</style>

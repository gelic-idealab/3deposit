<template>
  <card class="card" title="Deposit Action Form">
    <div>
      <form @submit.prevent>
        <div class="row">
          <div class="col-md-6">
            <fg-input type="text"
                      label="Action Name"
                      placeholder="Paper dashboard"
                      v-model="list.name">
            </fg-input>
          </div>
          <div class="col-md-6">
            <fg-input type="text"
                      label="Media Type"
                      placeholder="Media Type"
                      v-model="list.media_type">
            </fg-input>
          </div>
        </div>

        <div class="row">
          <div class="col-md-12">
            <fg-input type="text"
                      label="Service Name"
                      placeholder="Service Name"
                      v-model="list.service_name">
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
      list: {
        action: '',
        media_type: '',
        service_name:''
      }
    };
  },
  methods: {
    updateProfile() {
      axios
      .post('http://localhost:8080/services/actions',this.list)
      .then(response => (console.log(response)));
    }
  }
};
</script>
<style>
</style>

<template>
  <card class="card" title="Deposit Action Form">
    <div>
      <form @submit.prevent>
        <div class="row">
          <div class="col-md-6">
            <fg-input type="text"
                      label="Action Name"
                      placeholder="Paper dashboard"
                      v-model="action_config.action">
            </fg-input>
          </div>
          <div class="col-md-6">
            <fg-input type="text"
                      label="Media Type"
                      placeholder="Media Type"
                      v-model="action_config.media_type">
            </fg-input>
          </div>
        </div>

        <div class="row">
          <div class="col-md-12">
            <fg-input type="text"
                      label="Service Name"
                      placeholder="Service Name"
                      v-model="action_config.service_name">
            </fg-input>
          </div>
        </div>
        <div class="text-center">
          <p-button type="info"
                    round
                    @click.native.prevent="configureServiceForAction">
            Update Action
          </p-button>
        </div>
        <div class="clearfix"></div>
      </form>
    </div>
  </card>
</template>
<script>
import axios from 'axios'

export default {
  // name: AddServiceForm,
  data() {
    return {
      action_config: {
        action: '',
        media_type: '',
        service_name:''
      }
    };
  },
  methods: {
    configureServiceForAction() {
      axios
      .post('../api/services/actions',this.action_config)
      .then(response => (console.log(response)));
    }
  }
};
</script>
<style>
</style>
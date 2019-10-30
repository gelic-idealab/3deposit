<template>
  <div class="text-center">
    <p-button type="info"
              round
              @click.native.prevent="configureServiceForAction">
      Add Action
    </p-button>
  </div>
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
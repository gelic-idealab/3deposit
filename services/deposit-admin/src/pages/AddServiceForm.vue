<template>
  <card class="card" title="Deposit Service Form">
    <div>
      <form @submit.prevent>
        <div class="row">
          <div class="col-md-6">
            <fg-input type="text"
                      label="Service Name"
                      placeholder="Paper dashboard"
                      v-model="service_config.name">
            </fg-input>
          </div>
          <div class="col-md-6">
            <fg-input type="text"
                      label="Endpoint URL"
                      placeholder="URL"
                      v-model="service_config.endpoint">
            </fg-input>
          </div>
        </div>
<!-- 
        <div v-for="(value,key) in this.service_config.config" :key="key" class="row">
          <div class="col-md-12">
            <fg-input type="text"
                      :label="key"
                      :placeholder="value"
                      v-model="service_config.config[key]">
            </fg-input>
          </div>
        </div> -->

        <textarea class="form-control" rows="5" v-model="config_text"></textarea>

        <!-- <div class="row">
          <div class="col-md-5">
            <fg-input type="text"
                      label="Add New Key"
                      placeholder="Key"
                      v-model="new_key">
            </fg-input>
          </div>
          <div class="col-md-5">
            <fg-input type="text"
                      label="Add New Value"
                      placeholder="Value"
                      v-model="new_value">
            </fg-input>
          </div> -->
        <div>

        </div>

        <div class="text-center">
          <p-button type="info"
                    
                    @click.native.prevent="configureService">
            Configure Service
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
      service_config: {
        name: '',
        endpoint: '',
        config: {
          // auth: ''
        }
      },
      config_text: ''
    };
  },
  methods: {
    configureService() {
      this.parseConfigText();
      axios
      .post('http://localhost:8080/services/configs',this.service_config)
      .then(response => (console.log(response)));
    },
    addConfigKey() {
      this.service_config.config[new_key] = this.new_value;
      this.new_key='';
      this.new_value='';
    },
    parseConfigText() {
      this.service_config.config = JSON.parse(this.config_text);
    }
  }
};
</script>
<style>
</style>
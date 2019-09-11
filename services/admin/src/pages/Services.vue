<template>
  <div>
    <!-- <button type="button" class="btn btn-primary" data-toggle="modal" data-target="#exampleModal">
        Launch demo modal
    </button> -->
    <div class="row">
      <div class="col-12">
        <card :title="tables.services.title" :subTitle="tables.services.subTitle">
          <div slot="raw-content" class="table-responsive">
            <paper-table :data="tables.services.data" :columns="tables.services.columns">

            </paper-table>
          </div>
        </card>
      </div>
    </div>  
    <div class="modal fade" id="exampleModal" tabindex="-1" role="dialog">
      <!-- <div class="modal-dialog" role="document"> -->
        <div class="modal-content">
          <div class="modal-body">
            <add-service-form />
          </div>
          <button type="button" class="close" data-dismiss="modal">
            <span aria-hidden="true">
              &times;              
            </span>
          </button>
        </div>
      <!-- </div> -->
    </div>
    <add-service-form />
  </div>   
</template>
<script>
import { PaperTable } from "@/components";
import AddServiceForm from './AddServiceForm.vue';
import axios from 'axios';

export default {
  components: {
    AddServiceForm,
    PaperTable
  },
  mounted() {
    axios
    .get('../api/services')
    .then(response => {
      (this.tables.services.data = response.data.services);
      (this.tables.services.columns = Object.keys(response.data.services[0]));
    },
    error => {
      if (error.response.status === 401) {
        window.location.href = '../api/login';
      }
    });

  },
  data() {
    return {
      tables: {
        services: {
          title: "Services",
          subTitle: "Currently configured services",
          columns: [],
          data: []
        }
      }
    };
  }
};
</script>
<style>
</style>
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
    <div class="row">
      <div class="col-12">
        <card :title="tables.actions.title" :subTitle="tables.actions.subTitle">
          <div slot="raw-content" class="table-responsive">
            <paper-table :data="tables.actions.data" :columns="tables.actions.columns">

            </paper-table>
          </div>
        </card>
      </div>
    </div>  
    <add-action-form />
  </div>   
</template>
<script>
import { PaperTable } from "@/components";
import AddServiceForm from './AddServiceForm.vue';
import AddActionForm from './AddActionForm.vue';
import axios from 'axios';

export default {
  components: {
    AddServiceForm,
    AddActionForm,
    PaperTable
  },
  mounted() {
    axios
    .get('http://gateway.docker.localhost/services')
    .then(response => (this.tables.services.data = response.data.services))
    .then(() => (this.tables.services.columns = Object.keys(this.tables.services.data[0])));

    axios
    .get('http://gateway.docker.localhost/services/actions')
    // .then(response => console.log(response))
    .then(response => (this.tables.actions.data = response.data.services))
    .then(() => (this.tables.actions.columns = Object.keys(this.tables.actions.data[0])));

    
    // .then(response => (this.table2.data = response.data.actions))
    // .then(() => (this.table1.columns = Object.keys(this.table1.data[0])))
  },
  data() {
    return {
      tables: {
        services: {
          title: "Services",
          subTitle: "Currently configured services",
          columns: [],
          data: []
        },
        actions:{
          title: "Actions",
          subTitle: "Currently configured actions",
          columns: [],
          data: []
        }
      }
      // get table1() {
      //   return this._table1;
      // },
      // set table1(value) {
      //   this._table1=value;
      // },
    };
  }
};
</script>
<style>
</style>
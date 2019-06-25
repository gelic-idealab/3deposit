<template>
  <div>
    <!-- <button type="button" class="btn btn-primary" data-toggle="modal" data-target="#exampleModal">
        Launch demo modal
    </button> -->
    <div class="row">
      <div class="col-12">
        <card :title="table1.title" :subTitle="table1.subTitle">
          <div slot="raw-content" class="table-responsive">
            <paper-table :data="table1.data" :columns="table1.columns">

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
<<<<<<< HEAD
    <add-service-form />
<<<<<<< HEAD
=======
>>>>>>> AddServiceForm Working
=======
    <add-action-form />
>>>>>>> Action form added
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
    .get('http://localhost:8080/services')
    .then(response => (this.table1.data = response.data.services))
    .then(() => (this.table1.columns = Object.keys(this.table1.data[0])))
    // .then(response => (this.table2.data = response.data.actions))
    // .then(() => (this.table1.columns = Object.keys(this.table1.data[0])))
  },
  data() {
    return {
      table1: {
        title: "Services",
        subTitle: "Currently configured services",
        columns: [],
        data: []
      },
      table2:{
        title: "Actions",
        subTitle: "Currently configured actions",
        columns: [],
        data: []
      }
    };
  }
};
</script>
<style>
</style>
<template>
  <div>
    <button type="button" class="btn btn-primary" data-toggle="modal" data-target="#exampleModal">
        Launch demo modal
    </button>
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
    .get('http://localhost:8080/services')
<<<<<<< HEAD
    .then(response => (this.table1.data = response.data.services))
    .then(() => (this.table1.columns = Object.keys(this.table1.data[0])))
=======
    .then(response => (this.table1.data = response.data.services));
>>>>>>> Vue not using reverse-proxy
  },
  data() {
    return {
      table1: {
        title: "Services",
        subTitle: "Currently configured services",
        columns: [],
        data: []
      }
    };
  }
};
</script>
<style>
</style>
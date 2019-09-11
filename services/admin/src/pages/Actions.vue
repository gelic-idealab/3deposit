<template>
  <div>
    <div class="row">
      <div class="col-12">
        <card :title="tables.actions.title" :subTitle="tables.actions.subTitle">
          <div slot="raw-content" class="table-responsive">
            <paper-table :data="tables.actions.data" :columns="tables.actions.columns"></paper-table>
          </div>
        </card>
      </div>
    </div>  
    <add-action-form />
  </div>   
</template>
<script>
import { PaperTable } from "@/components";
import AddActionForm from './AddActionForm.vue';
import axios from 'axios';

export default {
  components: {
    AddActionForm,
    PaperTable
  },
  mounted() {
    axios
    .get('../api/services/actions')
    // .then(response => console.log(response))
    .then(response => {
      this.tables.actions.data = response.data.services
    },
    error => {
      if (error.response.status === 401) {
        window.location.href = '../api/login';
        }
    })
    .then(() => (this.tables.actions.columns = Object.keys(this.tables.actions.data[0])));

  },
  data() {
    return {
      tables: {
        actions:{
          title: "Actions",
          subTitle: "Currently configured actions",
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
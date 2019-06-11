<template>
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
</template>
<script>
import { PaperTable } from "@/components";
import axios from 'axios';

export default {
  components: {
    PaperTable
  },
  mounted() {
    axios
    .get('http://gateway.docker.localhost/services')
    .then(response => (this.table1.data = response.data.services));
  },
  data() {
    return {
      table1: {
        title: "Services",
        subTitle: "Currently configured services",
        columns: ["id", "name", "endpoint", "config"],
        data: []
      }
    };
  }
};
</script>
<style>
</style>

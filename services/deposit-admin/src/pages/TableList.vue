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

      <div class="col-12">
        <card class="card-plain">
          <div class="table-full-width table-responsive">
            <paper-table type="hover" :title="table2.title" :sub-title="table2.subTitle" :data="table2.data"
                         :columns="table2.columns">

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
    axios.get('http://gateway.docker.localhost/services')
                .then(response => (this.table1.data))
  },
  data() {
    return {
      table1: {
        title: "Services",
        subTitle: "Currently configured services",
        columns: ["Id", "Name", "Endpoint", "Config"],
        data: []
      }
    };
  }
};
</script>
<style>
</style>

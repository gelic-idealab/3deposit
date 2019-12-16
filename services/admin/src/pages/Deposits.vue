<template>
  <div>
    <!-- <button type="button" class="btn btn-primary" data-toggle="modal" data-target="#exampleModal">
        Launch demo modal
    </button> -->
    <div class="row">
      <div class="col-12">
        <card :title="tables.deposits.title" :subTitle="tables.deposits.subTitle">
          <div slot="raw-content" class="table-responsive">
            <paper-table :data="tables.deposits.data"
                         :columns="tables.deposits.columns"
                         linkField="deposit_id"
                         pathName="deposit-profile"
            >

            </paper-table>
          </div>
          <div slot="raw-content" class="table-responsive">
            <data-tables :data="this.tables.deposits.data" :pagination-props="{ pageSizes: [5, 10, 15] }" :table-props="tables.deposits.tableProps">
               <el-table-column v-for="title in tables.deposits.columns" :label="title" :key="title">
              </el-table-column>
            </data-tables>-
          </div>
        </card>
      </div>
    </div>
  </div>
</template>
<script>
import { PaperTable } from "@/components";
import { DataTables } from 'vue-data-tables';
import axios from 'axios';

export default {
  components: {
    PaperTable,
    DataTables
  },
  mounted() {
    axios
    .get('../api/deposits')
    .then(response => {
      this.data = response.data;
    },
    error => {
      if (error.response.status === 401) {
        window.location.href = '../api/login';
        }
    })
    //.then(() => (this.tables.deposits.columns = Object.keys(this.data[0])));

  },
  watch: {
    data(data) {
      this.tables.deposits.data = data;
      this.tables.deposits.columns = Object.keys(this.data[0])
    }
  },
  data() {
    return {
      tables: {
        deposits: {
          title: "Deposits",
          subTitle: "All deposits so far",
          columns: [],
          data: [],
          tableProps: {
            border: true,
            stripe: true
        }
        }
      },
      data: []
    };
  }
};
</script>
<style>
</style>

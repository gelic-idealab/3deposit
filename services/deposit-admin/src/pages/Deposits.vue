<template>
  <div>
    <!-- <button type="button" class="btn btn-primary" data-toggle="modal" data-target="#exampleModal">
        Launch demo modal
    </button> -->
    <div class="row">
      <div class="col-12">
        <card :title="tables.deposits.title" :subTitle="tables.deposits.subTitle">
          <div slot="raw-content" class="table-responsive">
            <paper-table :data="tables.deposits.data" :columns="tables.deposits.columns">

            </paper-table>
          </div>
        </card>
      </div>
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
    .get('../api/deposits')
    .then(response => (this.tables.deposits.data = response.data.deposits))
    .then(() => (this.tables.deposits.columns = Object.keys(this.tables.deposits.data[0])));

  },
  data() {
    return {
      tables: {
        deposits: {
          title: "Deposits",
          subTitle: "All deposits so far",
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
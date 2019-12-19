<template>
  <div>
    <card :title="title" :subTitle="subTitle">
      <div slot="raw-content" class="table-responsive">
        <el-table :data="data">

            <el-table-column width="40">
              <template slot-scope="scope">
                <el-tooltip content="Info"
                            :open-delay="300"
                            placement="top">
                  <p-button type="info" size="sm" class="mr-2" icon v-on:click.native="openDepositProfile(scope.row.deposit_id)">
                    <i class="ti-info"></i>
                  </p-button>
                </el-tooltip>
              </template>
            </el-table-column>

            <el-table-column
              sortable
              prop="deposit_id"
              label="ID">
            </el-table-column>
            <el-table-column
              sortable
              prop="deposit_date"
              label="Date">
            </el-table-column>
            <el-table-column
              sortable
              prop="media_type"
              label="Type">
            </el-table-column>

        </el-table>
      </div>
    </card>
  </div>
</template>
<script>
import {Table, TableColumn} from 'element-ui';
import axios from 'axios';

export default {
  components: {
    [Table.name]: Table,
    [TableColumn.name]: TableColumn
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

  },
  watch: {
    data(data) {
      this.columns = Object.keys(this.data[0])
    }
  },
  data() {
    return {
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
  methods: {
    openDepositProfile(id) {
      this.$router.push({ name: 'deposit-profile', params: { id: id }})
    }
  }
};
</script>
<style>
</style>

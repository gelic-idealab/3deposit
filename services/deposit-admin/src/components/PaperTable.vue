<template>
  <table class="table" :class="tableClass">
    <thead>
    <slot name="columns">
      <th v-for="column in columns" :key="column">{{column}}</th>
    </slot>
    </thead>
    <tbody>
    <tr v-for="(item, index) in data" :key="index">
      <slot :row="item">
        <td v-for="(column, index) in columns"
            :key="index"
            v-if="hasValue(item, column)">
            <router-link v-if="isLink(column)" :to="{ name: 'deposit-profile', params: { id: itemValue(item,column) }}"> {{ itemValue(item,column) }}
            </router-link>
            <a v-else>
              {{itemValue(item, column)}}
            </a>
        </td>
      </slot>
    </tr>
    </tbody>
  </table>
</template>
<script>
export default {
  name: 'paper-table',
  props: {
    columns: Array,
    data: Array,
    type: {
      type: String, // striped | hover
      default: "striped"
    },
    title: {
      type: String,
      default: ""
    },
    subTitle: {
      type: String,
      default: ""
    }
  },
  computed: {
    tableClass() {
      return `table-${this.type}`;
    }
  },
  methods: {
    hasValue(item, column) {
      return item[column.toLowerCase()] !== "undefined";
    },
    itemValue(item, column) {
      return item[column.toLowerCase()];
    },
    isLink(column) {
      if(column == 'id') {
        return true
      }
    },
    // makeHref(itemValue) {
    //   // console.log(this.$router.push({ name:"deposits", params:{ 'id': itemValue.toString() } }))
    //   return "http://localhost:8081/deposits/"+itemValue.toString()
    // }
  }
};
</script>
<style>
</style>
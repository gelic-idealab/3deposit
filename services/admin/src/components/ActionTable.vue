<template>
  <table class="table" :class="tableClass">
    <thead>
        <slot name="columns">
            <th v-for="column in columns" :key="column">{{column}}</th>
        </slot>
    </thead>
    <tbody>
    <tr v-for="(item, item_index) in data" :key="item_index">
      <slot :row="item">
        <td v-for="(column, col_index) in columns" :key="col_index">
          <select v-if="columnName(column) == 'action'" v-model="data[item_index].action">
            <option>publish</option>
            <option>store</option>
          </select>

          <select v-else-if="columnName(column) == 'media_type'" v-model="data[item_index].media_type">
            <option>default</option>
            <option>model</option>
            <option>video</option>
            <option>vr</option>
          </select>

          <select v-else-if="columnName(column) == 'service_name' && data[item_index].action == 'publish' && data[item_index].media_type == 'video'" v-model="data[item_index].service_name">
            <option>vimeo</option>
            <option>youtube</option>
          </select>

          <select v-else-if="columnName(column) == 'service_name' && data[item_index].action == 'publish' && data[item_index].media_type == 'vr'" v-model="data[item_index].service_name">
            <option>aws</option>
            <option>surge</option>
          </select>
          
          <select v-else-if="columnName(column) == 'service_name' && data[item_index].action == 'store' && data[item_index].media_type == 'default'" v-model="data[item_index].service_name">
            <option>minio</option>
          </select>

          <select v-else-if="columnName(column) == 'service_name' && data[item_index].action == 'publish' && data[item_index].media_type == 'model'" v-model="data[item_index].service_name">
            <option>sketchfab</option>
          </select>

          <p v-else>
            Invalid Combination
          </p>
        </td>
      </slot>
    </tr>
    </tbody>
  </table>
</template>

<script>
export default {
  name: 'action-table',
  props: {
      columns: Array,
      data: Array
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
  columnName(column) {
      return column.toLowerCase();
      },
  isLink(column) {
      if(column == this.linkField)
          return true
      }
  }
}
</script>
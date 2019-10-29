<template>
  <table class="table table-striped">
    <thead>
        <slot name="columns">
            <th v-for="column in columns" :key="column">{{column}}</th>
        </slot>
    </thead>
    <tbody>
    <tr v-for="(item, item_index) in actionConfig" :key="item_index">
      <slot :row="item">
        <td v-for="(column, col_index) in columns" :key="col_index">
          <select v-if="columnName(column) == 'action'" v-model="actionConfig[item_index].action">
            <option>publish</option>
            <option>store</option>
          </select>

          <select v-else-if="columnName(column) == 'media_type'" v-model="actionConfig[item_index].media_type">
            <option>default</option>
            <option>model</option>
            <option>video</option>
            <option>vr</option>
          </select>

          <select v-else-if="columnName(column) == 'service_name' && actionConfig[item_index].action == 'publish' && actionConfig[item_index].media_type == 'video'" v-model="actionConfig[item_index].service_name">
            <option>vimeo</option>
            <option>youtube</option>
          </select>

          <select v-else-if="columnName(column) == 'service_name' && actionConfig[item_index].action == 'publish' && actionConfig[item_index].media_type == 'vr'" v-model="actionConfig[item_index].service_name">
            <option>aws</option>
            <option>surge</option>
          </select>
          
          <select v-else-if="columnName(column) == 'service_name' && actionConfig[item_index].action == 'store' && actionConfig[item_index].media_type == 'default'" v-model="actionConfig[item_index].service_name">
            <option>minio</option>
          </select>

          <select v-else-if="columnName(column) == 'service_name' && actionConfig[item_index].action == 'publish' && actionConfig[item_index].media_type == 'model'" v-model="actionConfig[item_index].service_name">
            <option>sketchfab</option>
          </select>

          <p v-else-if="columnName(column) == 'service_name'">
            Invalid Combination
          </p>
          <p v-else>
            {{itemValue(item, column)}}
          </p>
        </td>
        <td>
          <p-button type="info"
                    round
                    @click.native.prevent="configureServiceForAction(item_index)" icon>
                <i class="fa fa-refresh"></i>
          </p-button>
        </td>
        <td>
          <p-button type="danger"
                    round
                    @click.native.prevent="deleteAction(item_index)" icon>
                <i class="fa fa-trash"></i>
          </p-button>
        </td>
      </slot>
    </tr>
    </tbody>
  </table>
</template>

<script>
import axios from 'axios';

export default {
  name: 'action-table',
  props: {
      columns: Array,
      actionConfig: Array
  },
  methods: {
    hasValue(item, column) {
      return item[column.toLowerCase()] !== "undefined"
    },
    itemValue(item, column) {
      return item[column.toLowerCase()]
    },
    columnName(column) {
      return column.toLowerCase()
    },
    isLink(column) {
      if(column == this.linkField)
          return true
    },
     deleteAction(index) {
      axios.delete(
        "../api/services/actions", this.actionConfig[index]
        );
    },
    configureServiceForAction(index) {
      axios
      .post('../api/services/actions', this.actionConfig[index])
      .then(response => (console.log(response)));
    },
  }
}
</script>
<template>
  <div class="fields">
    <div class="container">
    <div class="form-group">
      <div class="input-group mb-3" v-for="(field, index) in fields" :key="field.id">
        <template v-if="renderField(field)">

        <template v-if="field.type === 'text'">
          <h4>{{ field.label }}</h4>
          <button v-if="field.repeatable === true" type="button" class="btn btn-info btn-sm ml-3 mb-3" v-on:click="addValue(field.value)">Add</button>
            <div class="input-group mb-3" v-for="(value, index) in field.value" :key="index">
              <input :type="field.type" class="form-control"
              v-model="field.value[index]" 
              >
                <div class="input-group-append" v-if="index > 0">
                    <button type="button" class="btn btn-danger btn-sm" 
                    v-on:click="removeValue(field.value, index)">Remove</button>
                </div>
            </div>
        </template>

        <template v-else-if="field.type === 'select'">
          <h4>{{ field.label }}</h4>
              <select class="form-control ml-3 mb-3"
              v-model="field.value" 
              >
                <option v-for="option in field.options" :key="option.value">
                {{ option.label }} 
                </option> 
              </select>
        </template>

        <template v-else-if="field.type === 'checkbox'">
          <h4>{{ field.label }}</h4>
            <input class="ml-3" type="checkbox" v-on:change.native="toggleCheckbox(field, index)" v-model="field.value">
        </template>

      </template>
      </div>
    </div>
    </div>
  </div>
</template>


<script>
export default {
  name: 'Fields',
  props: {
    fields: Array
  },
  methods: {
    addValue: function (valueList) {
      valueList.push('')
    },
    removeValue: function (valueList, index) {
      valueList.splice(index, 1)
    },
    toggleCheckbox: function (field, index) {
      field[index].value = !field[index].value
    },
    getParent: function (field) {
      var parent = this.fields.filter(function (el) {
        return el.id === field.dependsOn.id
      })
      return parent[0]
    },
    renderField: function (field) {
      if (Object.keys(field.dependsOn).length === 0) {
        return true
      } else {
        var pf = this.getParent(field)
        if (field.dependsOn.value === pf.value) {
          return true
        } else {
          return false
        }
      }
    }
  },
}
</script>

<style>
</style>
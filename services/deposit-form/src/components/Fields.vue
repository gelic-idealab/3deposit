<template>
  <div class="fields">
    <div class="form-group">
      <div class="input-group mb-3" v-for="(field, index) in fields" :key="field.id">
        <template v-if="field.type === 'text'">
          <h4>{{ field.label }}</h4>
          <button v-if="field.repeatable === true" type="button" class="btn btn-info btn-sm ml-3 mb-3" v-on:click="addValue(field.value)">Add</button>
            <div class="input-group mb-3" v-for="(value, index) in field.value" :key="index">
              <input :type="field.type" class="form-control"
              v-model="field.value[index]" 
              >
                <div class="input-group-append" v-if="index > 0">
                    <button type="button" class="btn btn-danger btn-sm" 
                    v-on:click="removeValue(field.value, index)">Delete</button>
                </div>
            </div>
        </template>
        <template v-else-if="field.type === 'select'">
          <h4>{{ field.label }}</h4>
              <select class="form-control ml-3 mb-3"
              v-model="field.value[index]" 
              >
                <option v-for="option in field.options" :key="option.value">
                {{ option.label }} 
                </option> 
              </select>
        </template>
      </div>
    </div>
  </div>
</template>



<!--         </div>

        <button type="button" class="btn btn-info btn-sm" v-on:click="addCreator(fields.creatorName.creators)">Add Creators</button>
        <p>
            <h4>{{ fields.objectType.label }}</h4>
                <select class="custom-select" v-model="fields.objectType.value">
      <option disabled value="">Please select one</option>
      <option v-for="choice in fields.objectType.choices">{{ choice }}</option>
    </select>
    </p>

    <p>
    <h4 v-if="fields.objectType.value == '3d model'">{{ fields.modelFileType.label }}</h4>
    <select class="custom-select" v-if="fields.objectType.value == '3d model'" v-model ="fields.modelFileType.value">
      <option disabled value="">Select file type</option>v-container>
      <option v-for="choice in fields.modelFileType.choices">{{ choice }}</option>    
    </select>
    </p> -->



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
    }
  }
}
</script>

<style>
</style>
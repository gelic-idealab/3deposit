<template>
    <div class="fields">
        <div class="form-group">
            <h4>{{ fields.creatorName.label }}</h4>
                <div class="input-group mb-3" v-for="(creator, index) in fields.creatorName.creators">
                    <input type="text" class="form-control"
                    v-model="fields.creatorName.creators[index]" 
                    placeholder="Creator Name">
                        <div class="input-group-append" v-if="index > 0">
                            <button type="button" class="btn btn-danger btn-sm" 
                            v-on:click="removeCreator(fields.creatorName.creators, index)">Remove Creators</button>
                        </div>
                </div>
        </div>

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
    </p>

  </div>
</template>

<script>
export default {
  name: 'Fields',
  props: {
    fields: Object
  },
  methods: {
    addCreator: function (creatorList) {
      creatorList.push('')
    },
    removeCreator: function (creatorList, index) {
      creatorList.splice(index, 1)
    }
  }
}
</script>

<style>
</style>
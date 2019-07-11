<template>
  <div class="fields">
    <div class="container">
    <div class="form-group">
      
      <div class="input-group mb-3" v-for="field in fields" :key="field.id">
        <template v-if="renderField(field)">



        <template v-if="field.type === 'text'">
          <div class="col-12">
          <div>
          <h4>{{ field.label }}</h4>
          <button v-if="field.repeatable === true" type="button" class="btn btn-info ml-3 mb-3" v-on:click="addValue(field.value)">Add</button>
          </div>
          </div>
          <div class="col-12">
          <div>
            <transition-group name="fade" tag="ul">
              <div class="input-group mb-3" v-for="(value, index) in field.value" :key="index">
                  <input :type="field.type" class="form-control input-lg"
                  v-model="field.value[index]" 
                  >
                  <div class="input-group-append" v-if="index > 0">
                      <button type="button" class="btn btn-danger btn-lg" 
                      v-on:click="removeValue(field.value, index)">Remove</button>
                  </div>
              </div>
              </transition-group>
            </div>
          </div>
        </template>

        <template v-else-if="field.type === 'date'">
          <h4>{{field.label}}</h4>
          <input class="form-control ml-3 mb-3" type="date" v-model="field.value" value="">
        </template>

        <template v-else-if="field.type === 'select'">
          <h4>{{ field.label }}</h4>
              <select class="form-control ml-3 mb-3 input-lg"
              v-model="field.value" 
              >
                <option v-for="option in field.options" :value="option.value" :key="option.value">
                {{ option.label }} 
                </option> 
              </select>
        </template>

        
        <template v-else-if="field.type === 'container'">
          <div class="input-group mb-3 input-lg" v-for="(subfield, index) in field.subfields" :key="subfield.index">
            <h4>{{ field.label }}</h4>
              <input class="ml-3" type="checkbox" v-on:change.native="toggleCheckbox(field, index)" v-model="field.value">
          </div>
        </template>

      </template>
      </div>
      <button type="button" class="btn btn-primary btn-lg btn-block" v-on:click="submitDeposit">Submit</button>
    </div>
    </div>
  </div>
</template>


<script>
import axios from 'axios';


export default {
  name: 'Fields',
  props: {
    fields: Array,
    id: String
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
      let parent = this.fields.filter(function (el) {
        return el.id === field.dependsOn.id
      })
      return parent[0]
    },
    renderField: function (field) {
      if (Object.keys(field.dependsOn).length === 0) {
        return true
      } else {
        let pf = this.getParent(field)
        if (field.dependsOn.value === pf.value) {
          return true
        } else {
          return false
        }
      }
    }
  }
}

</script>

<style>
.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
</style>
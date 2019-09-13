<template>
  <div class="fields">
    <div class="container">
    <div class="form-group">

        <p v-if="errors.length">
          <ul>
            <div class="alert alert-danger" v-for="(error,index) in errors" :key="index">{{ error }}</div>
          </ul>
        </p>
      
      <div class="input-group mb-3" v-for="field in fields" :key="field.id">
        <template v-if="renderField(field)">

            <template v-if="field.type === 'text'">
              <div class="col">
                <div>
                  <h4>{{ field.label }}</h4>
                  <button v-if="field.repeatable == true" type="button" class="btn btn ml-3 mb-3" v-on:click="addValue(field.value)">Add</button>
                </div>
              </div>
              <div class="col">
                <div>
                  <transition-group name="fade" tag="ul">
                    <div class="input-group mb-3" v-for="(value, index) in field.value" :key="index">
                        <input :type="field.type" class="form-control input-lg" :class="fieldInvalid(field.id)"
                        v-model="field.value[index]" 
                        >
                        <div class="input-group-append" v-if="index > 0">
                            <button type="button" class="btn btn-danger" 
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
                  :class="fieldInvalid(field.id)"
                  >
                    <option v-for="option in field.options" :value="option.value" :key="option.value">
                    {{ option.label }} 
                    </option> 
                  </select>
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
  data() {
    return {
      errors: []
    }
  },
  methods: {
    formErrors() {
      console.log("formErrors called")
      let formErrors = []
      this.fields.forEach(f => {
        if (f.required && (f.value.length == 0 || f.value[0] == "")) {
          formErrors.push(f.id);
          console.log(f.label, f.value);
        }
      })
      return formErrors;
    },
    fieldInvalid(id) {
      if (this.errors.includes(id)) {
        return "is-invalid";
      }
    },
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
    },
    submitDeposit: function () {
      this.errors = this.formErrors();
      if (this.errors) {
        console.log(this.errors)
      }
      else {
        axios({
          url: '../api/form/submit',
          data: {
            'media_type': this.fields[0].value,
            'form': this.fields, 
            'id': this.id
            },
          method: 'post',
          config: { headers: {'Content-Type': 'application/json' }}
          })
        .then(function(response) {
          if (response.status === 200) {
            window.location.href = "/";
          } else {
            (console.log(response));
          }
        });
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
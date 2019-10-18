<template>
  <b-form-group>
    <div class="input-group mb-3" v-for="field in fields" :key="field.id">
      <template v-if="renderField(field)">

          <template v-if="field.type === 'text' && field.repeatable === true">
              <div>
                <h4>{{ field.label }}</h4>
                <button v-if="field.repeatable === true" type="button" class="btn btn-primary" v-on:click="addValue(field.value)">Add {{field.label}}</button>
              </div>
              <transition-group name="fade" tag="ul">
                <b-input-group v-for="(value, index) in field.value" :key="index">
                  <b-form-input class="ml-3"
                    :class="fieldInvalid(field.id)"
                    v-model="field.value[index]" 
                    v-on:input="clearError(field.id)">
                  </b-form-input>
                  <b-input-group-append v-if="index > 0">
                    <b-button variant="danger" v-on:click="removeValue(field.value, index)">Remove</b-button>
                  </b-input-group-append>
                </b-input-group>
              </transition-group>
          </template>

          <template v-if="field.type === 'text' && field.repeatable === false">
              <div>
                <h4>{{ field.label }}</h4>
              </div>
              <b-form-input class="ml-3"
                :class="fieldInvalid(field.id)"
                v-model="field.value" 
                v-on:input="clearError(field.id)">
              </b-form-input>
          </template>

          <template v-else-if="field.type === 'date'">
            <h4>{{field.label}}</h4>
            <b-form-input class="form-control ml-3" type="date" v-model="field.value" v-on:input="clearError(field.id)" :class="fieldInvalid(field.id)">
          </template>

          <template v-else-if="field.type === 'select'">
            <h4>{{ field.label }}</h4>
                <b-form-select class="form-control ml-3 input-lg"
                v-model="field.value"
                :multiple="field.repeatable"
                :options="field.options"
                :class="fieldInvalid(field.id)"
                v-on:input="clearError(field.id)"
                ></b-form-select>
          </template>

      </template>
    </div>

    <b-button block size="lg" variant="primary" v-on:click="submitDeposit">Submit Deposit</b-button>

  </b-form-group>
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
    clearError(id) {
      var i = this.errors.indexOf(id)
      if (i > -1) {
        this.errors.splice(i, 1)
      }
    },
    formErrors() {
      let formErrors = []
      this.fields.forEach(f => {
        if (f.required && this.renderField(f) && (f.value.length == 0 || f.value[0] == "")) {
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
      console.log(this.$parent.finished_uploading)
      if (this.errors.length == 0 && this.$parent.finished_uploading) {
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
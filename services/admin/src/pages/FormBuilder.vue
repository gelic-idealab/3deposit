<template>
    <div>
        <b-form inline>
            <b-input-group prepend="Form ID" class="mb-2">
                <b-form-select
                    id="inline-form-input-name"
                    class="mb-2 mr-sm-2 mb-sm-0"
                    label="Form ID"
                    :options="forms"
                    v-model="deposit_form.id"
                    v-on:change="getForm"
                ></b-form-select>
            </b-input-group>
        </b-form>

        <b-alert v-model="unsaved" variant="warning">
            <span>Form <b>{{deposit_form.form_id}}</b> has unsaved changes</span>
        </b-alert>

        <vue-json-editor v-model="deposit_form.content" :show-btns="true" @json-save="saveForm" @input="formChanged"></vue-json-editor>

    </div>
</template>

<script>
import axios from 'axios';
import vueJsonEditor from 'vue-json-editor'

export default {
    data() {
        return {
            forms: [],
            deposit_form: {
                id: null,
                content: {}
            },
            unsaved: false
        }
    },
    components: {
        vueJsonEditor
    },
    mounted() {
        this.getForms();
        this.getForm();
    },
    methods: {
        getForms() {
            axios.get('../api/form')
            .then(response => {
                if (response.data.forms) {
                    console.log(response.data.forms);
                    this.forms = response.data.forms
                }
            });
        },
        getForm() {
            axios.get('../api/form', {params: {form_id: this.deposit_form.id || 'default'}})
            .then(response => {
                if (response.data.form) {
                    this.deposit_form = response.data.form;
                    console.log(response.data.form.id, 'loaded')
                }
            })
        },
        saveForm() {
            axios.post('../api/form', this.deposit_form)
            .then(response => {
                if (response.status == 200) {
                    console.log(response);
                    this.unsaved = false;
                    this.$notify({
                        message: 'Form saved',
                        horizontalAlign: 'right',
                        verticalAlign: 'top',
                        type: 'success',
                        closeOnClick: true
                    });
                }            
            })
        },
        formChanged() {
            this.unsaved = true;
        }
    }
};
</script>
<style>
</style>
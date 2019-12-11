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
            <b-button size="sm" class="mb-2" v-on:click="toggleShowModal">Create New</b-button>
        </b-form>

        <b-alert v-model="unsaved" variant="warning">
            <span>Form <b>{{deposit_form.form_id}}</b> has unsaved changes</span>
        </b-alert>

        <vue-json-editor v-model="deposit_form.content" :show-btns="true" @json-save="saveForm" @input="formChanged"></vue-json-editor>

        <div v-if="showCreateModal">
            <transition name="modal">
            <div class="modal-mask">
            <div class="modal-wrapper">
                <div class="modal-container text-center">

                <div class="modal-header text-center">
                    <slot name="header" class="text-center">Create New Form</slot>
                </div>

                <div class="modal-body">
                    <b-form @submit="createNew">
                        <b-input class="mb-3" v-model="new_form.id" required></b-input>
                        <p>Create from template</p>
                        <b-form-select
                            id="templateId"
                            class="mb-3 mr-sm-2"
                            label="Form Template"
                            :options="forms"
                            v-model="new_form.template_id"
                        ></b-form-select>
                        <b-button class="mr-2" type="submit" variant="primary">Create</b-button>
                        <b-button v-on:click="toggleShowModal">Cancel</b-button>
                    </b-form>
                </div>

                <div class="modal-footer">
                    
                </div>
                </div>
            </div>
            </div>
            </transition>
        </div>

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
            new_form: {
                id: null,
                content: null,
                template_id: 'default'
            },
            unsaved: false,
            showCreateModal: false
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
            axios.get('../api/form', {params: {id: this.deposit_form.id || 'default'}})
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
                    console.log(response.data);
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
        },
        toggleShowModal() {
            this.showCreateModal = !this.showCreateModal;
        },
        resetNewForm() {
            this.new_form.id = null;
            this.new_form.content = {};
            this.new_form.template_id = null;
        },
        createNew() {
            this.toggleShowModal();
            axios.get('../api/form', {params: {id: this.new_form.template_id || 'default'}})
            .then(response => {
                if (response.data.form) {
                    this.new_form.content = response.data.form.content;
                    console.log('creating template from', response.data.form.id)
                } else {

                }
            })
            .then( () => {
                axios.post('../api/form', this.new_form)
                .then(response => {
                    if (response.status == 200) {
                        this.$notify({
                            message: 'New form created',
                            horizontalAlign: 'right',
                            verticalAlign: 'top',
                            type: 'success',
                            closeOnClick: true
                        });
                    }  
                })
                .then( () => {
                    this.getForms();
                })
                .then( () => {
                    this.deposit_form.id = this.new_form.id;
                    this.deposit_form.content = this.new_form.content
                    this.resetNewForm();
                })
            })          
        }
    }
};
</script>
<style>
  .ace-jsoneditor, textarea.jsoneditor-text {
    min-height: 350px;
  }
  .ace_line_group {
    text-align: left;
  }
  .json-editor-container {
    display: flex;
    width: 100%;
  }
  .json-editor-container .tree-mode {
    width: 75%;
  }
  .json-editor-container .code-mode {
    flex-grow: 1;
  }
  .jsoneditor-btns{
    text-align: center;
    margin-top:10px;
  }
  .jsoneditor-vue .jsoneditor-outer{
    min-height:350px;
  }
  .jsoneditor-vue div.jsoneditor-tree{
    min-height: 350px;
  }
  .json-save-btn{
    background-color: #66615b;
    border: none;
    color:#fff;
    padding:5px 10px;
    border-radius: 5px;
  }
  .json-save-btn:focus{
    outline: none;
  }
  .json-save-btn[disabled]{
    background-color: #66615b;
  }
  code {
    background-color: #f5f5f5;
  }
</style>
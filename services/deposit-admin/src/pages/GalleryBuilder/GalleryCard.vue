<template>
    <div>
      <!-- <h5>Placeholder</h5> -->
        <div class="card">
            <vue-json-pretty :data="localDep">
            </vue-json-pretty>
        </div>
  </div>
</template>
<script>

import VueJsonPretty from 'vue-json-pretty'

export default {
    data() {
        return {
            localDep: {}
        }
    },
    props: {
        deposit: Object
    },
    created() {
        this.localDep = this.deposit;
    }
}
</script>
<style>
</style>

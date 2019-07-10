<template>
      <div v-html="rendered">
      </div>
</template>
<script>
import VueJsonPretty from 'vue-json-pretty'

export default {
    name: 'metadata-json',
    props: {
        publish_metadata: Object
    },
    data() {
        return {
            rendered: {}
        }
    },
    mounted() {
        const formatter=new JSONFormatter(this.publish_metadata)
        this.rendered = formatter.render()
    }
}



</script>
<style>
</style>

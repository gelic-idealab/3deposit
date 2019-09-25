<template>
    <div>
        <Logs :service="service"/>
    </div>    
</template>

<script>
import Logs from "../components/Logs.vue";

export default {
    components: {
        Logs
    },
    data () {
        return {
            service: ""
        }
    },
    created () {
        this.service = this.$route.params.id;
    }
}
</script>
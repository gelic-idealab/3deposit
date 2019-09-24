<template>
    <div>
        {{logs}}
    </div>
</template>

<script>
import axios from 'axios';

export default {
    props: {
        service: String
    },
    data () {
        return {
            logs: ""
        }
    },
    mounted () {
        axios.get('../api/logs', {params: {'service': this.service}})
        .then(response => {
            this.logs = response.data.log
        })
    }
}
</script>
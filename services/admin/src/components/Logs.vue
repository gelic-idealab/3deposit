<template>
    <div>
        <h3>Service Logs<h3>
        <card style="background-color:black">
            <code v-for="(l, index) in logs" :key="index">
                <span style="color:lime">{{ index+1 }}</span>&emsp;{{ l }}
                <br />
            </code>
        </card>    
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
            logs: []
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
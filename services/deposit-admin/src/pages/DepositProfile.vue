<template>
    <div class="row">
    <div class="card mb-3">
        <div class="embed-responsive embed-responsive-16by9">
            <embed-card :location="deposit.location" class="embed-responsive-item"></embed-card>
        </div>
        <div class="card-body">
            <h5 class="card-title">{{ deposit.deposit_id }}</h5>
            <p class="card-text">{{ deposit_metadata }}</p>
            <p class="card-text">{{ publish_metadata }}</p>
            <p class="card-text"><small class="text-muted">{{ deposit.deposit_date }}</small></p>
        </div>
      </div>
    </div>
</template>

<script>
import axios from 'axios';
import EmbedCard from "./DepositProfile/EmbedCard.vue";
export default {
    data() {
        return{
            deposit: {},
            deposit_metadata: {},
            publish_metadata: {},
            id: ''
        }
    },
    components: {
        EmbedCard
    },
    mounted() {
        this.id = this.$route.params.id;
        console.log(this.id);
        axios.get("http://localhost:8080/metadata", {params: {deposit_id: this.id}})
        .then(response => (this.deposit_metadata = response.data.deposit_metadata));

        axios.get("http://localhost:8080/deposits", {params: {id: this.id}})
        .then(response => (this.deposit = response.data))
        .then(response => {
            axios.get("http://localhost:8080/publish/models", {params: {resource_id: this.deposit.resource_id}})
            .then(response => (this.publish_metadata = response.data))
        })     
        .then(console.log(this.deposit.resource_id))

    }
};
</script>
<style>
</style>
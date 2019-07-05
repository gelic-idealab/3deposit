<template>
    <div class="row">
    <div class="card mb-3">
        <div class="embed-responsive embed-responsive-16by9">
            <embed-card :location="deposit.location" class="embed-responsive-item"></embed-card>
        </div>
        <div class="card-body">
            <h5 class="card-title">{{ deposit.deposit_id }}</h5>
            <p class="card-text">This is a wider card with supporting text below as a natural lead-in to additional content. This content is a little bit longer.</p>
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
            id: ''
        }
    },
    components: {
        EmbedCard
    },
    mounted() {
        this.id = this.$route.params.id;
        console.log(this.id)
        axios.get("http://localhost:8080/deposits", {params: {id: this.id}})
        .then(response => (this.deposit = response.data));
    }
};
</script>
<style>
</style>

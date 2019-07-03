<template>
    <div class="row">
      <div class="col-xl-4 col-lg-5 col-md-6">
          <embed-card :location="deposit.location">
          
          </embed-card>
      </div>
    </div>
</template>
<script>
// import EditProfileForm from "./UserProfile/EditProfileForm.vue";
import axios from 'axios'
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
        this.id = $route.params.id;
        console.log(this.id)
        axios.get("http://localhost:8080/deposits/".concat(this.id))
        .then(response => (this.deposit = response.data));
    }
};
</script>
<style>
</style>

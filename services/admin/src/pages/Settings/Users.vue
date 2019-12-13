<template>
    <div>
        <span>
            <p>Active signup token: <a :href="signupUrl">{{signupToken}}</a></p>
        </span>
        <users-list :current_user="current_user"></users-list>
    </div>
</template>

<script>
import axios from 'axios';
import UsersList from "./UsersList.vue";

export default {
    components: {
        UsersList
    },
    props: {
        current_user: Object
    },
    data () {
        return {
            signupToken: '',
            signupUrl: ''
        }
    },
    mounted () {
        this.getSignupToken();
    },
    methods: {
        getSignupToken() {
            axios.get('../api/tokens', {params: {type: 'signup'}})
            .then(response => {
                if (response.status === 200) {
                    this.signupToken = response.data.token
                    this.signupUrl = '../api/signup?token=' + response.data.token
                }
            })
        }
    }
    
}
</script>
<style>

</style>

<template>
    <div>
        <users-list></users-list>
        <card>
            <h5 class="card-title">Create User</h5>
            <iframe src='../api/signup' width="100%" height="400"></iframe>
        </card>
    </div>
</template>

<script>
import UsersList from "./UsersList.vue";

export default {
    components: {
        UsersList
    }
    
}
</script>
<style>

</style>

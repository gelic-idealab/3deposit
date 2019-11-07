<template>
    <div>
        <users-list :current_user="current_user"></users-list>
    </div>
</template>

<script>
import UsersList from "./UsersList.vue";

export default {
    components: {
        UsersList
    },
    props: {
        current_user: Object
    }
    
}
</script>
<style>

</style>

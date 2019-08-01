<template>
    <div>
        <services v-if="current_user.role === 'admin'"></services>
        <users></users>
    </div>
</template>

<script>
import Services from "@/pages/Services.vue";
import Users from "./Settings/Users.vue";

export default {
    components: {
        Services,
        Users
    },
    props: {
        current_user: Object
    }
    
}
</script>
<style>

</style>

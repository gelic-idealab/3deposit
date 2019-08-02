<template>
    <div>
        <services v-if="current_user.role === 'admin'"></services>
    </div>
</template>

<script>
import Services from "@/pages/Services.vue";

export default {
    components: {
        Services
    },
    props: {
        current_user: Object
    }
    
}
</script>
<style>

</style>

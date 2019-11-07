<template>
    <div>
        {{ current_user.role }}
    </div>
</template>

<script>

export default {
    components: {
    },
    props: {
        current_user: Object
    }
    
}
</script>
<style>

</style>

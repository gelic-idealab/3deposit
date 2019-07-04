<template>
  <div>
      <embed :src="location">
  </div>
</template>
<script>
export default {
    props: {
        location: String
    }
}
</script>
<style>
</style>

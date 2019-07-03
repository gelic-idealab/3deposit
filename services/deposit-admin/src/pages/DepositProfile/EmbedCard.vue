<template>
  <container-fluid>
      <embed :src="location">
  </container-fluid>
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

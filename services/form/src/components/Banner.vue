<template>
  <div class="banner">
    <div class="jumbotron">
      <h1 class="display-4">{{ banner.title }}</h1>
        <p class="lead"> {{ banner.description }}</p>
        <hr class="my-4">
        <p>{{ banner.instructions }}</p>
        <p class="lead">
          <a class="btn btn-primary btn-lg" href="#" role="button">Learn more</a>
        </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Banner',
  props: {
    banner: Object
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>

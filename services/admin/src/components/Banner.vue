<template>
  <b-jumbotron id="bj">
    <h1 class="display-4">{{ banner.title }}</h1>
      <p class="lead"> {{ banner.description }}</p>
      <hr>
      <p>{{ banner.instructions }}</p>
      <p class="lead">
        <a class="btn btn-primary btn-lg" href="#" role="button">Learn more</a>
      </p>
  </b-jumbotron>
</template>

<script>
export default {
  name: 'Banner',
  props: {
    banner: Object
  }
}
</script>

<style scoped>
#bj {
  text-align: center;
}
</style>

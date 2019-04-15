<template>
  <div class="banner">
    <div class="jumbotron">
      <h1 class="display-4">{{ title }}</h1>
        <p class="lead">Use this form to upload your 3d models, 360 videos, and VR source code & projects</p>
        <hr class="my-4">
        <p>Your files will be deposited into a Library repository and published to a third-party website. You will receive a confirmation email when your deposit is processed.</p>
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
    title: String
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>

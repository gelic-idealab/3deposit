<template>
  <div class="content">
    <div class="container-fluid">
        <transition name="fade" mode="out-in">
          <!-- your content here -->
          <router-view :current_user="current_user"></router-view>
        </transition>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    current_user: Object
  }
};
</script>
<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.1s;
}

.fade-enter,
  .fade-leave-to
  /* .fade-leave-active in <2.1.8 */

 {
  opacity: 0;
}
</style>

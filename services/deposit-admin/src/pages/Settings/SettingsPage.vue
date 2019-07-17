<template>
    <div class="row">
        <service-list>

        </service-list>
      <div class="col-xl-8 col-lg-7 col-md-6">
        <configure-service>

        </configure-service>
      </div>
    </div>
</template>
<script>
import ConfigureService from "./ConfigureService.vue";
export default {
  components: {
    ConfigureService,
    ServiceList
  }
};
</script>
<style>
</style>

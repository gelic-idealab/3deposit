<template>
  <div class="wrapper">
    <side-bar>
      <template slot="links">
        <sidebar-link to="/admin/dashboard" name="Dashboard" icon="ti-panel"/>
        <sidebar-link to="/admin/stats" name="User Profile" icon="ti-user"/>
        <sidebar-link to="/admin/services" name="Services" icon="ti-widget"/>
        <sidebar-link to="/admin/deposits" name="Deposits" icon="ti-dropbox"/>
        <sidebar-link to="/admin/gallery-builder" name="Gallery" icon="ti-gallery"/>
        <sidebar-link to="/admin/icons" name="Icons" icon="ti-pencil-alt2"/>
        <sidebar-link to="/admin/notifications" name="Notifications" icon="ti-bell"/>
        <sidebar-link to="/admin/forms" name="Deposit Forms" icon="ti-pencil-alt"/>
      </template>
      <mobile-menu>
        <li class="nav-item">
          <a class="nav-link">
            <i class="ti-panel"></i>
            <p>Stats</p>
          </a>
        </li>
        <drop-down class="nav-item"
                   title="5 Notifications"
                   title-classes="nav-link"
                   icon="ti-bell">
          <a class="dropdown-item">Notification 1</a>
          <a class="dropdown-item">Notification 2</a>
          <a class="dropdown-item">Notification 3</a>
          <a class="dropdown-item">Notification 4</a>
          <a class="dropdown-item">Another notification</a>
        </drop-down>
        <li class="nav-item">
          <a class="nav-link">
            <i class="ti-settings"></i>
            <p>Settings</p>
          </a>
        </li>
        <li class="divider"></li>
      </mobile-menu>
    </side-bar>
    <div class="main-panel">
      <top-navbar></top-navbar>

      <dashboard-content @click.native="toggleSidebar">

      </dashboard-content>

      <content-footer></content-footer>
    </div>
  </div>
</template>
<style lang="scss">
</style>
<script>
import TopNavbar from "./TopNavbar.vue";
import ContentFooter from "./ContentFooter.vue";
import DashboardContent from "./Content.vue";
import MobileMenu from "./MobileMenu";
export default {
  components: {
    TopNavbar,
    ContentFooter,
    DashboardContent,
    MobileMenu
  },
  methods: {
    toggleSidebar() {
      if (this.$sidebar.showSidebar) {
        this.$sidebar.displaySidebar(false);
      }
    }
  }
};
</script>

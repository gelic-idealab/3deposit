import DashboardLayout from "@/layout/dashboard/DashboardLayout.vue";
// GeneralViews
import NotFound from "@/pages/NotFoundPage.vue";

// Admin pages
import Dashboard from "@/pages/Dashboard.vue";
import UserProfile from "@/pages/UserProfile.vue";
import Notifications from "@/pages/Notifications.vue";
import Icons from "@/pages/Icons.vue";
import Deposits from "@/pages/Deposits.vue";
import Services from "@/pages/Services.vue";
import DepositProfile from "@/pages/DepositProfile.vue";
import FormBuilder from "@/pages/FormBuilder.vue";
import GalleryBuilder from "@/pages/GalleryBuilder.vue";

const routes = [
  {
    path: "/",
    component: DashboardLayout,
    children: [
      {
        path: "dashboard",
        name: "dashboard",
        component: Dashboard
      },
      {
        path: "stats",
        name: "stats",
        component: UserProfile
      },
      {
        path: "notifications",
        name: "notifications",
        component: Notifications
      },
      {
        path: "icons",
        name: "icons",
        component: Icons
      },
      {
        path: "services",
        name: "services",
        component: Services
      },
      {
        path: "deposits",
        name: "deposits",
        component: Deposits
      },
      {
        path: "forms",
        name: "form-builder",
        component: FormBuilder
      },
      {
        path: "gallery-builder",
        name: "gallery-builder",
        component: GalleryBuilder
      },
      {
        path: "deposits/:id", 
        name: "deposit-profile", 
        component: DepositProfile
      },
    ]
  },
  { path: "*", component: NotFound }
];

/**
 * Asynchronously load view (Webpack Lazy loading compatible)
 * The specified component must be inside the Views folder
 * @param  {string} name  the filename (basename) of the view to load.
function view(name) {
   var res= require('../components/Dashboard/Views/' + name + '.vue');
   return res;
};**/

export default routes;

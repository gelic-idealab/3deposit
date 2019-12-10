import DashboardLayout from "@/layout/dashboard/DashboardLayout.vue";
// GeneralViews
import NotFound from "@/pages/NotFoundPage.vue";

// Admin pages
import Dashboard from "@/pages/Dashboard.vue";
import UserProfile from "@/pages/UserProfile.vue";
import Actions from '@/pages/Actions.vue';
import Deposits from "@/pages/Deposits.vue";
import Services from "@/pages/Services.vue";
import DepositProfile from "@/pages/DepositProfile.vue";
import FormBuilder from "@/pages/FormBuilder.vue";
import GalleryBuilder from "@/pages/GalleryBuilder.vue";
import GalleryEmbed from "@/pages/GalleryEmbed.vue";
import Settings from "@/pages/Settings.vue";
import Users from "@/pages/Settings/Users.vue";
import ServiceProfile from "@/pages/ServiceProfile.vue";
import UploadForm from "@/pages/UploadForm.vue";

const routes = [
  {
    path: "/admin",
    component: DashboardLayout,
    redirect: 'dashboard',
    children: [
      {
        path: "/dashboard",
        name: "dashboard",
        component: Dashboard
      },
      {
        path: "/profile",
        name: "profile",
        component: UserProfile
      },
      {
        path: "/actions",
        name: "actions",
        component: Actions
      },
      {
        path: "/users",
        name: "users",
        component: Users
      },
      {
        path: "/services",
        name: "services",
        component: Services
      },
      {
        path: "/services/:id", 
        name: "service-profile", 
        component: ServiceProfile
      },
      {
        path: "/deposits",
        name: "deposits",
        component: Deposits
      },
      {
        path: "/forms",
        name: "form-builder",
        component: FormBuilder
      },
      {
        path: "/gallery-builder",
        name: "gallery-builder",
        component: GalleryBuilder
      },
      {
        path: "/deposits/:id", 
        name: "deposit-profile", 
        component: DepositProfile
      },
      {
        path: "/settings",
        name: "settings",
        component: Settings
      }
    ]
  },
  {
    path: "/upload/:id", 
    name: "uploadForm", 
    component: UploadForm
  },
  {
    path: "/public/gallery",
    name: "public-gallery",
    component: GalleryEmbed 
  },
  { path: "/*", component: NotFound }
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

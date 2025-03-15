import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router';
import MainView from '../views/MainView.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: MainView
  }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

export default router;
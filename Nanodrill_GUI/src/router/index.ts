import { createRouter, createWebHashHistory } from 'vue-router';


const routes = [
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
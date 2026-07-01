import { defineRailway, project, service, postgres, preserve } from "railway/iac";

export default defineRailway(() => {
  const db = postgres("postgres");
  const web = service("web", {
    env: {
      DATABASE_URL: db.env.DATABASE_URL,
      DJANGO_DEBUG: "False",
      DJANGO_ALLOWED_HOSTS: ".railway.app,.up.railway.app,localhost,127.0.0.1",
      DJANGO_CSRF_TRUSTED_ORIGINS: "https://*.railway.app,https://*.up.railway.app,https://xingyunxue-production.up.railway.app,http://localhost:8000",
      DJANGO_SECRET_KEY: preserve(),
    },
  });

  return project("XHZS-TIC", {
    resources: [db, web],
  });
});

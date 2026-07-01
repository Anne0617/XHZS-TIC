const http = require("http");
const fs = require("fs");
const path = require("path");
const dist = "G:/心理测评系统/frontend/dist";
const mime = { html: "text/html", css: "text/css", js: "application/javascript", png: "image/png", svg: "image/svg+xml", ico: "image/x-icon", json: "application/json" };
// Override html to include charset
mime.html = "text/html; charset=utf-8";
http.createServer((req, res) => {
  // Proxy API calls to Django
  if (req.url.startsWith("/api/")) {
    const opts = { hostname: "127.0.0.1", port: 8000, path: req.url, method: req.method, headers: req.headers };
    const proxy = http.request(opts, (pr) => {
      res.writeHead(pr.statusCode, pr.headers);
      pr.pipe(res);
    });
    proxy.on("error", () => { res.writeHead(502); res.end("API unavailable"); });
    req.pipe(proxy);
    return;
  }
  // Root / serves corporate site, /corporate also works
  let filePath = req.url === "/" ? "/corporate.html" : req.url.split("?")[0];
  if (filePath === "/corporate" || filePath === "/corporate/") filePath = "/corporate.html";
  let fullPath = path.join(dist, filePath);
  fs.readFile(fullPath, (e, data) => {
    if (e) {
      // SPA fallback: serve index.html for SPA routes like /login, /dashboard
      fs.readFile(path.join(dist, "index.html"), (e2, d2) => {
        res.writeHead(200, { "Content-Type": "text/html" });
        res.end(d2);
      });
    } else {
      const ext = path.extname(fullPath).slice(1);
      res.writeHead(200, { "Content-Type": mime[ext] || "text/plain" });
      res.end(data);
    }
  });
}).listen(5173, () => { console.log("Frontend ready: http://localhost:5173"); });

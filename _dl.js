 const https = require("https");
 const fs = require("fs");
 const url = "https://mirrors.aliyun.com/python/3.12.10/python-3.12.10-amd64.exe";
 const file = fs.createWriteStream("C:\\tmp\\python-3.12.10-amd64.exe");
 console.log("Downloading from", url);
 https.get(url, (res) => {
   console.log("Status:", res.statusCode);
   let total = 0;
   res.on("data", (chunk) => { total += chunk.length; process.stdout.write("."); });
   res.pipe(file);
   res.on("end", () => { console.log("\nDone:", total, "bytes"); });
 }).on("error", (e) => { console.log("Error:", e.message); });

// vite.config.js
import { defineConfig } from "file:///D:/Oddo/hrms/frontend/node_modules/vite/dist/node/index.js";
import vue from "file:///D:/Oddo/hrms/frontend/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import { VitePWA } from "file:///D:/Oddo/hrms/frontend/node_modules/vite-plugin-pwa/dist/index.js";
import frappeui from "file:///D:/Oddo/hrms/frontend/node_modules/frappe-ui/vite.js";
import path from "path";
import fs from "fs";
var __vite_injected_original_dirname = "D:\\Oddo\\hrms\\frontend";
var vite_config_default = defineConfig({
  server: {
    port: 8080,
    proxy: getProxyOptions(),
    allowedHosts: true
  },
  plugins: [
    vue(),
    frappeui(),
    VitePWA({
      registerType: "autoUpdate",
      strategies: "injectManifest",
      injectRegister: null,
      devOptions: {
        enabled: true
      },
      manifest: {
        display: "standalone",
        name: "Frappe HR",
        short_name: "Frappe HR",
        start_url: "/hrms",
        scope: "/hrms",
        id: "/hrms",
        description: "Everyday HR & Payroll operations at your fingertips",
        theme_color: "#ffffff",
        icons: [
          {
            src: "/assets/hrms/manifest/manifest-icon-192.maskable.png",
            sizes: "192x192",
            type: "image/png",
            purpose: "any"
          },
          {
            src: "/assets/hrms/manifest/manifest-icon-192.maskable.png",
            sizes: "192x192",
            type: "image/png",
            purpose: "maskable"
          },
          {
            src: "/assets/hrms/manifest/manifest-icon-512.maskable.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "any"
          },
          {
            src: "/assets/hrms/manifest/manifest-icon-512.maskable.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "maskable"
          }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      "@": path.resolve(__vite_injected_original_dirname, "src")
    }
  },
  build: {
    outDir: "../hrms/public/frontend",
    emptyOutDir: true,
    target: "es2015",
    commonjsOptions: {
      include: [/tailwind.config.js/, /node_modules/]
    },
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          "frappe-ui": ["frappe-ui"]
        }
      }
    }
  },
  optimizeDeps: {
    include: [
      "frappe-ui > feather-icons",
      "showdown",
      "tailwind.config.js",
      "engine.io-client"
    ]
  }
});
function getProxyOptions() {
  const config = getCommonSiteConfig();
  const webserver_port = config ? config.webserver_port : 8e3;
  if (!config) {
    console.log("No common_site_config.json found, using default port 8000");
  }
  return {
    "^/(app|login|api|assets|files|private)": {
      target: `http://127.0.0.1:${webserver_port}`,
      ws: true,
      router: function(req) {
        const site_name = req.headers.host.split(":")[0];
        console.log(`Proxying ${req.url} to ${site_name}:${webserver_port}`);
        return `http://${site_name}:${webserver_port}`;
      }
    }
  };
}
function getCommonSiteConfig() {
  let currentDir = path.resolve(".");
  while (currentDir !== "/") {
    if (fs.existsSync(path.join(currentDir, "sites")) && fs.existsSync(path.join(currentDir, "apps"))) {
      let configPath = path.join(currentDir, "sites", "common_site_config.json");
      if (fs.existsSync(configPath)) {
        return JSON.parse(fs.readFileSync(configPath));
      }
      return null;
    }
    currentDir = path.resolve(currentDir, "..");
  }
  return null;
}
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJEOlxcXFxPZGRvXFxcXGhybXNcXFxcZnJvbnRlbmRcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIkQ6XFxcXE9kZG9cXFxcaHJtc1xcXFxmcm9udGVuZFxcXFx2aXRlLmNvbmZpZy5qc1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vRDovT2Rkby9ocm1zL2Zyb250ZW5kL3ZpdGUuY29uZmlnLmpzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSBcInZpdGVcIlxyXG5pbXBvcnQgdnVlIGZyb20gXCJAdml0ZWpzL3BsdWdpbi12dWVcIlxyXG5pbXBvcnQgeyBWaXRlUFdBIH0gZnJvbSBcInZpdGUtcGx1Z2luLXB3YVwiXHJcbmltcG9ydCBmcmFwcGV1aSBmcm9tIFwiZnJhcHBlLXVpL3ZpdGVcIlxyXG5cclxuaW1wb3J0IHBhdGggZnJvbSBcInBhdGhcIlxyXG5pbXBvcnQgZnMgZnJvbSBcImZzXCJcclxuXHJcbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZyh7XHJcblx0c2VydmVyOiB7XHJcblx0XHRwb3J0OiA4MDgwLFxyXG5cdFx0cHJveHk6IGdldFByb3h5T3B0aW9ucygpLFxyXG5cdFx0YWxsb3dlZEhvc3RzOiB0cnVlLFxyXG5cdH0sXHJcblx0cGx1Z2luczogW1xyXG5cdFx0dnVlKCksXHJcblx0XHRmcmFwcGV1aSgpLFxyXG5cdFx0Vml0ZVBXQSh7XHJcblx0XHRcdHJlZ2lzdGVyVHlwZTogXCJhdXRvVXBkYXRlXCIsXHJcblx0XHRcdHN0cmF0ZWdpZXM6IFwiaW5qZWN0TWFuaWZlc3RcIixcclxuXHRcdFx0aW5qZWN0UmVnaXN0ZXI6IG51bGwsXHJcblx0XHRcdGRldk9wdGlvbnM6IHtcclxuXHRcdFx0XHRlbmFibGVkOiB0cnVlLFxyXG5cdFx0XHR9LFxyXG5cdFx0XHRtYW5pZmVzdDoge1xyXG5cdFx0XHRcdGRpc3BsYXk6IFwic3RhbmRhbG9uZVwiLFxyXG5cdFx0XHRcdG5hbWU6IFwiRnJhcHBlIEhSXCIsXHJcblx0XHRcdFx0c2hvcnRfbmFtZTogXCJGcmFwcGUgSFJcIixcclxuXHRcdFx0XHRzdGFydF91cmw6IFwiL2hybXNcIixcclxuXHRcdFx0XHRzY29wZTogXCIvaHJtc1wiLFxyXG5cdFx0XHRcdGlkOiBcIi9ocm1zXCIsXHJcblx0XHRcdFx0ZGVzY3JpcHRpb246IFwiRXZlcnlkYXkgSFIgJiBQYXlyb2xsIG9wZXJhdGlvbnMgYXQgeW91ciBmaW5nZXJ0aXBzXCIsXHJcblx0XHRcdFx0dGhlbWVfY29sb3I6IFwiI2ZmZmZmZlwiLFxyXG5cdFx0XHRcdGljb25zOiBbXHJcblx0XHRcdFx0XHR7XHJcblx0XHRcdFx0XHRcdHNyYzogXCIvYXNzZXRzL2hybXMvbWFuaWZlc3QvbWFuaWZlc3QtaWNvbi0xOTIubWFza2FibGUucG5nXCIsXHJcblx0XHRcdFx0XHRcdHNpemVzOiBcIjE5MngxOTJcIixcclxuXHRcdFx0XHRcdFx0dHlwZTogXCJpbWFnZS9wbmdcIixcclxuXHRcdFx0XHRcdFx0cHVycG9zZTogXCJhbnlcIixcclxuXHRcdFx0XHRcdH0sXHJcblx0XHRcdFx0XHR7XHJcblx0XHRcdFx0XHRcdHNyYzogXCIvYXNzZXRzL2hybXMvbWFuaWZlc3QvbWFuaWZlc3QtaWNvbi0xOTIubWFza2FibGUucG5nXCIsXHJcblx0XHRcdFx0XHRcdHNpemVzOiBcIjE5MngxOTJcIixcclxuXHRcdFx0XHRcdFx0dHlwZTogXCJpbWFnZS9wbmdcIixcclxuXHRcdFx0XHRcdFx0cHVycG9zZTogXCJtYXNrYWJsZVwiLFxyXG5cdFx0XHRcdFx0fSxcclxuXHRcdFx0XHRcdHtcclxuXHRcdFx0XHRcdFx0c3JjOiBcIi9hc3NldHMvaHJtcy9tYW5pZmVzdC9tYW5pZmVzdC1pY29uLTUxMi5tYXNrYWJsZS5wbmdcIixcclxuXHRcdFx0XHRcdFx0c2l6ZXM6IFwiNTEyeDUxMlwiLFxyXG5cdFx0XHRcdFx0XHR0eXBlOiBcImltYWdlL3BuZ1wiLFxyXG5cdFx0XHRcdFx0XHRwdXJwb3NlOiBcImFueVwiLFxyXG5cdFx0XHRcdFx0fSxcclxuXHRcdFx0XHRcdHtcclxuXHRcdFx0XHRcdFx0c3JjOiBcIi9hc3NldHMvaHJtcy9tYW5pZmVzdC9tYW5pZmVzdC1pY29uLTUxMi5tYXNrYWJsZS5wbmdcIixcclxuXHRcdFx0XHRcdFx0c2l6ZXM6IFwiNTEyeDUxMlwiLFxyXG5cdFx0XHRcdFx0XHR0eXBlOiBcImltYWdlL3BuZ1wiLFxyXG5cdFx0XHRcdFx0XHRwdXJwb3NlOiBcIm1hc2thYmxlXCIsXHJcblx0XHRcdFx0XHR9LFxyXG5cdFx0XHRcdF0sXHJcblx0XHRcdH0sXHJcblx0XHR9KSxcclxuXHRdLFxyXG5cdHJlc29sdmU6IHtcclxuXHRcdGFsaWFzOiB7XHJcblx0XHRcdFwiQFwiOiBwYXRoLnJlc29sdmUoX19kaXJuYW1lLCBcInNyY1wiKSxcclxuXHRcdH0sXHJcblx0fSxcclxuXHRidWlsZDoge1xyXG5cdFx0b3V0RGlyOiBcIi4uL2hybXMvcHVibGljL2Zyb250ZW5kXCIsXHJcblx0XHRlbXB0eU91dERpcjogdHJ1ZSxcclxuXHRcdHRhcmdldDogXCJlczIwMTVcIixcclxuXHRcdGNvbW1vbmpzT3B0aW9uczoge1xyXG5cdFx0XHRpbmNsdWRlOiBbL3RhaWx3aW5kLmNvbmZpZy5qcy8sIC9ub2RlX21vZHVsZXMvXSxcclxuXHRcdH0sXHJcblx0XHRzb3VyY2VtYXA6IHRydWUsXHJcblx0XHRyb2xsdXBPcHRpb25zOiB7XHJcblx0XHRcdG91dHB1dDoge1xyXG5cdFx0XHRcdG1hbnVhbENodW5rczoge1xyXG5cdFx0XHRcdFx0XCJmcmFwcGUtdWlcIjogW1wiZnJhcHBlLXVpXCJdLFxyXG5cdFx0XHRcdH0sXHJcblx0XHRcdH0sXHJcblx0XHR9LFxyXG5cdH0sXHJcblx0b3B0aW1pemVEZXBzOiB7XHJcblx0XHRpbmNsdWRlOiBbXHJcblx0XHRcdFwiZnJhcHBlLXVpID4gZmVhdGhlci1pY29uc1wiLFxyXG5cdFx0XHRcInNob3dkb3duXCIsXHJcblx0XHRcdFwidGFpbHdpbmQuY29uZmlnLmpzXCIsXHJcblx0XHRcdFwiZW5naW5lLmlvLWNsaWVudFwiLFxyXG5cdFx0XSxcclxuXHR9LFxyXG59KVxyXG5cclxuZnVuY3Rpb24gZ2V0UHJveHlPcHRpb25zKCkge1xyXG5cdGNvbnN0IGNvbmZpZyA9IGdldENvbW1vblNpdGVDb25maWcoKVxyXG5cdGNvbnN0IHdlYnNlcnZlcl9wb3J0ID0gY29uZmlnID8gY29uZmlnLndlYnNlcnZlcl9wb3J0IDogODAwMFxyXG5cdGlmICghY29uZmlnKSB7XHJcblx0XHRjb25zb2xlLmxvZyhcIk5vIGNvbW1vbl9zaXRlX2NvbmZpZy5qc29uIGZvdW5kLCB1c2luZyBkZWZhdWx0IHBvcnQgODAwMFwiKVxyXG5cdH1cclxuXHRyZXR1cm4ge1xyXG5cdFx0XCJeLyhhcHB8bG9naW58YXBpfGFzc2V0c3xmaWxlc3xwcml2YXRlKVwiOiB7XHJcblx0XHRcdHRhcmdldDogYGh0dHA6Ly8xMjcuMC4wLjE6JHt3ZWJzZXJ2ZXJfcG9ydH1gLFxyXG5cdFx0XHR3czogdHJ1ZSxcclxuXHRcdFx0cm91dGVyOiBmdW5jdGlvbiAocmVxKSB7XHJcblx0XHRcdFx0Y29uc3Qgc2l0ZV9uYW1lID0gcmVxLmhlYWRlcnMuaG9zdC5zcGxpdChcIjpcIilbMF1cclxuXHRcdFx0XHRjb25zb2xlLmxvZyhgUHJveHlpbmcgJHtyZXEudXJsfSB0byAke3NpdGVfbmFtZX06JHt3ZWJzZXJ2ZXJfcG9ydH1gKVxyXG5cdFx0XHRcdHJldHVybiBgaHR0cDovLyR7c2l0ZV9uYW1lfToke3dlYnNlcnZlcl9wb3J0fWBcclxuXHRcdFx0fSxcclxuXHRcdH0sXHJcblx0fVxyXG59XHJcblxyXG5mdW5jdGlvbiBnZXRDb21tb25TaXRlQ29uZmlnKCkge1xyXG5cdGxldCBjdXJyZW50RGlyID0gcGF0aC5yZXNvbHZlKFwiLlwiKVxyXG5cdC8vIHRyYXZlcnNlIHVwIHRpbGwgd2UgZmluZCBmcmFwcGUtYmVuY2ggd2l0aCBzaXRlcyBkaXJlY3RvcnlcclxuXHR3aGlsZSAoY3VycmVudERpciAhPT0gXCIvXCIpIHtcclxuXHRcdGlmIChcclxuXHRcdFx0ZnMuZXhpc3RzU3luYyhwYXRoLmpvaW4oY3VycmVudERpciwgXCJzaXRlc1wiKSkgJiZcclxuXHRcdFx0ZnMuZXhpc3RzU3luYyhwYXRoLmpvaW4oY3VycmVudERpciwgXCJhcHBzXCIpKVxyXG5cdFx0KSB7XHJcblx0XHRcdGxldCBjb25maWdQYXRoID0gcGF0aC5qb2luKGN1cnJlbnREaXIsIFwic2l0ZXNcIiwgXCJjb21tb25fc2l0ZV9jb25maWcuanNvblwiKVxyXG5cdFx0XHRpZiAoZnMuZXhpc3RzU3luYyhjb25maWdQYXRoKSkge1xyXG5cdFx0XHRcdHJldHVybiBKU09OLnBhcnNlKGZzLnJlYWRGaWxlU3luYyhjb25maWdQYXRoKSlcclxuXHRcdFx0fVxyXG5cdFx0XHRyZXR1cm4gbnVsbFxyXG5cdFx0fVxyXG5cdFx0Y3VycmVudERpciA9IHBhdGgucmVzb2x2ZShjdXJyZW50RGlyLCBcIi4uXCIpXHJcblx0fVxyXG5cdHJldHVybiBudWxsXHJcbn1cclxuIl0sCiAgIm1hcHBpbmdzIjogIjtBQUF5UCxTQUFTLG9CQUFvQjtBQUN0UixPQUFPLFNBQVM7QUFDaEIsU0FBUyxlQUFlO0FBQ3hCLE9BQU8sY0FBYztBQUVyQixPQUFPLFVBQVU7QUFDakIsT0FBTyxRQUFRO0FBTmYsSUFBTSxtQ0FBbUM7QUFRekMsSUFBTyxzQkFBUSxhQUFhO0FBQUEsRUFDM0IsUUFBUTtBQUFBLElBQ1AsTUFBTTtBQUFBLElBQ04sT0FBTyxnQkFBZ0I7QUFBQSxJQUN2QixjQUFjO0FBQUEsRUFDZjtBQUFBLEVBQ0EsU0FBUztBQUFBLElBQ1IsSUFBSTtBQUFBLElBQ0osU0FBUztBQUFBLElBQ1QsUUFBUTtBQUFBLE1BQ1AsY0FBYztBQUFB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

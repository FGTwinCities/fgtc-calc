import { defineConfig } from "vite";
import litestar from "litestar-vite-plugin";
import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";


export default defineConfig({
  server: {
    host: "0.0.0.0",
    port: Number(process.env.VITE_PORT || "5173"),
    cors: true,
    hmr: {
      host: "localhost",
    },
  },
  plugins: [
    vue(),
    tailwindcss(),
    litestar({
      input: ["src/main.js"],
    }),
  ],
  build: {
    rollupOptions: {
      onwarn(warning, warn) {
        // Suppress eval warnings from htmx (htmx uses eval for dynamic attribute evaluation)
        if (warning.code === "EVAL" && warning.id?.includes("htmx")) {
          return;
        }
        warn(warning);
      },
    },
  },
  resolve: {
    alias: {
      "@": "/src",
    },
  },
});

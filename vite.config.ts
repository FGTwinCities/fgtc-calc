import { defineConfig } from "vite";
import litestar from "litestar-vite-plugin";
import tailwindcss from "@tailwindcss/vite";


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
    tailwindcss(),
    litestar({
      input: [
        "src/main.js",
        "src/buildsheet.js",
        "src/build/create.js",
        "src/build/search.js",
        ],
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

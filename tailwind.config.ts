import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: "#0B0F14",
        surface: "#111827",
        elevated: "#172033",
        border: "#263244",
        text: "#F5F7FA",
        muted: "#9CA3AF",
        faint: "#6B7280",
        accent: {
          DEFAULT: "#00D1B2",
          soft: "#00D1B233",
        },
        violet: "#7C3AED",
        warn: "#F59E0B",
        danger: "#EF4444",
        ok: "#22C55E",
      },
      fontFamily: {
        sans: ["ui-sans-serif", "system-ui", "Inter", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      boxShadow: {
        glow: "0 0 0 1px #263244, 0 0 20px -8px #00D1B255",
      },
      fontVariantNumeric: {
        tabular: "tabular-nums",
      },
    },
  },
  plugins: [],
};

export default config;

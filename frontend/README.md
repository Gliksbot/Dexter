# Dexter Frontend

This React application provides the web interface for Dexter. It is built with [Vite](https://vitejs.dev/).

## Getting Started

```bash
cd frontend
npm install --no-package-lock
npm run dev
```

The UI expects a backend running at `http://localhost:8000` by default. To point to a different backend, set the `VITE_API_BASE_URL` environment variable.

## Production Build

```bash
npm run build
```

The compiled assets will be output to the `dist/` directory.

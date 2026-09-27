# BusiAI Frontend

Next.js 16 web application and analytics dashboard for BusiAI.

## Tech Stack

* **Framework:** Next.js 16 (App Router, Turbopack)
* **UI & Styling:** Tailwind CSS 4, Lucide React
* **Charts & Visualizations:** Recharts 3
* **Language:** TypeScript 5

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Configure environment (optional):
```bash
cp .env.example .env.local
```
*(By default, connects to `http://localhost:8000/api/v1`)*

3. Start development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

## Build for Production

```bash
npm run build
npm run start
```

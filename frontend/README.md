# Frontend (Recommended: Next.js + TypeScript)

## Why
- Enterprise UX, strong SEO, component ecosystem.

## Suggested Setup (local)
- `npx create-next-app@latest`
- Add pages:
  - Category selection
  - Top 5 table
  - Product detail with AI explanation

## API Integration
- Base URL: `http://localhost:8000`
- `GET /categories`
- `POST /categories`
- `GET /top5`
- `GET /explain/{asin}`

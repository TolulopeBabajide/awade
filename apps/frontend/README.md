# Awade Frontend

A modern, responsive React application for the Awade AI-powered educator support platform.

## 🚀 Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- Node.js 18+ (for local development)

### Running with Docker (Recommended)

1. **Start the frontend only:**
   ```bash
   # From the project root
   ./scripts/run_frontend_docker.sh
   ```

2. **Or use docker-compose directly:**
   ```bash
   # From the project root
   docker-compose -f docker-compose.dev.yml up --build frontend
   ```

3. **Start full stack (frontend + backend + database):**
   ```bash
   # From the project root
   docker-compose up --build
   ```

### Local Development

1. **Install dependencies:**
   ```bash
   cd apps/frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

## 🏗️ Project Structure

```
apps/frontend/
├── src/
│   ├── components/          # Reusable UI components
│   ├── pages/              # Page components
│   ├── utils/              # Utility functions
│   ├── types/              # TypeScript type definitions
│   ├── assets/             # Static assets
│   ├── App.tsx             # Main app component
│   ├── main.tsx            # React entry point
│   └── index.css           # Global styles
├── public/                 # Public assets
├── Dockerfile              # Production Docker configuration
├── Dockerfile.dev          # Development Docker configuration
├── docker-compose.dev.yml  # Development Docker Compose
├── tailwind.config.js      # Tailwind CSS configuration
├── vite.config.ts          # Vite configuration
└── package.json            # Dependencies and scripts
```

## 🎨 Design System

The frontend uses a custom design system with:

- **Colors:** Primary (blue), Secondary (purple), Accent (yellow), Success, Warning, Error
- **Typography:** Inter (body), Poppins (headings)
- **Components:** Custom button styles, cards, gradients
- **Animations:** Fade-in, slide-up, bounce effects

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
NODE_ENV=development
```

### Tailwind CSS

The project uses Tailwind CSS with custom configurations:
- Custom color palette
- Custom animations
- Responsive design utilities
- Component classes

## 📱 Features

- **Responsive Design:** Mobile-first approach
- **Modern UI:** Clean, professional interface
- **Accessibility:** WCAG compliant components
- **Performance:** Optimized with Vite
- **Type Safety:** Full TypeScript support

## 🐳 Docker Commands

### Development
```bash
# Build and run development container
docker-compose -f docker-compose.dev.yml up --build frontend

# Run in background
docker-compose -f docker-compose.dev.yml up -d frontend

# View logs
docker-compose -f docker-compose.dev.yml logs -f frontend

# Stop containers
docker-compose -f docker-compose.dev.yml down
```

### Production
```bash
# Build production image
docker build -f apps/frontend/Dockerfile -t awade-frontend:latest apps/frontend

# Run production container
docker run -p 3000:3000 awade-frontend:latest
```

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

## 📦 Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## 🔍 Linting and Formatting

```bash
# Lint code
npm run lint

# Format code
npm run format

# Fix linting issues
npm run lint:fix
```

## 🌐 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 📄 License

This project is licensed under the AGPL-3.0 License. 
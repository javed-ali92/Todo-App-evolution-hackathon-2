# Quickstart Guide: Todo App Frontend UI/UX

## Overview

This guide provides instructions for setting up and running the Todo App frontend with its premium UI/UX implementation. The frontend is built with Next.js using the App Router, featuring responsive design, smooth animations, and secure authentication integration.

## Prerequisites

- Node.js 18.x or higher
- npm or yarn package manager
- Git for version control
- Access to the backend API (FastAPI server running)

## Environment Setup

### 1. Clone the Repository
```bash
git clone [repository-url]
cd hackathon-todo
cd frontend
```

### 2. Install Dependencies
```bash
npm install
# or
yarn install
```

### 3. Environment Configuration
Create a `.env.local` file in the frontend directory:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
NEXT_PUBLIC_JWT_SECRET=your-jwt-secret-here
```

## Development Setup

### 1. Running the Development Server
```bash
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:3000`

### 2. Backend API Connection
Ensure your backend API is running on `http://localhost:8000` before starting the frontend.

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout with global styles
│   ├── page.tsx            # Landing page
│   ├── login/page.tsx      # Login page
│   ├── signup/page.tsx     # Signup page
│   ├── dashboard/
│   │   ├── layout.tsx      # Dashboard layout with navigation
│   │   └── page.tsx        # Dashboard main content
│   └── globals.css         # Global styles
├── components/
│   ├── ui/                 # Reusable UI components
│   ├── forms/              # Form components
│   └── layouts/            # Layout components
├── lib/
│   ├── auth.ts             # Authentication utilities
│   └── api.ts              # API utilities
├── hooks/
│   └── use-media-query.ts  # Responsive hooks
├── public/
│   └── images/
├── styles/
│   └── theme.css           # Theme variables
├── types/
│   └── index.ts            # TypeScript type definitions
├── package.json
├── tailwind.config.js
├── next.config.js
└── tsconfig.json
```

## Key Technologies

### Next.js Features
- **App Router**: Modern routing system with nested layouts
- **Server Components**: Optimized rendering for static content
- **Client Components**: Interactive UI elements with state management
- **Built-in Optimization**: Image optimization, font optimization

### Styling & UI
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **Framer Motion**: Animation library for smooth, professional animations
- **Premium Design**: Rounded components, soft shadows, consistent spacing

### Authentication
- **Better Auth**: Complete authentication solution with JWT support
- **Protected Routes**: Middleware to protect sensitive pages
- **Session Management**: Secure handling of authentication tokens

## Running Different Environments

### Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
npm start
```

### Preview Mode
```bash
npm run build
npm run start
```

## API Integration

### Authentication Flow
1. User registers/logins via Better Auth
2. JWT token received and stored securely
3. Token automatically attached to all API requests
4. Backend validates token and authorizes requests

### API Endpoints Used
- `GET /api/{user_id}/tasks` - Retrieve user's tasks
- `POST /api/{user_id}/tasks` - Create new task
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion

## Key Features

### Responsive Design
- Mobile-first approach with progressive enhancement
- Optimized layouts for mobile, tablet, and desktop
- Touch-friendly interface with adequate touch targets

### Premium UI Elements
- Smooth animations and transitions
- Consistent spacing and typography
- Rounded components with soft shadows
- Accessible color contrast ratios

### Task Management
- Create, read, update, delete tasks
- Filter tasks by completion status and priority
- Search functionality for quick task location
- Visual indicators for task priority and status

## Troubleshooting

### Common Issues

#### API Connection Problems
- Ensure backend server is running
- Check that environment variables are correctly set
- Verify CORS settings on the backend

#### Authentication Issues
- Confirm Better Auth is properly configured
- Check that JWT secrets match between frontend and backend
- Ensure tokens are being stored and sent correctly

#### Styling Problems
- Verify Tailwind CSS is properly configured
- Check that the global CSS file is imported
- Ensure all necessary dependencies are installed

### Development Tips

#### Component Development
- Start with reusable UI components
- Use consistent prop interfaces
- Implement proper error boundaries
- Add loading states for async operations

#### Performance Optimization
- Use React.memo for expensive components
- Implement lazy loading for non-critical components
- Optimize images and assets
- Minimize bundle size with code splitting

## Next Steps

1. **Customize the design**: Adjust colors, fonts, and spacing to match brand requirements
2. **Extend functionality**: Add advanced features like task categories or recurring tasks
3. **Enhance animations**: Fine-tune animations for specific user interactions
4. **Improve accessibility**: Conduct thorough accessibility testing
5. **Add testing**: Implement comprehensive unit and integration tests
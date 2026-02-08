# VIP Todo App - Premium Task Management

A luxurious, feature-rich todo application with smooth animations and premium design.

## 🎨 VIP Design Features

- **Gold & Purple Theme**: Elegant gold accents on dark purple/black background
- **Smooth Animations**: Powered by Framer Motion for premium feel
- **Luxury Typography**: Playfair Display for headings, Inter for body text
- **Glass Morphism**: Beautiful card designs with backdrop blur effects
- **Particle Effects**: Animated background elements for premium experience

## 🚀 Tech Stack

- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS 3.4 with custom VIP theme
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Routing**: React Router DOM v6
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Forms**: React Hook Form

## 🎯 VIP Features

### Authentication
- Secure login/signup with validation
- Protected routes
- Token-based authentication

### Task Management
- Create, read, update, delete tasks
- Task completion toggle
- Priority levels (High/Medium/Low)
- Due dates
- Tags system
- Advanced filtering and search

### Dashboard
- Stats cards with animations
- Quick add functionality
- Filter tasks by status and priority
- Beautiful UI with smooth transitions

## 📁 Project Structure

```
src/
├── components/
│   ├── Header.jsx          # VIP navigation header
│   ├── Footer.jsx          # Premium footer
│   ├── HeroSection.jsx     # Landing page hero
│   ├── TodoForm.jsx        # Task creation/editing form
│   ├── TodoItem.jsx        # Individual task component
│   ├── TodoList.jsx        # Task listing with filters
│   ├── DashboardStats.jsx  # Stats cards component
│   └── ProtectedRoute.jsx  # Authentication guard
├── pages/
│   ├── LandingPage.jsx     # Homepage with features
│   ├── LoginPage.jsx       # Login form
│   ├── SignupPage.jsx      # Registration form
│   ├── DashboardPage.jsx   # Main dashboard
│   └── TodoAddPage.jsx     # Dedicated add page
├── context/
│   └── AuthContext.jsx     # Authentication state
├── api/
│   └── axios.js           # API client setup
├── App.jsx                # Main router
├── main.jsx               # Entry point
└── index.css              # Tailwind and custom styles
```

## 🛠️ Installation

1. Clone the repository
2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Visit `http://localhost:5173` in your browser

## 🎬 Animation Highlights

- Page transitions with smooth fade/slide effects
- Staggered animations for lists
- Interactive button hover effects
- Card hover lifts and shadows
- Loading spinners and skeleton screens
- Form validation animations
- Todo item entry/exit animations

## 🔐 API Integration

The app connects to a backend API at `http://localhost:8000` with the following endpoints:

- `POST /auth/signup` - User registration
- `POST /auth/login` - User authentication
- `POST /tasks` - Create new task
- `GET /tasks` - Get all tasks
- `PUT /tasks/:id` - Update task
- `DELETE /tasks/:id` - Delete task
- `PATCH /tasks/:id/toggle` - Toggle task completion

## 📱 Responsive Design

Fully responsive design that works on:
- Desktop (premium experience)
- Tablet (optimized layout)
- Mobile (touch-friendly)

## 🌟 VIP Experience

Every interaction feels premium with:
- Smooth 60fps animations
- Intuitive user flows
- Immediate feedback
- Error handling
- Loading states
- Success confirmations

## 🚀 Production Ready

- Proper error boundaries
- Loading states
- Empty states
- Form validation
- Security best practices
- Performance optimized
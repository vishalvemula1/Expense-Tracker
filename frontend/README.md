# Expense Tracker Frontend

A fully functional, visually polished frontend for the Expense Tracker API built with React, TypeScript, and Tailwind CSS.

## Features

- **Authentication**: Secure login and signup with JWT token management
- **Dashboard**: Overview of monthly spending with interactive charts
- **Expense Management**: Create, edit, delete, and search expenses
- **Category Management**: Organize expenses with customizable categories
- **User Profile**: Manage account settings and update profile information
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Beautiful UI**: Premium SaaS aesthetic with smooth animations

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **Zustand** - State management
- **React Router** - Navigation
- **Framer Motion** - Animations
- **Recharts** - Data visualization
- **Lucide React** - Icons
- **Vite** - Build tool

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:3000`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
src/
├── components/       # Reusable UI components
│   ├── Badge.tsx
│   ├── Card.tsx
│   ├── ConfirmDialog.tsx
│   ├── EmptyState.tsx
│   ├── Layout.tsx
│   ├── Loading.tsx
│   ├── Modal.tsx
│   └── ProtectedRoute.tsx
├── pages/           # Page components
│   ├── Categories.tsx
│   ├── Dashboard.tsx
│   ├── Expenses.tsx
│   ├── Login.tsx
│   ├── Profile.tsx
│   └── Signup.tsx
├── store/           # Zustand state management
│   ├── auth.ts
│   └── data.ts
├── lib/            # Utilities and API client
│   ├── api.ts
│   └── utils.ts
├── types/          # TypeScript type definitions
│   └── index.ts
├── App.tsx         # Main app component with routing
├── main.tsx        # Entry point
└── index.css       # Global styles
```

## API Integration

The frontend integrates with the Expense Tracker API using the following endpoints:

### Authentication
- `POST /auth/signup` - Create a new account
- `POST /auth/login` - Sign in to existing account

### Users
- `GET /me` - Get current user information
- `PUT /me` - Update user profile
- `DELETE /me` - Delete user account

### Categories
- `POST /me/categories/` - Create a new category
- `GET /me/categories/` - List all categories
- `GET /me/categories/{id}` - Get category details
- `PUT /me/categories/{id}` - Update category
- `DELETE /me/categories/{id}` - Delete category

### Expenses
- `POST /me/expenses/` - Create a new expense
- `GET /me/expenses/` - List all expenses
- `GET /me/expenses/{id}` - Get expense details
- `PUT /me/expenses/{id}` - Update expense
- `DELETE /me/expenses/{id}` - Delete expense

## Key Features

### Authentication & Security
- JWT token stored in memory (Zustand store)
- Automatic token injection in API requests
- Protected routes with redirect to login
- Automatic logout on 401 (Unauthorized)

### Smart Category Management
- Default category cannot be edited or deleted (buttons disabled)
- Color-coded category tags
- Category-wise expense grouping

### Expense Tracking
- Create expenses with optional category (uses default if not specified)
- Only changed fields sent on update (PATCH-like behavior)
- Search and filter expenses
- Real-time expense calculations

### User Experience
- Smooth animations with Framer Motion
- Responsive design for all screen sizes
- Loading states and error handling
- Confirmation dialogs for destructive actions
- Empty states with helpful CTAs

## Environment Variables

The frontend uses a proxy to connect to the backend API. By default, it proxies `/api` requests to `http://localhost:8000`. You can modify this in `vite.config.ts`.

## Development Notes

- All API calls go through the centralized API client (`lib/api.ts`)
- State management uses Zustand for simplicity and performance
- Forms use controlled components with validation
- Error handling is consistent across the application
- TypeScript ensures type safety throughout

## Contributing

When contributing to this project:

1. Follow the existing code style
2. Use TypeScript types for all new code
3. Test all CRUD operations before submitting
4. Ensure responsive design works on mobile
5. Add appropriate loading and error states

## License

This project is part of the Expense Tracker application.

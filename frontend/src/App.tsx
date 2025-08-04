import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'

import { AuthProvider } from './contexts/AuthContext'
import Header from './components/Header'
import ProtectedRoute from './components/auth/ProtectedRoute'
import ProjectList from './pages/ProjectList'
import CreateProject from './pages/CreateProject'
import ProjectDetail from './pages/ProjectDetail'
import Profile from './pages/Profile'
import CharacterChecklists from './pages/CharacterChecklists'

// Создаем экземпляр React Query клиента
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <div className="app">
            <Header />
            
            <main className="main-content">
              <Routes>
                <Route 
                  path="/" 
                  element={
                    <ProtectedRoute>
                      <ProjectList />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/projects/new" 
                  element={
                    <ProtectedRoute>
                      <CreateProject />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/projects/:id" 
                  element={
                    <ProtectedRoute>
                      <ProjectDetail />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/profile" 
                  element={<Profile />}
                />
                <Route 
                  path="/characters/:characterId/checklists" 
                  element={
                    <ProtectedRoute>
                      <CharacterChecklists />
                    </ProtectedRoute>
                  } 
                />
              </Routes>
            </main>

          <footer className="footer">
            <div className="container">
              <div className="footer-content">
                <div className="footer-title">Analyse Text</div>
                <p>Система анализа персонажей художественных произведений</p>
                
                <div className="footer-features">
                  <div className="footer-feature">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    3 модуля анализа
                  </div>
                  <div className="footer-feature">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Yandex GPT
                  </div>
                  <div className="footer-feature">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                    NLP обработка
                  </div>
                </div>
              </div>
            </div>
          </footer>
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App


import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'

import { AuthProvider } from './contexts/AuthContext'
import Header from './components/Header'
import ProtectedRoute from './components/auth/ProtectedRoute'
import ProjectList from './pages/ProjectList'
import CreateProject from './pages/CreateProject'
import ProjectDetail from './pages/ProjectDetail'
import Profile from './pages/Profile'
import CharacterChecklists from './pages/CharacterChecklistsV2'
import CharacterChecklistDetail from './pages/CharacterChecklistDetailV2'

// Импорт новых стилей v2
import './styles_v2/index.css'

import "@gravity-ui/uikit/styles/fonts.css";
import "@gravity-ui/uikit/styles/styles.css";

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
                <Route path="/" element={<ProjectList />} />
                <Route 
                  path="/create-project" 
                  element={
                    <ProtectedRoute>
                      <CreateProject />
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
                  element={
                    <ProtectedRoute>
                      <Profile />
                    </ProtectedRoute>
                  }
                />
                <Route 
                  path="/characters/:characterId/checklists" 
                  element={
                    <ProtectedRoute>
                      <CharacterChecklists />
                    </ProtectedRoute>
                  } 
                />
                <Route
                  path="/characters/:characterId/checklists/:checklistSlug"
                  element={
                    <ProtectedRoute>
                      <CharacterChecklistDetail />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/characters/:characterId/checklists/:checklistSlug/:questionExternalId"
                  element={
                    <ProtectedRoute>
                      <CharacterChecklistDetail />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </main>
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App

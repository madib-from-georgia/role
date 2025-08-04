import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import AuthModal from './auth/AuthModal'
import AuthGuard from './auth/AuthGuard'

const Header: React.FC = () => {
  const location = useLocation()
  const { user, logout, isAuthenticated } = useAuth()
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)

  const handleLogout = async () => {
    try {
      await logout()
      setShowUserMenu(false)
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  return (
    <>
      <header className="header">
        <div className="container">
          <div className="header-inner">
            <Link to="/" className="logo">
              <div className="logo-icon">AI</div>
              <span>Analyse Text</span>
            </Link>
            
            <nav className="nav">
              <AuthGuard
                fallback={
                  <div className="nav-guest">
                    <button 
                      className="nav-link auth-trigger"
                      onClick={() => setShowAuthModal(true)}
                    >
                      Войти
                    </button>
                  </div>
                }
              >
                <Link 
                  to="/" 
                  className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
                >
                  Проекты
                </Link>
                
                <Link 
                  to="/projects/new" 
                  className={`nav-link ${location.pathname === '/projects/new' ? 'active' : ''}`}
                >
                  Создать проект
                </Link>

                <a 
                  href="http://localhost:8000/docs" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="nav-link external"
                >
                  API Docs
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>

                {/* User Menu */}
                <div className="user-menu-container">
                  <button 
                    className="user-menu-trigger"
                    onClick={() => setShowUserMenu(!showUserMenu)}
                  >
                    <div className="user-avatar">
                      {user?.full_name 
                        ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase()
                        : user?.username.slice(0, 2).toUpperCase()
                      }
                    </div>
                    <span className="user-name">
                      {user?.full_name || user?.username}
                    </span>
                    <svg className={`user-menu-arrow ${showUserMenu ? 'open' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  {showUserMenu && (
                    <div className="user-menu-dropdown">
                      <Link 
                        to="/profile" 
                        className="user-menu-item"
                        onClick={() => setShowUserMenu(false)}
                      >
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        Профиль
                      </Link>
                      
                      <div className="user-menu-divider"></div>
                      
                      <button 
                        className="user-menu-item logout"
                        onClick={handleLogout}
                      >
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                        Выйти
                      </button>
                    </div>
                  )}
                </div>
              </AuthGuard>
            </nav>
          </div>

        {/* Хлебные крошки для внутренних страниц */}
        {location.pathname !== '/' && (
          <div className="breadcrumb">
            <Link to="/" className="breadcrumb-link">Главная</Link>
            <span className="breadcrumb-separator">/</span>
            <span className="breadcrumb-current">
              {location.pathname === '/projects/new' ? 'Новый проект' : 
               location.pathname === '/profile' ? 'Профиль' :
               location.pathname.includes('/projects/') ? 'Детали проекта' : 'Страница'}
            </span>
          </div>
        )}
      </div>
    </header>

    {/* Auth Modal */}
    <AuthModal 
      isOpen={showAuthModal}
      onClose={() => setShowAuthModal(false)}
    />
  </>
  )
}

export default Header

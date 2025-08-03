import React from 'react'
import { Link, useLocation } from 'react-router-dom'

const Header: React.FC = () => {
  const location = useLocation()

  return (
    <header className="header">
      <div className="container">
        <div className="header-inner">
          <Link to="/" className="logo">
            <div className="logo-icon">AI</div>
            <span>Analyse Text</span>
          </Link>
          
          <nav className="nav">
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
          </nav>
        </div>

        {/* Хлебные крошки для внутренних страниц */}
        {location.pathname !== '/' && (
          <div className="breadcrumb">
            <Link to="/" className="breadcrumb-link">Главная</Link>
            <span className="breadcrumb-separator">/</span>
            <span className="breadcrumb-current">
              {location.pathname === '/projects/new' ? 'Новый проект' : 
               location.pathname.includes('/projects/') ? 'Детали проекта' : 'Страница'}
            </span>
          </div>
        )}
      </div>
    </header>
  )
}

export default Header

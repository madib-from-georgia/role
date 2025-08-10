import React, { useState, useCallback } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button, User, ArrowToggle } from "@gravity-ui/uikit";
import { useAuth } from "../contexts/AuthContext";
import AuthModal from "./auth/AuthModal";
import AuthGuard from "./auth/AuthGuard";

const Header: React.FC = () => {
  const location = useLocation();
  const { user, logout } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = useCallback(async () => {
    try {
      await logout();
      setShowUserMenu(false);
    } catch (error) {
      console.error("Logout error:", error);
    }
  }, [logout]);

  const handleOpenAuthModal = useCallback(() => {
    setShowAuthModal(true);
  }, []);

  const handleCloseAuthModal = useCallback(() => {
    setShowAuthModal(false);
  }, []);

  return (
    <>
      <header className="header">
        <div className="container">
          <div className="header-inner">
            <Link to="/" className="logo">
              <div className="logo-icon">Р</div>
              <span>Роль</span>
            </Link>

            <nav className="nav">
              <AuthGuard
                fallback={
                  <div className="nav-guest">
                    <button
                      className="nav-link auth-trigger"
                      onClick={handleOpenAuthModal}
                    >
                      Войти
                    </button>
                  </div>
                }
              >
                <Link to="/">
                  <Button
                    view={location.pathname === "/" ? "normal" : "flat"}
                    size="l"
                  >
                    Проекты
                  </Button>
                </Link>

                <Link to="/projects/new">
                  <Button
                    view={
                      location.pathname === "/projects/new" ? "normal" : "flat"
                    }
                    size="l"
                  >
                    Создать проект
                  </Button>
                </Link>

                <Button
                  view="flat"
                  size="l"
                  href="/docs"
                  target="_blank"
                  className="nav-link external"
                >
                  API Docs
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                    />
                  </svg>
                </Button>

                {/* User Menu */}
                <div className="user-menu-container">
                  <Button
                    onClick={() => setShowUserMenu(!showUserMenu)}
                    view="flat"
                    size="l"
                  >
                    <div className="user-menu-trigger">
                      <User
                        avatar={{
                          text: `${user?.full_name || user?.username}`,
                          theme: "brand",
                        }}
                        name={user?.full_name || user?.username}
                        size="m"
                      />
                      <ArrowToggle
                        direction={showUserMenu ? "top" : "bottom"}
                      />
                    </div>
                  </Button>

                  {/* <button className="user-menu-trigger">
                    <div className="user-avatar">
                      {user?.full_name
                        ? user.full_name
                            .split(" ")
                            .map((n) => n[0])
                            .join("")
                            .toUpperCase()
                        : user?.username.slice(0, 2).toUpperCase()}
                    </div>
                    <span className="user-name">
                      {user?.full_name || user?.username}
                    </span>
                    <svg
                      className={`user-menu-arrow ${
                        showUserMenu ? "open" : ""
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 9l-7 7-7-7"
                      />
                    </svg>
                  </button> */}

                  {showUserMenu && (
                    <div className="user-menu-dropdown">
                      <Link
                        to="/profile"
                        className="user-menu-item"
                        onClick={() => setShowUserMenu(false)}
                      >
                        <svg
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                          />
                        </svg>
                        Профиль
                      </Link>

                      <div className="user-menu-divider"></div>

                      <button
                        className="user-menu-item logout"
                        onClick={handleLogout}
                      >
                        <svg
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                          />
                        </svg>
                        Выйти
                      </button>
                    </div>
                  )}
                </div>
              </AuthGuard>
            </nav>
          </div>
        </div>
      </header>

      {/* Auth Modal */}
      <AuthModal isOpen={showAuthModal} onClose={handleCloseAuthModal} />
    </>
  );
};

export default Header;

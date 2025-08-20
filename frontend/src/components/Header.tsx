import React, { useState, useCallback, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button, User, DropdownMenu } from "@gravity-ui/uikit";
import { useAuth } from "../contexts/AuthContext";
import AuthModal from "./auth/AuthModal";
import AuthGuard from "./auth/AuthGuard";

const Header: React.FC = () => {
  const location = useLocation();
  const { user, logout } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);

  const handleLogout = useCallback(async () => {
    try {
      await logout();
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

  const handleToggleMobileMenu = useCallback(() => {
    setShowMobileMenu(!showMobileMenu);
  }, [showMobileMenu]);

  const handleCloseMobileMenu = useCallback(() => {
    setShowMobileMenu(false);
  }, []);

  // Handle Esc key for mobile menu
  useEffect(() => {
    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && showMobileMenu) {
        handleCloseMobileMenu();
        // Remove focus from the button to avoid outline
        (document.activeElement as HTMLElement)?.blur();
      }
    };

    if (showMobileMenu) {
      document.addEventListener('keydown', handleEscKey);
    }

    return () => {
      document.removeEventListener('keydown', handleEscKey);
    };
  }, [showMobileMenu, handleCloseMobileMenu]);

  return (
    <>
      <header className="header">
        <div className="container">
          <div className="header-inner">
            <Link to="/" className="logo">
              <div className="logo-icon">Р</div>
              <span>Роль</span>
            </Link>

            {/* Mobile Menu Button */}
            <Button
              view="flat"
              size="l"
              className="mobile-menu-btn"
              onClick={handleToggleMobileMenu}
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </Button>

            <nav className="nav desktop-nav">
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

                {/* User Menu */}
                <div className="user-menu-container">
                  <DropdownMenu
                    renderSwitcher={(props) => (
                      <div {...props} className="user-menu-trigger">
                        <User
                          avatar={{
                            text: `${user?.full_name || user?.username}`,
                            theme: "brand",
                          }}
                          name={user?.full_name || user?.username}
                          size="m"
                        />
                      </div>
                    )}
                    popupProps={{placement: 'bottom-end'}}
                    items={[
                      {
                          action: () => console.log('Rename'),
                          text: 'Профиль',
                          href: "/profile"
                      },
                      {
                          action: handleLogout,
                          text: 'Выйти',
                          theme: 'danger',
                      },
                  ]} />

                </div>
              </AuthGuard>
            </nav>
          </div>
        </div>
      </header>

      {/* Mobile Menu */}
      {showMobileMenu && (
        <div className="mobile-menu-overlay" onClick={handleCloseMobileMenu}>
          <div className="mobile-menu" onClick={(e) => e.stopPropagation()}>
            <div className="mobile-menu-header">
              <div className="mobile-menu-logo">
                <div className="logo-icon">Р</div>
                <span>Роль</span>
              </div>
              <Button
                view="flat"
                size="m"
                className="mobile-menu-close"
                onClick={handleCloseMobileMenu}
              >
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </Button>
            </div>

            <nav className="mobile-menu-nav">
              <AuthGuard
                fallback={
                  <div className="mobile-nav-guest">
                    <Button
                      view="action"
                      size="l"
                      onClick={() => {
                        handleCloseMobileMenu();
                        handleOpenAuthModal();
                      }}
                    >
                      Войти
                    </Button>
                  </div>
                }
              >
                <Link to="/" onClick={handleCloseMobileMenu}>
                  <Button
                    view={location.pathname === "/" ? "normal" : "flat"}
                    size="l"
                    className="mobile-nav-link"
                  >
                    Проекты
                  </Button>
                </Link>

                <Link to="/projects/new" onClick={handleCloseMobileMenu}>
                  <Button
                    view={location.pathname === "/projects/new" ? "normal" : "flat"}
                    size="l"
                    className="mobile-nav-link"
                  >
                    Создать проект
                  </Button>
                </Link>

                {/* User Menu in Mobile */}
                <div className="mobile-user-section">
                  <div className="mobile-user-info">
                    <User
                      avatar={{
                        text: `${user?.full_name || user?.username}`,
                        theme: "brand",
                      }}
                      name={user?.full_name || user?.username}
                      size="m"
                    />
                  </div>

                  <Link to="/profile" onClick={handleCloseMobileMenu}>
                    <Button
                      view="flat"
                      size="l"
                      className="mobile-nav-link"
                    >
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                        />
                      </svg>
                      Профиль
                    </Button>
                  </Link>

                  <Button
                    view="flat"
                    size="l"
                    className="mobile-nav-link logout"
                    onClick={() => {
                      handleCloseMobileMenu();
                      handleLogout();
                    }}
                  >
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                      />
                    </svg>
                    Выйти
                  </Button>
                </div>
              </AuthGuard>
            </nav>
          </div>
        </div>
      )}

      {/* Auth Modal */}
      <AuthModal isOpen={showAuthModal} onClose={handleCloseAuthModal} />
    </>
  );
};

export default Header;

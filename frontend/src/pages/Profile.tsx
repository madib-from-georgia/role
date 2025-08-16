import React, { useState } from "react";
import { Button, TextInput, Label } from "@gravity-ui/uikit";
import { useAuth } from "../contexts/AuthContext";
import { authApi } from "../services/api/auth";
import ProtectedRoute from "../components/auth/ProtectedRoute";
import ChangePasswordForm from "../components/ChangePasswordForm";

const Profile: React.FC = () => {
  const { user, getAuthHeader } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showChangePassword, setShowChangePassword] = useState(false);

  const [editData, setEditData] = useState({
    username: user?.username || "",
    full_name: user?.full_name || "",
    email: user?.email || "",
  });

  const handleSave = async () => {
    if (!user) return;

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const authHeader = getAuthHeader();
      if (!authHeader) {
        throw new Error("Токен авторизации не найден");
      }

      await authApi.updateProfile(authHeader.replace("Bearer ", ""), editData);

      // Здесь можно было бы обновить пользователя в контексте,
      // но для простоты просто покажем сообщение об успехе
      setSuccess("Профиль успешно обновлен");
      setIsEditing(false);

      // Обновляем локальные данные
      // В реальном приложении лучше обновить состояние в AuthContext
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Ошибка обновления профиля"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setEditData({
      username: user?.username || "",
      full_name: user?.full_name || "",
      email: user?.email || "",
    });
    setIsEditing(false);
    setError(null);
    setSuccess(null);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEditData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  if (!user) {
    return <div>Загрузка...</div>;
  }

  return (
    <ProtectedRoute>
      <div className="profile-page">
        <div className="container">
          <div className="profile-header">
            <div className="profile-avatar">
              <div className="avatar-placeholder">
                {user.full_name
                  ? user.full_name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")
                      .toUpperCase()
                  : user.username.slice(0, 2).toUpperCase()}
              </div>
            </div>

            <div className="profile-info">
              <h1>{user.full_name || user.username}</h1>
              <p className="profile-email">{user.email}</p>
              <p className="profile-joined">
                Регистрация:{" "}
                {new Date(user.created_at).toLocaleDateString("ru-RU")}
              </p>
            </div>

            <div className="form-group">
              <span>Статус аккаунта: </span>
              <Label theme={user.is_active ? "success" : "warning"}>
                {user.is_active ? "Активный" : "Неактивный"}
              </Label>
            </div>
          </div>

          {(error || success) && (
            <div className="profile-messages">
              {error && (
                <div className="alert alert-error">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  {error}
                </div>
              )}
              {success && (
                <div className="alert alert-success">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  {success}
                </div>
              )}
            </div>
          )}

          <div className="profile-content">
            <div className="profile-card">
              <h2>Личная информация</h2>

              <div className="profile-fields">
                <div className="form-group">
                  <label>Имя пользователя</label>
                  {isEditing ? (
                    <TextInput
                      type="text"
                      name="username"
                      value={editData.username}
                      onChange={handleChange}
                      disabled={isLoading}
                    />
                  ) : (
                    <div className="field-value">{user.username}</div>
                  )}
                </div>

                <div className="form-group">
                  <label>Полное имя</label>
                  {isEditing ? (
                    <TextInput
                      type="text"
                      name="full_name"
                      value={editData.full_name}
                      onChange={handleChange}
                      disabled={isLoading}
                      placeholder="Ваше имя и фамилия"
                    />
                  ) : (
                    <div className="field-value">
                      {user.full_name || "Не указано"}
                    </div>
                  )}
                </div>

                <div className="form-group">
                  <label>Email</label>
                  {isEditing ? (
                    <TextInput
                      type="email"
                      name="email"
                      value={editData.email}
                      onChange={handleChange}
                      disabled={isLoading}
                    />
                  ) : (
                    <div className="field-value">{user.email}</div>
                  )}
                </div>
              </div>

              <div className="profile-actions">
                {!isEditing ? (
                  <Button onClick={() => setIsEditing(true)}>
                    Редактировать профиль
                  </Button>
                ) : (
                  <div className="edit-actions">
                    <Button onClick={handleSave} disabled={isLoading}>
                      {isLoading ? "Сохранение..." : "Сохранить"}
                    </Button>
                    <Button onClick={handleCancel} disabled={isLoading}>
                      Отмена
                    </Button>
                  </div>
                )}
              </div>
            </div>

            <div className="profile-card">
              <div className="security-section">
                {!showChangePassword ? (
                  <div className="security-info">
                    <Button
                      onClick={() => setShowChangePassword(true)}
                      disabled={isLoading}
                    >
                      Изменить пароль
                    </Button>
                  </div>
                ) : (
                  <ChangePasswordForm
                    onSuccess={() => {
                      setShowChangePassword(false);
                      setSuccess("Пароль успешно изменен");
                    }}
                    onCancel={() => setShowChangePassword(false)}
                  />
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default Profile;

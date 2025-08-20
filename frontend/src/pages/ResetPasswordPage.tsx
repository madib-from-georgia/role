import React from 'react'
import ResetPasswordForm from '../components/auth/ResetPasswordForm'

const ResetPasswordPage: React.FC = () => {
  return (
    <div className="auth-page">
      <div className="auth-container">
        <ResetPasswordForm />
      </div>
    </div>
  )
}

export default ResetPasswordPage

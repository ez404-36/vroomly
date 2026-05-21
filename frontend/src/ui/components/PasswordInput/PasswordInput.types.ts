import type React from 'react';

export interface PasswordInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  mt?: string;
  wrapperClassName?: string;
}

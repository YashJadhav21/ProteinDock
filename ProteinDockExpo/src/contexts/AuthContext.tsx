import AsyncStorage from '@react-native-async-storage/async-storage';
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  institution?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string, institution?: string) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadStoredAuth();
  }, []);

  const loadStoredAuth = async () => {
    try {
      const storedToken = await AsyncStorage.getItem('token');
      const storedUser = await AsyncStorage.getItem('user');
      
      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
      }
    } catch (error) {
      console.error('Failed to load auth:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      console.log('🔑 Attempting login for:', email);
      const response = await fetch('https://proteindock-production.up.railway.app/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      console.log('📡 Login response status:', response.status);
      const data = await response.json();
      console.log('📦 Login response data:', data);
      
      if (!response.ok) {
        console.error('❌ Login failed:', data.message);
        throw new Error(data.message || 'Login failed');
      }

      await AsyncStorage.setItem('token', data.token);
      await AsyncStorage.setItem('user', JSON.stringify(data.user));
      
      setToken(data.token);
      setUser(data.user);
      console.log('✅ Login successful!');
    } catch (error) {
      console.error('❌ Login error:', error);
      throw error;
    }
  };

  const register = async (name: string, email: string, password: string, institution?: string) => {
    try {
      console.log('📝 Attempting registration for:', email);
      const url = 'https://proteindock-production.up.railway.app/api/auth/register';
      const body = { name, email, password, institution };
      console.log('🌐 Request URL:', url);
      console.log('📤 Request body:', { ...body, password: '***' });
      
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      console.log('📡 Registration response status:', response.status);
      const data = await response.json();
      console.log('📦 Registration response data:', data);
      
      if (!response.ok) {
        console.error('❌ Registration failed:', data.message);
        throw new Error(data.message || 'Registration failed');
      }

      await AsyncStorage.setItem('token', data.token);
      await AsyncStorage.setItem('user', JSON.stringify(data.user));
      
      setToken(data.token);
      setUser(data.user);
      console.log('✅ Registration successful!');
    } catch (error) {
      console.error('❌ Registration error:', error);
      throw error;
    }
  };

  const logout = async () => {
    await AsyncStorage.removeItem('token');
    await AsyncStorage.removeItem('user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

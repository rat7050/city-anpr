import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiService } from '../lib/api';
import { User, LoginResponse } from '../types';
import { wsManager } from '../lib/websocket';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  role: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [role, setRole] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const res = await apiService.getMe();
          setUser(res.data);
          setRole(res.data.role);
          wsManager.connect(token);
        } catch (err) {
          localStorage.removeItem('token');
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = async (username: string, password: string) => {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    const res = await apiService.login(params);
    const data: LoginResponse = res.data;
    localStorage.setItem('token', data.access_token);
    setRole(data.role);
    const userRes = await apiService.getMe();
    setUser(userRes.data);
    wsManager.connect(data.access_token);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setRole(null);
    wsManager.disconnect();
  };

  if (loading) return <div className="min-h-screen bg-background flex items-center justify-center text-white">Loading...</div>;

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, role, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};

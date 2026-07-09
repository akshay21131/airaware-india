import { createContext, useContext, useEffect, useState } from "react";
import {
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signOut,
} from "firebase/auth";
import { auth, isFirebaseConfigured } from "./firebase";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(isFirebaseConfigured);

  useEffect(() => {
    if (!auth) {
      setAuthLoading(false);
      return;
    }
    const unsub = onAuthStateChanged(auth, (u) => {
      setUser(u);
      setAuthLoading(false);
    });
    return unsub;
  }, []);

  async function login(email, password) {
    if (!auth) throw new Error("Firebase isn't configured yet - see src/firebase.js");
    return signInWithEmailAndPassword(auth, email, password);
  }

  async function signup(email, password) {
    if (!auth) throw new Error("Firebase isn't configured yet - see src/firebase.js");
    return createUserWithEmailAndPassword(auth, email, password);
  }

  async function loginWithGoogle() {
    if (!auth) throw new Error("Firebase isn't configured yet - see src/firebase.js");
    return signInWithPopup(auth, new GoogleAuthProvider());
  }

  async function logout() {
    if (!auth) return;
    return signOut(auth);
  }

  return (
    <AuthContext.Provider
      value={{ user, authLoading, isFirebaseConfigured, login, signup, loginWithGoogle, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

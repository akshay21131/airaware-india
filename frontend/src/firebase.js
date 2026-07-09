import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// Firebase config - paste your own project's values here.
//
// Get these from: Firebase Console (console.firebase.google.com) > your
// project > Project settings > General > "Your apps" > Web app > SDK setup
// and configuration > Config.
//
// You'll also need to enable sign-in providers under
// Authentication > Sign-in method: turn on "Email/Password" and "Google".
//
// If left as placeholders, the app still runs fully - login/signup just
// show a "not configured" message instead of crashing anything else.
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDfwaFbo4MmfjhcLsefF-2fBwGm3u07BzA",
  authDomain: "airaware-26132.firebaseapp.com",
  projectId: "airaware-26132",
  storageBucket: "airaware-26132.firebasestorage.app",
  messagingSenderId: "186124426537",
  appId: "1:186124426537:web:8fb8f1e348288e9369eb38",
  measurementId: "G-DJ4RPKL38D"
};

export const isFirebaseConfigured = firebaseConfig.apiKey !== "YOUR_FIREBASE_API_KEY";

let auth = null;
if (isFirebaseConfigured) {
  try {
    const app = initializeApp(firebaseConfig);
    auth = getAuth(app);
  } catch (err) {
    console.warn("Firebase failed to initialize:", err);
    auth = null;
  }
}

export { auth };

"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error,    setError]    = useState("");
  const [loading,  setLoading]  = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const base = process.env.NEXT_PUBLIC_BACKEND_URL || "";
      const res = await fetch(`${base}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) {
        setError("Invalid username or password.");
        return;
      }
      const { token } = await res.json();
      sessionStorage.setItem("jadwa_token", token);
      window.location.href = "/gsk-splash.html";
    } catch {
      setError("Connection error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center p-6"
      style={{
        background:
          "radial-gradient(70% 55% at -5% 108%, rgba(107,45,139,.12) 0%, rgba(155,91,190,.06) 45%, rgba(255,255,255,0) 78%), linear-gradient(160deg,#fefdff 0%,#fdfaff 55%,#faf6ff 100%)",
      }}
    >
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="flex items-center justify-center mb-3">
            <img src="/gsk-new-logo.png" alt="GSK" style={{ height: 72, objectFit: "contain" }} />
          </div>
          <p className="text-xs font-semibold tracking-[0.3em]" style={{ color: "#6B2D8B" }}>
            AI PATIENT SIMULATOR
          </p>
          <p className="text-xs text-gray-400 mt-2">Doctor Training Platform</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl border shadow-xl p-8" style={{ borderColor: "rgba(107,45,139,0.15)", boxShadow: "0 20px 60px rgba(107,45,139,0.12)" }}>
          <h2 className="text-base font-semibold mb-6" style={{ color: "#3b0764" }}>
            Sign in to continue
          </h2>

          <form onSubmit={handleLogin} className="flex flex-col gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1.5 tracking-wide uppercase">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoComplete="username"
                placeholder="Enter username"
                className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 bg-gray-50 text-sm text-gray-900 placeholder-gray-400 focus:outline-none transition-all"
                onFocus={(e) => (e.target.style.boxShadow = "0 0 0 2px #8B3DAB")}
                onBlur={(e) => (e.target.style.boxShadow = "")}
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1.5 tracking-wide uppercase">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                placeholder="Enter password"
                className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 bg-gray-50 text-sm text-gray-900 placeholder-gray-400 focus:outline-none transition-all"
                onFocus={(e) => (e.target.style.boxShadow = "0 0 0 2px #8B3DAB")}
                onBlur={(e) => (e.target.style.boxShadow = "")}
              />
            </div>

            {error && (
              <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl font-bold text-white text-sm tracking-widest transition-all hover:opacity-90 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed mt-1"
              style={{ background: "linear-gradient(118deg,#8B3DAB 0%,#6B2D8B 48%,#5B1D7B 100%)" }}
            >
              {loading ? "Signing in…" : "SIGN IN"}
            </button>
          </form>
        </div>

        <p className="text-center text-xs text-gray-400 mt-6">
          GSK · Augmentin · Authorized Personnel Only
        </p>
      </div>
    </div>
  );
}

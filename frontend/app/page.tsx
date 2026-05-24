"use client";

import { useState } from "react";

export default function InkOS() {
  // --- AUTHENTICATION STATE ---
  const [token, setToken] = useState<string | null>(null);
  const [userHash, setUserHash] = useState("");
  const [pin, setPin] = useState("");
  const [authError, setAuthError] = useState("");
  const [isAuthenticating, setIsAuthenticating] = useState(false);

  // --- WORKSPACE STATE ---
  const [intent, setIntent] = useState("");
  const [targetModel, setTargetModel] = useState("ChatGPT");
  const [refinedPrompt, setRefinedPrompt] = useState("");
  const [audit, setAudit] = useState<{ score: number; critique: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [systemError, setSystemError] = useState("");

  // ── THE VAULT GATE (LOGIN) ──
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsAuthenticating(true);
    setAuthError("");

    try {
      const response = await fetch("https://inkos-engine.onrender.com/api/auth", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_hash: userHash,
          pin: pin,
          is_new: false,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Authentication sequence failed.");
      }

      // Vault Unlocked: Store the VIP Keycard
      setToken(data.token);
    } catch (err: any) {
      setAuthError(err.message);
    } finally {
      setIsAuthenticating(false);
    }
  };

  // ── THE INTELLIGENCE CORE (WORKSPACE) ──
  const handleRefine = async () => {
    if (!intent.trim() || !token) return;
    
    setIsLoading(true);
    setSystemError("");
    setRefinedPrompt("");
    setAudit(null);

    try {
      const response = await fetch("https://inkos-engine.onrender.com/api/refine", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          intent: intent,
          target_model: targetModel,
          framework: "Professional (RACE)",
          source_lang: "English",
          aesthetic_choice: "Default",
          hikmah_style: "None",
          skip_security: false,
          token: token, // Injecting the Keycard into the payload
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 401) {
          setToken(null); // Boot the user if token expired
          throw new Error("Session expired. Uplink severed.");
        }
        throw new Error(data.detail || `System Fault: ${response.status}`);
      }

      setRefinedPrompt(data.refined_prompt);
      setAudit(data.audit);
    } catch (err: any) {
      setSystemError(err.message || "Failed to establish uplink with the CIPHER engine.");
    } finally {
      setIsLoading(false);
    }
  };

  // ── RENDER: VAULT LOGIN SCREEN ──
  if (!token) {
    return (
      <main className="min-h-screen flex items-center justify-center p-6 bg-[var(--color-void)] relative overflow-hidden">
        {/* Background Grid Illusion */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_50%,#000_10%,transparent_100%)]"></div>

        <form onSubmit={handleLogin} className="relative z-10 w-full max-w-sm flex flex-col gap-6 bg-black/40 p-8 border border-[var(--color-border-subtle)] rounded-md backdrop-blur-md shadow-2xl">
          <div className="text-center mb-4">
            <h1 className="text-[var(--color-gold)] tracking-[0.3em] text-xl font-mono uppercase mb-2 shadow-gold">InkOS</h1>
            <p className="text-[12px] text-[var(--color-steel)] tracking-widest font-arabic font-bold">حبر وفكرة</p>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[9px] text-[var(--color-steel)] tracking-[0.2em] font-mono uppercase">System ID</label>
            <input 
              suppressHydrationWarning
              type="text" 
              value={userHash}
              onChange={(e) => setUserHash(e.target.value)}
              className="bg-[var(--color-input)] border border-[var(--color-border-subtle)] text-[var(--color-text-main)] text-sm p-3 font-mono focus:outline-none focus:border-[var(--color-gold)] transition-colors rounded-sm"
              autoComplete="off"
              required
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[9px] text-[var(--color-steel)] tracking-[0.2em] font-mono uppercase">Passcode</label>
            <input 
              suppressHydrationWarning
              type="password" 
              value={pin}
              onChange={(e) => setPin(e.target.value)}
              className="bg-[var(--color-input)] border border-[var(--color-border-subtle)] text-[var(--color-text-main)] text-sm p-3 font-mono tracking-widest focus:outline-none focus:border-[var(--color-gold)] transition-colors rounded-sm"
              required
            />
          </div>

          {authError && (
            <div className="text-[10px] text-[var(--color-danger)] font-mono border-l-2 border-[var(--color-danger)] pl-2">
              [!] Access Denied: {authError}
            </div>
          )}

          <button 
            suppressHydrationWarning
            type="submit"
            disabled={isAuthenticating}
            className="mt-4 bg-[var(--color-gold)] text-black py-3 text-[11px] font-mono font-bold tracking-[0.2em] uppercase rounded-sm hover:bg-[#E2D5BC] hover:shadow-[0_0_15px_rgba(201,168,76,0.3)] transition-all disabled:opacity-50"
          >
            {isAuthenticating ? "Verifying..." : "Initialize Uplink"}
          </button>
        </form>
      </main>
    );
  }

  // ── RENDER: WORKSPACE ──
  return (
    <main className="min-h-screen p-6 md:p-12 max-w-5xl mx-auto flex flex-col gap-6">
      <header className="flex items-center gap-3 border-b border-[var(--color-border-gold)] pb-3 mb-4">
        <div className="w-2 h-2 rounded-full bg-[var(--color-gold)] shadow-[0_0_6px_var(--color-gold)] shrink-0"></div>
        <h1 className="text-[var(--color-gold)] tracking-[0.2em] text-xs font-mono uppercase">Workspace</h1>
        <span className="ml-auto text-[10px] text-[var(--color-text-dim)] tracking-widest font-arabic">مساحة العمل</span>
      </header>

      <section className="flex flex-col gap-2">
        <div className="text-[10px] text-[var(--color-text-dim)] tracking-[0.2em] font-mono uppercase">
          [ 01 ] Source Intent
        </div>
        <textarea
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          placeholder="Describe what you want the AI to do..."
          className="w-full h-48 bg-black/30 border border-white/5 rounded-sm text-[var(--color-text-main)] text-sm p-4 font-mono focus:outline-none focus:border-[var(--color-gold)] transition-all resize-none"
        />
        
        <div className="flex justify-between items-center mt-2">
          <select 
            value={targetModel}
            onChange={(e) => setTargetModel(e.target.value)}
            className="bg-[var(--color-input)] border border-white/5 text-[var(--color-text-main)] text-xs p-2 rounded-sm font-mono focus:outline-none focus:border-[var(--color-gold)]"
          >
            <option value="ChatGPT">ChatGPT</option>
            <option value="Claude">Claude</option>
            <option value="Midjourney">Midjourney</option>
          </select>

          <button
            onClick={handleRefine}
            disabled={isLoading || !intent.trim()}
            className="bg-[var(--color-gold)] text-black px-8 py-2.5 text-[11px] font-mono font-bold tracking-[0.15em] uppercase rounded-sm hover:bg-[#E2D5BC] hover:shadow-[0_0_15px_rgba(201,168,76,0.4)] transition-all disabled:opacity-50"
          >
            {isLoading ? "Compiling..." : "⚡ Refine"}
          </button>
        </div>
      </section>

      {systemError && (
        <div className="bg-black/40 border border-[var(--color-border-subtle)] rounded-sm p-4 text-xs font-mono text-[var(--color-danger)]">
          System Fault: {systemError}
        </div>
      )}

      <section className="flex flex-col gap-3 mt-4">
        <div className="flex items-center gap-2 mb-2">
          <div className="text-[10px] text-[var(--color-gold)] tracking-[0.2em] font-mono uppercase">
            [ 03 ] Refined Output
          </div>
          <div className="flex-1 h-[1px] bg-gradient-to-r from-[var(--color-border-gold)] to-transparent"></div>
        </div>

        {audit && (
          <div className="bg-black/30 border border-white/5 rounded-sm p-3 flex items-center gap-4">
            <div className="flex flex-col items-center pr-4 border-r border-white/5">
              <span className={`font-mono text-2xl font-bold leading-none ${audit.score >= 85 ? 'text-[var(--color-success)]' : audit.score >= 70 ? 'text-[var(--color-gold)]' : 'text-[var(--color-danger)]'}`}>
                {audit.score}
              </span>
            </div>
            <div className="flex-1 font-mono text-[11px] text-[var(--color-steel)] italic">
              ✦ {audit.critique}
            </div>
          </div>
        )}

        {refinedPrompt && (
          <textarea
            readOnly
            value={refinedPrompt}
            className="w-full h-80 bg-black/40 border border-white/5 rounded-sm text-[var(--color-text-main)] text-[13px] p-4 font-mono focus:outline-none transition-all resize-none"
          />
        )}
      </section>
    </main>
  );
}
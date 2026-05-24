"use client";

import { useState, useEffect } from "react";

export default function InkOS() {
  // --- AUTHENTICATION STATE ---
  const [token, setToken] = useState<string | null>(null);
  const [userHash, setUserHash] = useState("");
  const [pin, setPin] = useState("");
  const [authError, setAuthError] = useState("");
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false); // NEW STATE: Toggle Registration

  // --- NAVIGATION & UI STATE ---
  const [activeTab, setActiveTab] = useState<"workspace" | "archive" | "profile">("workspace");
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // --- WORKSPACE CORE STATE ---
  const [intent, setIntent] = useState("");
  const [refinedPrompt, setRefinedPrompt] = useState("");
  const [audit, setAudit] = useState<{ score: number; critique: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [systemError, setSystemError] = useState("");

  // --- COGNITIVE MAP STATE ---
  const [targetModel, setTargetModel] = useState("ChatGPT");
  const [framework, setFramework] = useState("Professional (RACE)");
  const [sourceLang, setSourceLang] = useState("English");
  const [aesthetic, setAesthetic] = useState("Default");
  const [hikmahStyle, setHikmahStyle] = useState("None");

  // --- VISUAL DIRECTOR STATE ---
  const [aspectRatio, setAspectRatio] = useState("--ar 16:9");
  const [camera, setCamera] = useState("Cinematic Wide Shot, 35mm lens");
  const [lighting, setLighting] = useState("Volumetric, moody atmosphere");
  const [filmStock, setFilmStock] = useState("Cinestill 800T, high grain");

  // --- ARCHIVE STATE ---
  const [archiveItems, setArchiveItems] = useState<any[]>([]);
  const [isArchiveLoading, setIsArchiveLoading] = useState(false);

  // ── THE VAULT GATE (LOGIN / LOGOUT / REGISTER) ──
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsAuthenticating(true);
    setAuthError("");

    try {
      const response = await fetch("https://inkos-engine.onrender.com/api/auth", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        // Dynamically sends is_new based on UI toggle
        body: JSON.stringify({ user_hash: userHash, pin: pin, is_new: isRegistering }), 
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Authentication sequence failed.");
      setToken(data.token);
    } catch (err: any) {
      setAuthError(err.message);
    } finally {
      setIsAuthenticating(false);
    }
  };

  const handleLogout = () => {
    setToken(null);
    setPin("");
    setActiveTab("workspace");
    setArchiveItems([]);
  };

  // ── FETCH ARCHIVE ──
  const fetchArchive = async () => {
    if (!token) return;
    setIsArchiveLoading(true);
    try {
      const response = await fetch(`https://inkos-engine.onrender.com/api/vault?token=${token}`);
      const data = await response.json();
      if (response.ok) setArchiveItems(data.items || []);
    } catch (err) {
      console.error("Failed to fetch archive banks.");
    } finally {
      setIsArchiveLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === "archive" && archiveItems.length === 0) fetchArchive();
  }, [activeTab, token]);

  // ── THE INTELLIGENCE CORE ──
  const handleRefine = async () => {
    if (!intent.trim() || !token) return;
    
    setIsLoading(true);
    setSystemError("");
    setRefinedPrompt("");
    setAudit(null);

    let finalIntent = intent;
    if (targetModel === "Midjourney") {
      finalIntent = `[VISUAL DIRECTIVES]\nCamera: ${camera}\nLighting: ${lighting}\nFilm Stock: ${filmStock}\nAspect Ratio: ${aspectRatio}\n\n[SCENE DESCRIPTION]\n${intent}`;
    }

    try {
      const response = await fetch("https://inkos-engine.onrender.com/api/refine", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          intent: finalIntent,
          target_model: targetModel,
          framework: targetModel === "Midjourney" ? "Zero-Shot (Direct)" : framework,
          source_lang: targetModel === "Midjourney" ? "English" : sourceLang,
          aesthetic_choice: aesthetic,
          hikmah_style: targetModel === "Midjourney" ? "None" : hikmahStyle,
          skip_security: false,
          token: token, 
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 401) {
          handleLogout();
          throw new Error("Session expired. Uplink severed.");
        }
        throw new Error(data.detail || `System Fault: ${response.status}`);
      }

      setRefinedPrompt(data.refined_prompt);
      setAudit(data.audit);
      setArchiveItems([]); 
    } catch (err: any) {
      setSystemError(err.message || "Failed to establish uplink with the CIPHER engine.");
    } finally {
      setIsLoading(false);
    }
  };

  // ── SECURE CLIPBOARD ──
  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      const textArea = document.createElement("textarea");
      textArea.value = text;
      textArea.style.position = "fixed"; 
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      try {
        document.execCommand('copy');
        setCopiedId(id);
        setTimeout(() => setCopiedId(null), 2000);
      } catch (fallbackErr) {
        console.error("Clipboard bypass failed.");
      }
      document.body.removeChild(textArea);
    }
  };

  // ── RENDER: VAULT GATE (LOGIN / REGISTER) ──
  if (!token) {
    return (
      <main className="min-h-screen flex items-center justify-center p-6 bg-[var(--color-void)] relative overflow-hidden">
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_50%,#000_10%,transparent_100%)]"></div>
        <form onSubmit={handleLogin} className="relative z-10 w-full max-w-sm flex flex-col gap-6 bg-black/40 p-8 border border-[var(--color-border-subtle)] rounded-md backdrop-blur-md shadow-2xl">
          <div className="text-center mb-4">
            <h1 className="text-[var(--color-gold)] tracking-[0.3em] text-xl font-mono uppercase mb-2 shadow-gold">InkOS</h1>
            <p className="text-[12px] text-[var(--color-steel)] tracking-widest font-arabic font-bold">حبر وفكرة</p>
          </div>
          
          <div className="flex flex-col gap-1">
            <label className="text-[9px] text-[var(--color-steel)] tracking-[0.2em] font-mono uppercase">
              {isRegistering ? "Create System ID" : "System ID"}
            </label>
            <input suppressHydrationWarning type="text" value={userHash} onChange={(e) => setUserHash(e.target.value)} className="bg-[var(--color-input)] border border-[var(--color-border-subtle)] text-[var(--color-text-main)] text-sm p-3 font-mono focus:outline-none focus:border-[var(--color-gold)] transition-colors rounded-sm" autoComplete="off" required />
          </div>
          
          <div className="flex flex-col gap-1">
            <label className="text-[9px] text-[var(--color-steel)] tracking-[0.2em] font-mono uppercase">
              {isRegistering ? "Create Passcode" : "Passcode"}
            </label>
            <input suppressHydrationWarning type="password" value={pin} onChange={(e) => setPin(e.target.value)} className="bg-[var(--color-input)] border border-[var(--color-border-subtle)] text-[var(--color-text-main)] text-sm p-3 font-mono tracking-widest focus:outline-none focus:border-[var(--color-gold)] transition-colors rounded-sm" required />
          </div>
          
          {authError && <div className="text-[10px] text-[var(--color-danger)] font-mono border-l-2 border-[var(--color-danger)] pl-2">[!] {authError}</div>}
          
          <button suppressHydrationWarning type="submit" disabled={isAuthenticating} className="mt-4 bg-[var(--color-gold)] text-black py-3 text-[11px] font-mono font-bold tracking-[0.2em] uppercase rounded-sm hover:bg-[#E2D5BC] hover:shadow-[0_0_15px_rgba(201,168,76,0.3)] transition-all disabled:opacity-50">
            {isAuthenticating ? "Processing..." : isRegistering ? "Register Operator" : "Initialize Uplink"}
          </button>

          <div className="text-center mt-2 border-t border-white/10 pt-4">
            <button 
              type="button" 
              onClick={() => {
                setIsRegistering(!isRegistering);
                setAuthError(""); // Clear errors when toggling modes
              }} 
              className="text-[9px] text-[var(--color-steel)] tracking-[0.2em] font-mono uppercase hover:text-white transition-colors"
            >
              {isRegistering ? "[ Return to Login ]" : "[ Request New Clearance ]"}
            </button>
          </div>
        </form>
      </main>
    );
  }

  // ── RENDER: MAIN OS APPLICATION ──
  return (
    <div className="flex h-screen bg-[var(--color-void)] text-[var(--color-text-main)] overflow-hidden">
      
      {/* OS SIDEBAR */}
      <aside className="w-64 border-r border-white/5 bg-black/20 flex flex-col justify-between shrink-0">
        <div className="flex flex-col">
          {/* Brand Header */}
          <div className="p-8 border-b border-white/5">
            <div className="flex items-center gap-3 mb-1">
              <div className="w-2 h-2 rounded-full bg-[var(--color-gold)] shadow-[0_0_6px_var(--color-gold)] shrink-0 animate-pulse"></div>
              <h1 className="text-[var(--color-gold)] tracking-[0.3em] text-sm font-mono uppercase shadow-gold">InkOS</h1>
            </div>
            <span className="text-[11px] text-[var(--color-steel)] tracking-widest font-arabic font-bold block ml-5">حبر وفكرة</span>
          </div>

          {/* Navigation Matrix */}
          <nav className="flex flex-col gap-2 p-4 mt-4">
            <div className="text-[8px] text-[var(--color-steel)] tracking-[0.2em] font-mono uppercase mb-2 px-4">System Routing</div>
            
            <button onClick={() => setActiveTab("workspace")} className={`flex items-center gap-3 px-4 py-3 text-[11px] font-mono tracking-[0.1em] uppercase rounded-sm transition-all ${activeTab === "workspace" ? "bg-white/5 text-[var(--color-gold)] border-l-2 border-[var(--color-gold)]" : "text-[var(--color-steel)] hover:bg-white/5 hover:text-white border-l-2 border-transparent"}`}>
              <span className="text-[14px] leading-none opacity-80">◧</span> Workspace
            </button>
            
            <button onClick={() => setActiveTab("archive")} className={`flex items-center gap-3 px-4 py-3 text-[11px] font-mono tracking-[0.1em] uppercase rounded-sm transition-all ${activeTab === "archive" ? "bg-white/5 text-[var(--color-gold)] border-l-2 border-[var(--color-gold)]" : "text-[var(--color-steel)] hover:bg-white/5 hover:text-white border-l-2 border-transparent"}`}>
              <span className="text-[14px] leading-none opacity-80">≡</span> Memory Banks
            </button>

            <button onClick={() => setActiveTab("profile")} className={`flex items-center gap-3 px-4 py-3 text-[11px] font-mono tracking-[0.1em] uppercase rounded-sm transition-all ${activeTab === "profile" ? "bg-white/5 text-[var(--color-gold)] border-l-2 border-[var(--color-gold)]" : "text-[var(--color-steel)] hover:bg-white/5 hover:text-white border-l-2 border-transparent"}`}>
              <span className="text-[14px] leading-none opacity-80">👤</span> Operator Profile
            </button>
          </nav>
        </div>

        {/* User Mini-Profile & Logout */}
        <div className="p-6 border-t border-white/5 bg-black/40">
          <div className="text-[9px] text-[var(--color-steel)] tracking-[0.1em] font-mono uppercase mb-1">Active Operator</div>
          <div className="text-[12px] text-white font-mono mb-4">{userHash}</div>
          <button onClick={handleLogout} className="w-full bg-black/50 border border-[var(--color-danger)]/50 text-[var(--color-danger)] py-2 text-[10px] font-mono tracking-[0.2em] uppercase rounded-sm hover:bg-[var(--color-danger)] hover:text-black transition-all">
            [ Sever Uplink ]
          </button>
        </div>
      </aside>

      {/* OS MAIN VIEWPORT */}
      <main className="flex-1 overflow-y-auto p-8 lg:p-12 relative bg-[linear-gradient(rgba(255,255,255,0.01)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.01)_1px,transparent_1px)] bg-[size:40px_40px]">
        
        {/* VIEW: WORKSPACE */}
        {activeTab === "workspace" && (
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 animate-in fade-in duration-500 max-w-7xl mx-auto">
            {/* LEFT PANE: COMMAND TERMINAL */}
            <section className="xl:col-span-2 flex flex-col gap-4">
              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <div className="text-[10px] text-[var(--color-steel)] tracking-[0.2em] font-mono uppercase">[ 01 ] Source Intent</div>
                  <span className="text-[10px] text-[var(--color-steel)] tracking-widest font-arabic">القصد</span>
                </div>
                <textarea
                  value={intent}
                  onChange={(e) => setIntent(e.target.value)}
                  placeholder="Initiate prompt sequence..."
                  className="w-full h-32 bg-black/60 border border-white/10 rounded-sm text-[var(--color-text-main)] text-sm p-4 font-mono focus:outline-none focus:border-[var(--color-gold)] transition-all resize-none shadow-inner"
                />
              </div>

              <div className="flex justify-end mt-2">
                <button
                  onClick={handleRefine}
                  disabled={isLoading || !intent.trim()}
                  className="bg-[var(--color-gold)] text-black px-12 py-3 text-[11px] font-mono font-bold tracking-[0.2em] uppercase rounded-sm hover:bg-[#E2D5BC] hover:shadow-[0_0_15px_rgba(201,168,76,0.4)] transition-all disabled:opacity-50"
                >
                  {isLoading ? "Compiling..." : "⚡ Refine Payload"}
                </button>
              </div>

              {systemError && (
                <div className="bg-black/40 border border-[var(--color-danger)] rounded-sm p-4 text-xs font-mono text-[var(--color-danger)]">
                  System Fault: {systemError}
                </div>
              )}

              {audit && (
                <div className="mt-2 bg-black/40 border border-white/5 rounded-sm p-4 flex items-center gap-5">
                  <div className="flex flex-col items-center pr-5 border-r border-white/10">
                    <span className={`font-mono text-3xl font-bold leading-none ${audit.score >= 85 ? 'text-[var(--color-success)]' : audit.score >= 70 ? 'text-[var(--color-gold)]' : 'text-[var(--color-danger)]'}`}>
                      {audit.score}
                    </span>
                  </div>
                  <div className="flex-1 font-mono text-[12px] text-[var(--color-steel)] leading-relaxed">
                    <span className="text-[var(--color-gold)] font-bold">ANALYSIS:</span> {audit.critique}
                  </div>
                </div>
              )}

              {refinedPrompt && (
                <div className="flex flex-col gap-2 mt-4">
                  <div className="flex items-center justify-between">
                    <div className="text-[10px] text-[var(--color-gold)] tracking-[0.2em] font-mono uppercase">[ 03 ] Refined Output</div>
                    <button 
                      onClick={() => copyToClipboard(refinedPrompt, "workspace")} 
                      className={`text-[10px] font-mono transition-colors ${copiedId === "workspace" ? "text-[var(--color-success)]" : "text-[var(--color-steel)] hover:text-white"}`}
                    >
                      {copiedId === "workspace" ? "[ COPIED ]" : "[ COPY ]"}
                    </button>
                  </div>
                  <textarea
                    readOnly
                    value={refinedPrompt}
                    className="w-full h-[400px] bg-black/60 border border-white/10 rounded-sm text-[var(--color-text-main)] text-[13px] p-5 font-mono focus:outline-none transition-all resize-none shadow-inner leading-relaxed"
                  />
                </div>
              )}
            </section>

            {/* RIGHT PANE: COGNITIVE MAP & SETTINGS */}
            <aside className="xl:col-span-1 flex flex-col gap-6 bg-black/40 border border-white/5 p-6 rounded-sm h-fit">
              <div className="flex items-center gap-2 border-b border-white/10 pb-4">
                <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-steel)]"></div>
                <h2 className="text-[11px] text-white tracking-[0.2em] font-mono uppercase">Control Matrix</h2>
              </div>

              <div className="flex flex-col gap-5">
                {/* Always Visible Controls */}
                <div className="flex flex-col gap-2">
                  <label className="text-[9px] text-[var(--color-steel)] tracking-[0.1em] font-mono uppercase">Target Architecture</label>
                  <select value={targetModel} onChange={(e) => setTargetModel(e.target.value)} className="w-full bg-black/60 border border-white/10 text-[var(--color-text-main)] text-xs p-2.5 rounded-sm font-mono focus:outline-none focus:border-[var(--color-gold)] transition-colors">
                    <option value="ChatGPT">ChatGPT (OpenAI)</option>
                    <option value="Claude">Claude (Anthropic)</option>
                    <option value="Midjourney">Midjourney (Visual)</option>
                  </select>
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-[9px] text-[var(--color-steel)] tracking-[0.1em] font-mono uppercase">Aesthetic Overlay</label>
                  <select value={aesthetic} onChange={(e) => setAesthetic(e.target.value)} className="w-full bg-black/60 border border-white/10 text-[var(--color-text-main)] text-xs p-2.5 rounded-sm font-mono focus:outline-none focus:border-[var(--color-gold)] transition-colors">
                    <option value="Default">System Default</option>
                    <option value="Tech-Noir">Tech-Noir / Moody</option>
                    <option value="Cinematic">Cinematic</option>
                    <option value="Minimalist">Minimalist</option>
                  </select>
                </div>

                <div className="border-t border-white/10 pt-4"></div>

                {/* DYNAMIC RENDER */}
                {targetModel === "Midjourney" ? (
                  <div className="flex flex-col gap-5 animate-in fade-in duration-300">
                    <div className="flex flex-col gap-2">
                      <label className="text-[9px] text-[var(--color-steel)] tracking-[0.1em] font-mono uppercase">Aspect Ratio</label>
                      <select value={aspectRatio} onChange={(e) => setAspectRatio(e.target.value)} className="w-full bg-black/60 border border-white/10 text-[var(--color-text-main)] text-xs p-2.5 rounded-sm font-mono focus:outline-none focus:border-[var(--color-gold)]">
                        <option value="--ar 16:9">Cinematic Wide (16:9)</option>
                        <option value="--ar 9:16">Vertical Portrait (9:16)</option>
                        <option value="--ar 1:1">Square Grid (1:1)</option>
                      </select>
                    </div>
                    <div className="flex flex-col gap-2">
                      <label className="text-[9px] text-[var(--color-steel)] tracking-[0.1em] font-mono uppercase">Camera Angle & Lens</label>
                      <select value={camera} onChange={(e) => setCamera(e.target.value)} className="w-full bg-black/60 border border-white/10 text-[var(--color-text-main)] text-xs p-2.5 rounded-sm font-mono focus:outline-none focus:border-[var(--color-gold)]">
                        <option value="Cinematic Wide Shot, 35mm lens">Wide / Environmental (35mm)</option>
                        <option value="Extreme Close-up, macro photography">Extreme Close-Up (Macro)</option>
                        <option value="Drone top-down view">Top-Down / Drone View</option>
                      </select>
                    </div>
                    <div className="flex flex-col gap-2">
                      <label className="text-[9px] text-[var(--color-steel)] tracking-[0.1em] font-mono uppercase">Lighting Rig</label>
                      <select value={lighting} onChange={(e) => setLighting(e.target.value)} className="w-full bg-black/60 border border-white/10 text-[var(--color-text-main)] text-xs p-2.5 rounded-sm font-mono focus:outline-none focus:border-[var(--color-gold)]">
                        <option value="Volumetric, moody atmosphere, god rays">Volumetric / God Rays</option>
                        <option value="Cyberpunk neon lighting, harsh contrast">Neon High-Contrast</option>
                        <option value="Chiaroscuro, deep cinematic shadows">Chiaroscuro (Deep Shadows)</option>
                      </select>
                    </div>
                    <div className="flex flex-col gap-2">
                      <label className="text-[9px] text-[var(--color-steel)] tracking-[0.1em] font-mono uppercase">Film Stock & Texture</label>
                      <select value={filmStock} onChange={(e) => setFilmStock(e.target.value)} className="w-full bg-black/60 border border-white/10 text-[var(--color-text-main)] text-xs p-2.5 rounded-sm font-mono focus:outline-none focus:border-[var(--color-gold)]">
                        <option value="Cinestill 800T, high grain, cinematic">Cinestill 800T (Night/Tungsten)</option>
                        <option value="Kodak Portra 400, warm vintage feel">Kodak Portra 400 (Warm/Day)</option>
                        <option value="Crisp 8k digital rendering, hyper-detailed">8K Digital (Hyper-Realistic)</option>
                      </select>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col gap-5 animate-in fade-in duration-300">
                    <div className="flex flex-col gap-2">
                      <div className="flex justify-between items-end">
                        <label className="text-[9px] text-[var(--color-steel)] tracking-[0.1em] font-mono uppercase">Rhetoric Profile</label>
                        <span className="text-[9px] text-[var(--color-text-dim)] font-arabic">البلاغة</span>
                      </div>
                      <select value={hikmahStyle} onChange={(e) => setHikmahStyle(e.target.value)} className="w-full bg-black/60 border border-white/10 text-[var(--color-text-main)] text-xs p-2.5 rounded-sm font-mono focus:outline-none focus:border-[var(--color-gold)]">
                        <option value="None">Standard Integration</option>
                        <option value="Academic (Tahqiq)">Academic (Tahqiq)</option>
                        <option value="Classical Adab (Badi')">Classical Adab (Badi')</option>
                        <option value="Technical (Bayan)">Technical (Bayan)</option>
                      </select>
                    </div>
                    <div className="flex flex-col gap-2">
                      <div className="flex justify-between items-end">
                        <label className="text-[9px] text-[var(--color-steel)] tracking-[0.1em] font-mono uppercase">Framework</label>
                        <span className="text-[9px] text-[var(--color-text-dim)] font-arabic">الإطار</span>
                      </div>
                      <select value={framework} onChange={(e) => setFramework(e.target.value)} className="w-full bg-black/60 border border-white/10 text-[var(--color-text-main)] text-xs p-2.5 rounded-sm font-mono focus:outline-none focus:border-[var(--color-gold)]">
                        <option value="Professional (RACE)">Professional (RACE)</option>
                        <option value="Zero-Shot (Direct)">Zero-Shot (Direct)</option>
                        <option value="Chain of Thought">Chain of Thought</option>
                      </select>
                    </div>
                    <div className="flex flex-col gap-2">
                      <label className="text-[9px] text-[var(--color-steel)] tracking-[0.1em] font-mono uppercase">Output Language</label>
                      <select value={sourceLang} onChange={(e) => setSourceLang(e.target.value)} className="w-full bg-black/60 border border-white/10 text-[var(--color-text-main)] text-xs p-2.5 rounded-sm font-mono focus:outline-none focus:border-[var(--color-gold)]">
                        <option value="English">English</option>
                        <option value="Arabic">Arabic (العربية)</option>
                      </select>
                    </div>
                  </div>
                )}
              </div>
            </aside>
          </div>
        )}

        {/* VIEW: ARCHIVE */}
        {activeTab === "archive" && (
          <section className="flex flex-col gap-4 animate-in fade-in duration-500 max-w-5xl mx-auto">
            <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-4">
              <div className="flex items-center gap-3">
                <span className="text-[16px] text-[var(--color-gold)] leading-none">≡</span>
                <h2 className="text-[14px] text-white tracking-[0.2em] font-mono uppercase">Memory Banks</h2>
              </div>
              <button onClick={fetchArchive} className="text-[10px] font-mono text-[var(--color-gold)] hover:text-white transition-colors border border-[var(--color-gold)]/30 px-3 py-1 rounded-sm">
                [ REFRESH DATA ]
              </button>
            </div>

            {isArchiveLoading ? (
              <div className="text-[11px] font-mono text-[var(--color-steel)] animate-pulse p-4 bg-black/40 border border-white/5 rounded-sm">Decrypting memory banks from Supabase...</div>
            ) : archiveItems.length === 0 ? (
              <div className="text-[11px] font-mono text-[var(--color-text-dim)] p-4 bg-black/40 border border-white/5 rounded-sm">No operational records found in the vault.</div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {archiveItems.map((item, idx) => {
                  const textToCopy = item.content || item.refined_prompt || "ERROR: Could not locate text.";
                  const displayIntent = item.intent || item.title || "No original intent recorded.";
                  const targetModel = item.target || item.target_model || "ChatGPT";

                  return (
                    <div key={idx} className="bg-black/60 border border-white/10 rounded-sm p-6 flex flex-col gap-4 hover:border-white/30 transition-all shadow-md">
                      <div className="flex justify-between items-start">
                        <span className="text-[10px] font-mono text-[var(--color-gold)] border border-[var(--color-gold)]/20 px-3 py-1 rounded-sm shadow-inner">
                          {targetModel}
                        </span>
                        <button 
                          onClick={() => copyToClipboard(textToCopy, `archive-${idx}`)} 
                          className={`text-[10px] font-mono transition-colors ${copiedId === `archive-${idx}` ? "text-[var(--color-success)]" : "text-[var(--color-steel)] hover:text-white"}`}
                        >
                          {copiedId === `archive-${idx}` ? "[ COPIED ]" : "[ EXTRACT PAYLOAD ]"}
                        </button>
                      </div>
                      
                      <div className="border-t border-white/5 pt-3">
                        <div className="text-[9px] text-[var(--color-text-dim)] font-mono uppercase mb-2">Original Protocol Intent:</div>
                        <p className="text-[13px] text-[var(--color-steel)] line-clamp-3 leading-relaxed">{displayIntent}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        )}

        {/* VIEW: SYSTEM PROFILE */}
        {activeTab === "profile" && (
          <section className="flex flex-col gap-6 animate-in fade-in duration-500 max-w-3xl mx-auto">
            <div className="flex items-center gap-3 border-b border-white/10 pb-4 mb-4">
              <span className="text-[16px] text-[var(--color-gold)] leading-none">👤</span>
              <h2 className="text-[14px] text-white tracking-[0.2em] font-mono uppercase">Operator Credentials</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Identity Card */}
              <div className="bg-black/60 border border-white/10 rounded-sm p-6 flex flex-col gap-6 shadow-lg">
                <div className="flex flex-col gap-1">
                  <span className="text-[9px] text-[var(--color-steel)] tracking-[0.2em] font-mono uppercase">System ID</span>
                  <span className="text-xl text-white font-mono">{userHash}</span>
                </div>
                
                <div className="grid grid-cols-2 gap-4 border-t border-white/5 pt-4">
                  <div className="flex flex-col gap-1">
                    <span className="text-[9px] text-[var(--color-steel)] tracking-[0.2em] font-mono uppercase">Clearance</span>
                    <span className="text-xs text-[var(--color-gold)] font-mono">Level 4 (Admin)</span>
                  </div>
                  <div className="flex flex-col gap-1">
                    <span className="text-[9px] text-[var(--color-steel)] tracking-[0.2em] font-mono uppercase">Status</span>
                    <span className="text-xs text-[var(--color-success)] font-mono animate-pulse">Uplink Active</span>
                  </div>
                </div>
              </div>

              {/* DNA Readout */}
              <div className="bg-black/60 border border-white/10 rounded-sm p-6 flex flex-col justify-between shadow-lg">
                 <div>
                   <div className="text-[9px] text-[var(--color-steel)] tracking-[0.2em] font-mono uppercase mb-4">Brand DNA Integration</div>
                   <div className="text-2xl text-white font-arabic mb-2 text-right">حبر وفكرة</div>
                   <p className="text-[11px] text-[var(--color-steel)] font-mono leading-relaxed text-right">
                     InkOS Architecture v2.0 <br/>
                     Web Dev | Cybersecurity | AI Mod
                   </p>
                 </div>
                 <div className="border-t border-white/5 pt-4 mt-4">
                    <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                       <div className="bg-[var(--color-gold)] w-[100%] h-full shadow-[0_0_10px_var(--color-gold)]"></div>
                    </div>
                    <div className="text-[8px] text-[var(--color-steel)] tracking-[0.2em] font-mono uppercase mt-2 text-right">DNA Synced</div>
                 </div>
              </div>
            </div>
          </section>
        )}

      </main>
    </div>
  );
}
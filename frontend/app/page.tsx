"use client";

import { useState } from "react";

export default function Workspace() {
  const [intent, setIntent] = useState("");
  const [targetModel, setTargetModel] = useState("ChatGPT");
  const [refinedPrompt, setRefinedPrompt] = useState("");
  const [audit, setAudit] = useState<{ score: number; critique: string; precision?: number; alignment?: number; efficiency?: number } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleRefine = async () => {
    if (!intent.trim()) return;
    
    setIsLoading(true);
    setError("");
    setRefinedPrompt("");
    setAudit(null);

    try {
      const response = await fetch("http://localhost:8000/api/refine", {
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
        }),
      });

      if (!response.ok) {
        throw new Error(`Server Fault: ${response.status}`);
      }

      const data = await response.json();
      setRefinedPrompt(data.refined_prompt);
      setAudit(data.audit);
    } catch (err: any) {
      setError(err.message || "Failed to establish uplink with the CIPHER engine.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-6 md:p-12 max-w-5xl mx-auto flex flex-col gap-6">
      {/* Header */}
      <header className="flex items-center gap-3 border-b border-gold/30 pb-3 mb-4">
        <div className="w-2 h-2 rounded-full bg-gold shadow-[0_0_6px_var(--gold)] shrink-0"></div>
        <h1 className="text-gold tracking-[0.2em] text-xs font-mono uppercase">Workspace</h1>
        <span className="ml-auto text-[10px] text-text-dim tracking-widest font-arabic">مساحة العمل</span>
      </header>

      {/* Input Section */}
      <section className="flex flex-col gap-2">
        <div className="text-[10px] text-text-dim tracking-[0.2em] font-mono uppercase">
          [ 01 ] Source Intent
        </div>
        <textarea
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          placeholder="Describe what you want the AI to do..."
          className="w-full h-48 bg-black/30 border border-white/5 rounded-sm text-text-main text-sm p-4 font-mono focus:outline-none focus:border-gold focus:ring-1 focus:ring-gold/20 transition-all resize-none"
        />
        
        <div className="flex justify-between items-center mt-2">
          <select 
            value={targetModel}
            onChange={(e) => setTargetModel(e.target.value)}
            className="bg-input border border-white/5 text-text-main text-xs p-2 rounded-sm font-mono focus:outline-none focus:border-gold"
          >
            <option value="ChatGPT">ChatGPT</option>
            <option value="Claude">Claude</option>
            <option value="Midjourney">Midjourney</option>
            <option value="DALL-E 3">DALL-E 3</option>
          </select>

          <button
            onClick={handleRefine}
            disabled={isLoading || !intent.trim()}
            className="bg-gold text-black px-8 py-2.5 text-[11px] font-mono font-bold tracking-[0.15em] uppercase rounded-sm hover:bg-[#E2D5BC] hover:shadow-[0_0_15px_rgba(201,168,76,0.4)] hover:-translate-y-[1px] transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-none"
          >
            {isLoading ? "Compiling..." : "⚡ Refine"}
          </button>
        </div>
      </section>

      {/* Error State */}
      {error && (
        <div className="bg-black/40 border border-border-subtle rounded-sm p-4 text-xs font-mono text-danger">
          System Fault: {error}
        </div>
      )}

      {/* Output Section */}
      <section className="flex flex-col gap-3 mt-4">
        <div className="flex items-center gap-2 mb-2">
          <div className="text-[10px] text-gold tracking-[0.2em] font-mono uppercase">
            [ 03 ] Refined Output
          </div>
          <div className="flex-1 h-[1px] bg-gradient-to-r from-gold/30 to-transparent"></div>
        </div>

        {!refinedPrompt && !isLoading && !error && (
          <div className="border border-dashed border-white/5 rounded-md p-10 text-center flex flex-col gap-2">
            <span className="text-[11px] text-text-dim tracking-widest font-mono uppercase">
              [ ❖ ] Compiled prompt will appear here
            </span>
          </div>
        )}

        {audit && (
          <div className="bg-black/30 border border-white/5 rounded-sm p-3 mb-2 flex items-center gap-4 flex-wrap">
            <div className="flex flex-col items-center pr-4 border-r border-white/5">
              <span className={`font-mono text-2xl font-bold leading-none ${audit.score >= 85 ? 'text-success' : audit.score >= 70 ? 'text-gold' : 'text-danger'}`}>
                {audit.score}
              </span>
              <span className={`font-mono text-[8px] tracking-[0.15em] mt-1 ${audit.score >= 85 ? 'text-success' : audit.score >= 70 ? 'text-gold' : 'text-danger'}`}>
                {audit.score >= 85 ? 'HIGH FIDELITY' : audit.score >= 70 ? 'ACCEPTABLE' : 'NEEDS WORK'}
              </span>
            </div>
            <div className="flex-1 font-mono text-[11px] text-steel italic px-2">
              ✦ {audit.critique}
            </div>
          </div>
        )}

        {refinedPrompt && (
          <textarea
            readOnly
            value={refinedPrompt}
            className="w-full h-80 bg-black/40 border border-white/5 rounded-sm text-text-main text-[13px] p-4 font-mono focus:outline-none focus:border-gold transition-all resize-none"
          />
        )}
      </section>
    </main>
  );
}
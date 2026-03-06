import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence, useAnimation } from "framer-motion";
import {
  Phone, PhoneOff, Play, Pause, ChevronDown, ChevronUp,
  Building2, Target, Users, TrendingUp, Mic, MicOff,
  Calendar, Clock, AlertCircle, CheckCircle2, XCircle,
  Flame, Wifi, Settings, Bell, BarChart3, Home, Zap,
  PhoneCall, Brain, Star, MapPin
} from "lucide-react";

// ─── Seed Data ───────────────────────────────────────────────────────────────
const INITIAL_CALLS = [
  {
    id: 1, name: "Arjun Mehta", phone: "+91 98765 43210",
    status: "success", duration: "4:32", sentiment: 82, hotness: 8,
    followUp: "Mar 10, 2026", objections: "Price too high, wants ground floor",
    siteVisit: true, time: "10:14 AM",
    summary: "Arjun is a serious buyer with budget flexibility. He expressed strong interest in the 3BHK unit on Block C. Main friction is the asking price — he wants a ₹5L reduction. Recommend scheduling a site visit and introducing the payment plan.",
    transcript: "Monika: Good morning Arjun, I'm calling from Elite Estate regarding the Prestige Towers project...\nArjun: Yes, I've been looking at 3BHK options. What's the final price?\nMonika: The unit starts at ₹1.2 Cr. We have flexible EMI options...\nArjun: That's a bit over my budget. Can we negotiate?\nMonika: I'll escalate to our sales manager. Can I schedule a visit?"
  },
  {
    id: 2, name: "Priya Sharma", phone: "+91 87654 32109",
    status: "success", duration: "3:15", sentiment: 71, hotness: 6,
    followUp: "Mar 12, 2026", objections: "Needs husband's approval, school proximity concern",
    siteVisit: false, time: "10:47 AM",
    summary: "Priya is interested but a joint decision-maker. Her primary concern is proximity to schools for her 2 children. The upcoming school partnership announcement may convert her. Flag for follow-up post the announcement.",
    transcript: "Monika: Hi Priya, calling about the 2BHK units at Prestige Towers...\nPriya: I'm interested but need to discuss with my husband.\nMonika: Of course. Is there anything specific I can address for you today?\nPriya: The schools nearby — my kids are in primary school...\nMonika: We have DPS and Ryan International within 2km. Shall I send the details?"
  },
  {
    id: 3, name: "Vikram Nair", phone: "+91 76543 21098",
    status: "failed", duration: "0:18", sentiment: 30, hotness: 2,
    followUp: "Mar 15, 2026", objections: "Not interested, already purchased elsewhere",
    siteVisit: false, time: "11:02 AM",
    summary: "Vikram has already closed a deal with a competitor. He was polite but firm. Remove from active pipeline. Archive contact for future projects.",
    transcript: "Monika: Good morning Vikram...\nVikram: I've already bought a flat. Not interested. Please don't call again.\nMonika: Understood, I'll update our records. Thank you for your time."
  },
  {
    id: 4, name: "Sunita Reddy", phone: "+91 65432 10987",
    status: "success", duration: "6:48", sentiment: 91, hotness: 9,
    followUp: "Mar 08, 2026", objections: "Wants dedicated parking, corner unit preference",
    siteVisit: true, time: "11:30 AM",
    summary: "Sunita is a hot lead — she's been researching for 6 months and is ready to commit. She specifically wants a corner unit with dual parking. Two units match her criteria. Priority: book a site visit this weekend before she looks elsewhere.",
    transcript: "Monika: Hi Sunita, this is Monika from Elite Estate...\nSunita: Oh perfect timing! I was just about to call you.\nMonika: We have two corner units matching your brief. Both have dedicated parking.\nSunita: Send me the floor plans. When can I visit the site?\nMonika: This Saturday works — I'll have our senior consultant available exclusively for you."
  }
];

const PROPERTY_OPTIONS = ["2 BHK - Prestige Towers, Whitefield (₹78L)", "3 BHK - Prestige Towers, Whitefield (₹1.2Cr)", "3 BHK - Elite Heights, Koramangala (₹1.8Cr)", "4 BHK Penthouse - Sky Villas, Indiranagar (₹3.2Cr)"];
const GOAL_OPTIONS = ["Site Visit Booking", "Lead Generation", "Follow-up & Nurture", "Closing Conversion"];

// ─── Waveform Component ───────────────────────────────────────────────────────
const WaveVisualizer = ({ active }) => {
  const bars = Array.from({ length: 40 });
  return (
    <div className="flex items-center justify-center gap-[3px] h-20 w-full">
      {bars.map((_, i) => (
        <motion.div
          key={i}
          className="rounded-full"
          style={{
            width: 3,
            background: active
              ? `linear-gradient(to top, #D97706, #FCD34D)`
              : "#1e293b",
          }}
          animate={active ? {
            height: [8, Math.random() * 50 + 10, 8, Math.random() * 40 + 6, 8],
            opacity: [0.5, 1, 0.7, 1, 0.5],
          } : { height: 4, opacity: 0.2 }}
          transition={active ? {
            duration: 1.2 + Math.random() * 0.8,
            repeat: Infinity,
            delay: i * 0.04,
            ease: "easeInOut",
          } : { duration: 0.5 }}
        />
      ))}
    </div>
  );
};

// ─── Sentiment Badge ──────────────────────────────────────────────────────────
const SentimentBar = ({ score }) => {
  const color = score >= 75 ? "#10b981" : score >= 50 ? "#f59e0b" : "#ef4444";
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-slate-700 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className="h-full rounded-full"
          style={{ background: color }}
        />
      </div>
      <span className="text-xs font-mono" style={{ color }}>{score}%</span>
    </div>
  );
};

// ─── Hotness Dots ─────────────────────────────────────────────────────────────
const HotnessMeter = ({ score }) => (
  <div className="flex gap-1">
    {Array.from({ length: 10 }).map((_, i) => (
      <motion.div
        key={i}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: i * 0.05 }}
        className="w-2 h-2 rounded-full"
        style={{
          background: i < score
            ? i >= 7 ? "#ef4444" : i >= 4 ? "#f59e0b" : "#10b981"
            : "#1e293b",
          boxShadow: i < score && i >= 7 ? "0 0 4px #ef4444" : "none"
        }}
      />
    ))}
  </div>
);

// ─── Call Card ────────────────────────────────────────────────────────────────
const CallCard = ({ call, index }) => {
  const [expanded, setExpanded] = useState(false);
  const [playing, setPlaying] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      className="rounded-xl overflow-hidden border border-slate-700/50"
      style={{ background: "rgba(15,23,42,0.8)" }}
    >
      <div
        className="p-4 cursor-pointer hover:bg-slate-800/40 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Avatar Circle */}
            <div className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold border"
              style={{
                background: call.status === "success"
                  ? "rgba(16,185,129,0.15)" : "rgba(239,68,68,0.15)",
                borderColor: call.status === "success" ? "#10b981" : "#ef4444",
                color: call.status === "success" ? "#10b981" : "#ef4444"
              }}>
              {call.name.split(" ").map(n => n[0]).join("")}
            </div>
            <div>
              <p className="text-white font-semibold text-sm">{call.name}</p>
              <p className="text-slate-400 text-xs">{call.phone} · {call.time}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {/* Status badge */}
            <span className="px-2 py-0.5 rounded-full text-xs font-medium flex items-center gap-1"
              style={{
                background: call.status === "success" ? "rgba(16,185,129,0.15)" : "rgba(239,68,68,0.15)",
                color: call.status === "success" ? "#10b981" : "#ef4444"
              }}>
              {call.status === "success" ? <CheckCircle2 size={10} /> : <XCircle size={10} />}
              {call.status === "success" ? "Success" : "Failed"}
            </span>
            <span className="text-slate-400 text-xs flex items-center gap-1">
              <Clock size={10} />{call.duration}
            </span>
            {/* Site Visit */}
            {call.siteVisit && (
              <span className="px-2 py-0.5 rounded-full text-xs font-medium"
                style={{ background: "rgba(245,158,11,0.15)", color: "#fbbf24" }}>
                🏠 Site Visit
              </span>
            )}
            <motion.div animate={{ rotate: expanded ? 180 : 0 }}>
              <ChevronDown size={14} className="text-slate-500" />
            </motion.div>
          </div>
        </div>

        {/* Quick stats row */}
        <div className="mt-3 grid grid-cols-3 gap-3">
          <div>
            <p className="text-slate-500 text-xs mb-1">Sentiment</p>
            <SentimentBar score={call.sentiment} />
          </div>
          <div>
            <p className="text-slate-500 text-xs mb-1">Lead Hotness</p>
            <HotnessMeter score={call.hotness} />
          </div>
          <div>
            <p className="text-slate-500 text-xs mb-1">Follow-up</p>
            <p className="text-amber-400 text-xs flex items-center gap-1">
              <Calendar size={10} />{call.followUp}
            </p>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 border-t border-slate-700/50 pt-4 space-y-4">
              {/* AI Summary */}
              <div className="rounded-lg p-3" style={{ background: "rgba(245,158,11,0.05)", border: "1px solid rgba(245,158,11,0.2)" }}>
                <div className="flex items-center gap-2 mb-2">
                  <Brain size={12} className="text-amber-400" />
                  <span className="text-amber-400 text-xs font-semibold uppercase tracking-widest">AI Summary</span>
                </div>
                <p className="text-slate-300 text-sm leading-relaxed">{call.summary}</p>
              </div>

              {/* Objections */}
              <div>
                <p className="text-slate-500 text-xs uppercase tracking-widest mb-1">Customer Objections</p>
                <p className="text-slate-300 text-sm flex items-start gap-2">
                  <AlertCircle size={12} className="text-amber-500 mt-0.5 shrink-0" />
                  {call.objections}
                </p>
              </div>

              {/* Transcript */}
              <div>
                <p className="text-slate-500 text-xs uppercase tracking-widest mb-2">Transcript Snippet</p>
                <div className="rounded-lg p-3 font-mono text-xs text-slate-400 leading-relaxed max-h-28 overflow-y-auto"
                  style={{ background: "rgba(0,0,0,0.4)" }}>
                  {call.transcript.split("\n").map((line, i) => (
                    <p key={i} className={line.startsWith("Monika") ? "text-amber-400/80" : "text-slate-300"}>{line}</p>
                  ))}
                </div>
              </div>

              {/* Recording */}
              <div className="flex items-center gap-3">
                <button
                  onClick={(e) => { e.stopPropagation(); setPlaying(!playing); }}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all"
                  style={{
                    background: playing ? "rgba(239,68,68,0.15)" : "rgba(245,158,11,0.15)",
                    border: `1px solid ${playing ? "#ef4444" : "#f59e0b"}`,
                    color: playing ? "#ef4444" : "#f59e0b"
                  }}
                >
                  {playing ? <><Pause size={12} /> Stop Playback</> : <><Play size={12} /> Play Recording</>}
                </button>
                {playing && (
                  <motion.div className="flex gap-0.5 items-center" animate={{ opacity: [1, 0.5, 1] }} transition={{ repeat: Infinity, duration: 1 }}>
                    {[...Array(6)].map((_, i) => (
                      <motion.div key={i} className="w-0.5 rounded-full bg-amber-400"
                        animate={{ height: [4, 12 + i * 2, 4] }}
                        transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.1 }} />
                    ))}
                  </motion.div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

// ─── Main Dashboard ───────────────────────────────────────────────────────────
export default function MonikaDashboard() {
  const [campaignActive, setCampaignActive] = useState(false);
  const [calls, setCalls] = useState(INITIAL_CALLS.slice(0, 0));
  const [callQueue, setCallQueue] = useState([...INITIAL_CALLS]);
  const [activeTab, setActiveTab] = useState("campaign");
  const [numbers, setNumbers] = useState("+91 98765 43210\n+91 87654 32109\n+91 76543 21098\n+91 65432 10987");
  const [property, setProperty] = useState(PROPERTY_OPTIONS[1]);
  const [goal, setGoal] = useState(GOAL_OPTIONS[0]);
  const [currentCall, setCurrentCall] = useState(null);
  const [callProgress, setCallProgress] = useState(0);
  const timerRef = useRef(null);
  const callIndexRef = useRef(0);

  const stats = {
    total: calls.length,
    success: calls.filter(c => c.status === "success").length,
    siteVisits: calls.filter(c => c.siteVisit).length,
    avgHotness: calls.length ? (calls.reduce((a, b) => a + b.hotness, 0) / calls.length).toFixed(1) : 0
  };

  useEffect(() => {
    if (!campaignActive) return;

    const runNextCall = () => {
      if (callIndexRef.current >= INITIAL_CALLS.length) {
        setCampaignActive(false);
        setCurrentCall(null);
        return;
      }

      const next = INITIAL_CALLS[callIndexRef.current];
      setCurrentCall(next);
      setCallProgress(0);

      let prog = 0;
      const progTimer = setInterval(() => {
        prog += 2;
        setCallProgress(prog);
        if (prog >= 100) {
          clearInterval(progTimer);
          setCalls(prev => [next, ...prev]);
          setCurrentCall(null);
          callIndexRef.current++;
          setTimeout(runNextCall, 1500);
        }
      }, 80);
    };

    callIndexRef.current = 0;
    setCalls([]);
    setTimeout(runNextCall, 800);

    return () => clearInterval(timerRef.current);
  }, [campaignActive]);

  const navItems = [
    { icon: Home, label: "Dashboard", id: "dashboard" },
    { icon: PhoneCall, label: "Campaign", id: "campaign" },
    { icon: BarChart3, label: "Analytics", id: "analytics" },
    { icon: Users, label: "Contacts", id: "contacts" },
    { icon: Settings, label: "Settings", id: "settings" },
  ];

  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
        ::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 2px; }
        .gold-glow { box-shadow: 0 0 30px rgba(245,158,11,0.3), 0 0 60px rgba(245,158,11,0.1); }
        .gold-border { border: 1px solid rgba(245,158,11,0.3); }
        .glass { background: rgba(15,23,42,0.6); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.06); }
        .stat-card { background: linear-gradient(135deg, rgba(30,41,59,0.8), rgba(15,23,42,0.8)); border: 1px solid rgba(255,255,255,0.06); }
      `}</style>

      {/* ── Left Sidebar ── */}
      <div className="w-64 flex flex-col border-r border-slate-800/50 shrink-0"
        style={{ background: "rgba(8,12,24,0.95)" }}>

        {/* Logo */}
        <div className="px-5 py-5 border-b border-slate-800/50">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center"
              style={{ background: "linear-gradient(135deg, #D97706, #92400e)" }}>
              <Building2 size={14} className="text-white" />
            </div>
            <div>
              <p className="text-white text-sm font-semibold" style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: 16 }}>Elite Estate</p>
              <p className="text-amber-500/60 text-xs tracking-widest uppercase" style={{ fontSize: 9 }}>AI Sales Platform</p>
            </div>
          </div>
        </div>

        {/* Monika Card */}
        <div className="p-4">
          <motion.div
            animate={campaignActive ? {
              boxShadow: ["0 0 20px rgba(245,158,11,0.2)", "0 0 50px rgba(245,158,11,0.5)", "0 0 20px rgba(245,158,11,0.2)"],
            } : { boxShadow: "0 0 0px rgba(245,158,11,0)" }}
            transition={{ duration: 2, repeat: Infinity }}
            className="rounded-2xl overflow-hidden"
            style={{ border: "1px solid rgba(245,158,11,0.2)" }}
          >
            {/* Avatar area */}
            <div className="relative h-52" style={{
              background: "linear-gradient(160deg, #0f172a 0%, #1c1200 60%, #0f172a 100%)"
            }}>
              {/* Decorative rings */}
              <div className="absolute inset-0 flex items-center justify-center">
                {[1, 2, 3].map(i => (
                  <motion.div key={i}
                    className="absolute rounded-full border"
                    style={{
                      width: 60 + i * 28, height: 60 + i * 28,
                      borderColor: `rgba(245,158,11,${0.12 - i * 0.03})`
                    }}
                    animate={campaignActive ? { scale: [1, 1.05, 1], opacity: [0.5, 1, 0.5] } : {}}
                    transition={{ duration: 2 + i, repeat: Infinity, delay: i * 0.3 }}
                  />
                ))}
              </div>

              {/* AI Avatar Face */}
              <div className="absolute inset-0 flex items-center justify-center">
                <motion.div
                  animate={campaignActive ? { scale: [1, 1.03, 1] } : {}}
                  transition={{ duration: 3, repeat: Infinity }}
                  className="w-24 h-24 rounded-full flex items-center justify-center text-4xl relative"
                  style={{
                    background: "linear-gradient(135deg, #92400e, #D97706, #fbbf24)",
                    boxShadow: campaignActive ? "0 0 30px rgba(245,158,11,0.6)" : "0 0 15px rgba(245,158,11,0.2)"
                  }}
                >
                  <span style={{ fontSize: 38 }}>👩‍💼</span>
                  {campaignActive && (
                    <motion.div className="absolute inset-0 rounded-full"
                      style={{ border: "2px solid #fbbf24" }}
                      animate={{ scale: [1, 1.2, 1], opacity: [1, 0, 1] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    />
                  )}
                </motion.div>
              </div>

              {/* Status pill */}
              <div className="absolute bottom-3 left-1/2 -translate-x-1/2">
                <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs"
                  style={{ background: "rgba(0,0,0,0.6)", border: "1px solid rgba(16,185,129,0.3)" }}>
                  <motion.div className="w-1.5 h-1.5 rounded-full bg-emerald-400"
                    animate={{ opacity: [1, 0.3, 1] }} transition={{ duration: 1.5, repeat: Infinity }} />
                  <span className="text-emerald-400 font-medium">
                    {campaignActive ? "On Call" : "Online"}
                  </span>
                </div>
              </div>
            </div>

            <div className="p-3 text-center" style={{ background: "rgba(10,15,30,0.9)" }}>
              <p className="text-white font-semibold" style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: 17 }}>Monika AI</p>
              <p className="text-amber-500/70 text-xs">Senior Sales Consultant</p>
              <div className="flex justify-center gap-3 mt-2 text-xs text-slate-400">
                <span>📞 {stats.total} calls</span>
                <span>✓ {stats.success} closed</span>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 space-y-1">
          {navItems.map(({ icon: Icon, label, id }) => (
            <button key={id} onClick={() => setActiveTab(id)}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all"
              style={{
                background: activeTab === id ? "rgba(245,158,11,0.1)" : "transparent",
                color: activeTab === id ? "#fbbf24" : "#64748b",
                border: activeTab === id ? "1px solid rgba(245,158,11,0.2)" : "1px solid transparent"
              }}>
              <Icon size={15} />
              {label}
              {id === "campaign" && calls.length > 0 && (
                <span className="ml-auto text-xs px-1.5 py-0.5 rounded-full"
                  style={{ background: "rgba(245,158,11,0.2)", color: "#fbbf24" }}>
                  {calls.length}
                </span>
              )}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-800/50">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>v2.4.1</span>
            <span className="text-amber-500/60">Elite License</span>
          </div>
        </div>
      </div>

      {/* ── Main Content ── */}
      <div className="flex-1 flex flex-col overflow-hidden">

        {/* Top Bar */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800/50 shrink-0"
          style={{ background: "rgba(8,12,24,0.8)" }}>
          <div>
            <h1 className="text-white font-semibold" style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: 22 }}>
              AI Sales Command Center
            </h1>
            <p className="text-slate-500 text-xs">Prestige Towers Campaign · Whitefield, Bengaluru</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg" style={{ background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)" }}>
              <Wifi size={12} className="text-emerald-400" />
              <span className="text-emerald-400 text-xs">Live</span>
            </div>
            <button className="p-2 rounded-lg text-slate-400 hover:text-white transition-colors" style={{ background: "rgba(30,41,59,0.5)" }}>
              <Bell size={16} />
            </button>
          </div>
        </div>

        {/* Stat Row */}
        <div className="grid grid-cols-4 gap-4 px-6 py-4 shrink-0">
          {[
            { label: "Calls Made", value: stats.total, icon: Phone, color: "#60a5fa" },
            { label: "Successful", value: stats.success, icon: CheckCircle2, color: "#10b981" },
            { label: "Site Visits", value: stats.siteVisits, icon: MapPin, color: "#f59e0b" },
            { label: "Avg Hotness", value: stats.avgHotness, icon: Flame, color: "#ef4444" }
          ].map((s, i) => (
            <motion.div key={i}
              className="stat-card rounded-xl p-4"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <div className="flex items-center justify-between mb-2">
                <p className="text-slate-400 text-xs uppercase tracking-wider">{s.label}</p>
                <s.icon size={14} style={{ color: s.color }} />
              </div>
              <motion.p className="text-2xl font-bold text-white"
                key={s.value}
                initial={{ scale: 1.2 }}
                animate={{ scale: 1 }}
                style={{ fontFamily: "'DM Mono', monospace" }}>
                {s.value}
              </motion.p>
            </motion.div>
          ))}
        </div>

        {/* Main 2-col layout */}
        <div className="flex-1 grid grid-cols-2 gap-4 px-6 pb-5 overflow-hidden min-h-0">

          {/* Left: Config + Visualizer */}
          <div className="flex flex-col gap-4 overflow-y-auto">

            {/* Campaign Config */}
            <div className="glass rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <Target size={14} className="text-amber-400" />
                <h2 className="text-white font-semibold" style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: 17 }}>
                  Campaign Setup
                </h2>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-slate-400 text-xs uppercase tracking-widest mb-1.5">Call List</label>
                  <textarea
                    value={numbers}
                    onChange={e => setNumbers(e.target.value)}
                    rows={3}
                    className="w-full text-xs text-slate-200 rounded-xl px-3 py-2.5 resize-none focus:outline-none font-mono"
                    style={{ background: "rgba(0,0,0,0.4)", border: "1px solid rgba(245,158,11,0.25)", lineHeight: 1.7 }}
                    placeholder="One number per line..."
                  />
                </div>

                <div>
                  <label className="block text-slate-400 text-xs uppercase tracking-widest mb-1.5">Property</label>
                  <select
                    value={property}
                    onChange={e => setProperty(e.target.value)}
                    className="w-full text-xs text-slate-200 rounded-xl px-3 py-2.5 focus:outline-none appearance-none"
                    style={{ background: "rgba(0,0,0,0.4)", border: "1px solid rgba(245,158,11,0.25)" }}
                  >
                    {PROPERTY_OPTIONS.map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 text-xs uppercase tracking-widest mb-1.5">Sales Goal</label>
                  <select
                    value={goal}
                    onChange={e => setGoal(e.target.value)}
                    className="w-full text-xs text-slate-200 rounded-xl px-3 py-2.5 focus:outline-none appearance-none"
                    style={{ background: "rgba(0,0,0,0.4)", border: "1px solid rgba(245,158,11,0.25)" }}
                  >
                    {GOAL_OPTIONS.map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                </div>

                <motion.button
                  onClick={() => {
                    if (!campaignActive) {
                      callIndexRef.current = 0;
                      setCampaignActive(true);
                    } else {
                      setCampaignActive(false);
                      setCurrentCall(null);
                    }
                  }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full py-3 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-all"
                  style={campaignActive ? {
                    background: "rgba(239,68,68,0.15)",
                    border: "1px solid rgba(239,68,68,0.4)",
                    color: "#ef4444"
                  } : {
                    background: "linear-gradient(135deg, #D97706, #92400e)",
                    border: "none",
                    color: "white",
                    boxShadow: "0 4px 20px rgba(217,119,6,0.4)"
                  }}>
                  {campaignActive ? <><PhoneOff size={14} /> Stop Campaign</> : <><Zap size={14} /> Start Campaign</>}
                </motion.button>
              </div>
            </div>

            {/* Waveform Visualizer */}
            <div className="glass rounded-2xl p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Mic size={14} className="text-amber-400" />
                  <h2 className="text-white font-semibold" style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: 17 }}>
                    Voice Activity
                  </h2>
                </div>
                {currentCall && (
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-xs px-2 py-1 rounded-lg"
                    style={{ background: "rgba(245,158,11,0.1)", color: "#fbbf24", border: "1px solid rgba(245,158,11,0.2)" }}>
                    📞 {currentCall.name}
                  </motion.span>
                )}
              </div>

              <WaveVisualizer active={!!currentCall} />

              {currentCall && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mt-3"
                >
                  <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                    <span>Call Progress</span>
                    <span>{callProgress}%</span>
                  </div>
                  <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full rounded-full"
                      style={{
                        width: `${callProgress}%`,
                        background: "linear-gradient(to right, #D97706, #fbbf24)"
                      }}
                      transition={{ duration: 0.1 }}
                    />
                  </div>
                </motion.div>
              )}

              {!currentCall && !campaignActive && (
                <p className="text-center text-slate-600 text-xs mt-2">Start a campaign to activate</p>
              )}
              {!currentCall && campaignActive && (
                <motion.p className="text-center text-amber-500/60 text-xs mt-2"
                  animate={{ opacity: [0.5, 1, 0.5] }} transition={{ repeat: Infinity, duration: 1.5 }}>
                  Connecting next call...
                </motion.p>
              )}
            </div>
          </div>

          {/* Right: Call Intelligence */}
          <div className="flex flex-col overflow-hidden">
            <div className="flex items-center justify-between mb-3 shrink-0">
              <div className="flex items-center gap-2">
                <Brain size={14} className="text-amber-400" />
                <h2 className="text-white font-semibold" style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: 17 }}>
                  Recent Intelligence
                </h2>
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <TrendingUp size={12} />
                {calls.length} records
              </div>
            </div>

            <div className="flex-1 overflow-y-auto space-y-2 pr-1">
              <AnimatePresence>
                {calls.length === 0 ? (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex flex-col items-center justify-center h-full text-center"
                  >
                    <div className="w-16 h-16 rounded-full flex items-center justify-center mb-3"
                      style={{ background: "rgba(245,158,11,0.05)", border: "1px dashed rgba(245,158,11,0.2)" }}>
                      <PhoneCall size={24} className="text-amber-500/30" />
                    </div>
                    <p className="text-slate-500 text-sm">No calls yet</p>
                    <p className="text-slate-600 text-xs mt-1">Start a campaign to see intelligence</p>
                  </motion.div>
                ) : (
                  calls.map((call, i) => <CallCard key={call.id} call={call} index={i} />)
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

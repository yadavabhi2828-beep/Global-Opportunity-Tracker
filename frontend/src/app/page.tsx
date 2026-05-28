"use client";

import { useState, useEffect } from "react";
import { 
  Search, Compass, LayoutDashboard, MapPin, Clock, SlidersHorizontal, 
  Sparkles, RefreshCw, ExternalLink, Bookmark, CheckCircle2,
  FileText, Calendar, DollarSign, Award
} from "lucide-react";
import axios from "axios";
import Link from "next/link";

const API_BASE = "/api";
axios.defaults.headers.common['bypass-tunnel-reminder'] = 'true';
const FIXED_USER_ID = "00000000-0000-0000-0000-000000000000"; // Default user ID for testing

// Fallback items if API is not running
const MOCK_OPPORTUNITIES = [
  {
    id: "m-1",
    name: "Thiel Fellowship 2026",
    organization: "Thiel Foundation",
    description: "Two-year program for young people who want to build new things instead of sitting in a classroom. Offers funding and support to drop out of college.",
    url: "https://thielfellowship.org",
    category: "fellowship",
    tags: ["Founder", "Startup", "Tech"],
    country: ["Global"],
    remote: false,
    funding_amount: "$100,000 grant",
    deadline: "2026-08-31T00:00:00Z",
    eligibility_text: "Anyone under the age of 22 who wants to build a startup.",
    women_friendly: false,
    indian_eligible: true,
    student_eligible: true,
    ai_summary: "A world-renowned program giving founders $100K to skip college and focus entirely on constructing their ideas. Perfect for visionary builders under 22."
  },
  {
    id: "m-2",
    name: "Erasmus Mundus Joint Masters",
    organization: "European Union Council",
    description: "Fully funded scholarship for top-tier master programs in European universities. Includes tuition, health insurance, and monthly living stipends.",
    url: "https://erasmus-plus.ec.europa.eu",
    category: "scholarship",
    tags: ["Research", "Travel", "Student"],
    country: ["India", "Global", "Asia"],
    remote: false,
    funding_amount: "Fully Funded (Tuition + €1,400/month)",
    deadline: "2026-10-15T00:00:00Z",
    eligibility_text: "Undergraduate degree holders from any country globally.",
    women_friendly: true,
    indian_eligible: true,
    student_eligible: true,
    ai_summary: "Prestigious joint graduate scholarship program funded by the EU. Covers full tuition, travel costs, and provides a monthly allowance of €1,400."
  },
  {
    id: "m-3",
    name: "Y Combinator Summer 2026 Batch",
    organization: "Y Combinator",
    description: "Twice-yearly startup accelerator funding early-stage companies and providing elite founder networking, advisory, and demo-day visibility.",
    url: "https://ycombinator.com",
    category: "accelerator",
    tags: ["Startup", "Founder", "AI", "Engineering"],
    country: ["Global"],
    remote: true,
    funding_amount: "$500,000 investment",
    deadline: "2026-07-01T00:00:00Z",
    eligibility_text: "Early-stage startup teams in technology, software, climate, and biotechnology.",
    women_friendly: true,
    indian_eligible: true,
    student_eligible: false,
    ai_summary: "The world's premier startup accelerator. Invests $500k standard deal and provides invaluable mentorship, connections, and demo day exposure."
  },
  {
    id: "m-4",
    name: "Google AI Research Grant 2026",
    organization: "Google Research Labs",
    description: "Funding program supporting academic researchers focusing on artificial intelligence, machine learning, and ethics in AI applications.",
    url: "https://research.google",
    category: "grant",
    tags: ["AI", "Research", "Climate"],
    country: ["USA", "India", "UK", "Europe"],
    remote: true,
    funding_amount: "$50,000 funding",
    deadline: "2026-09-30T00:00:00Z",
    eligibility_text: "PhD candidates, faculty members, and research groups at accredited universities.",
    women_friendly: false,
    indian_eligible: true,
    student_eligible: true,
    ai_summary: "Google-sponsored grant intended to support breakthrough research in machine learning. Awards up to $50k with access to Google Cloud credits."
  }
];

export default function Home() {
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<string>("");
  const [country, setCountry] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [womenFriendlyOnly, setWomenFriendlyOnly] = useState(false);
  const [studentEligibleOnly, setStudentEligibleOnly] = useState(false);
  
  const [selectedOpp, setSelectedOpp] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [savedIds, setSavedIds] = useState<string[]>([]);
  const [toast, setToast] = useState<string | null>(null);

  const fetchOpportunities = async (isSearch = false) => {
    setLoading(true);
    try {
      let res;
      if (isSearch && query.trim()) {
        res = await axios.get(`${API_BASE}/search/`, {
          params: {
            q: query,
            category: category || undefined,
            country: country || undefined,
            women_only: womenFriendlyOnly,
            student_only: studentEligibleOnly,
          }
        });
        setOpportunities(res.data.results || []);
      } else {
        res = await axios.get(`${API_BASE}/opportunities/`, {
          params: {
            category: category || undefined,
            country: country || undefined,
            remote: remoteOnly ? true : undefined,
            women_friendly: womenFriendlyOnly ? true : undefined,
            student_eligible: studentEligibleOnly ? true : undefined,
          }
        });
        setOpportunities(res.data || []);
      }
    } catch (err) {
      console.warn("Backend API not reachable. Using mock fallbacks.");
      // Fallback local filters
      let items = [...MOCK_OPPORTUNITIES];
      if (category) items = items.filter(i => i.category === category);
      if (remoteOnly) items = items.filter(i => i.remote === true);
      if (womenFriendlyOnly) items = items.filter(i => i.women_friendly === true);
      if (studentEligibleOnly) items = items.filter(i => i.student_eligible === true);
      if (country) {
        items = items.filter(i => 
          i.country.some(c => c.toLowerCase().includes(country.toLowerCase()))
        );
      }
      if (isSearch && query.trim()) {
        items = items.filter(i => 
          i.name.toLowerCase().includes(query.toLowerCase()) ||
          i.description.toLowerCase().includes(query.toLowerCase())
        );
      }
      setOpportunities(items);
    } finally {
      setLoading(false);
    }
  };

  const fetchSavedStatus = async () => {
    try {
      const res = await axios.get(`${API_BASE}/applications/user/${FIXED_USER_ID}`);
      setSavedIds(res.data.map((app: any) => app.opportunity_id));
      
      // Load AI Centroid Recommendations
      try {
        const recRes = await axios.get(`${API_BASE}/search/recommendations/${FIXED_USER_ID}`);
        setRecommendations(recRes.data.recommendations || []);
      } catch (recErr) {
        console.log("Could not load recommendations.");
      }
    } catch (err) {
      console.log("Could not load application states from backend.");
    }
  };

  const saveOpportunity = async (oppId: string) => {
    try {
      await axios.post(`${API_BASE}/applications/`, {
        opportunity_id: oppId,
        user_id: FIXED_USER_ID,
        status: "saved",
        priority: 3
      });
      setSavedIds(prev => [...prev, oppId]);
      showToast("Added to Tracker board!");
    } catch (err) {
      showToast("Already saved or backend offline.");
    }
  };

  const triggerScraper = async () => {
    setSyncing(true);
    try {
      await axios.post(`${API_BASE}/admin/trigger-pipeline`);
      showToast("Scraper run initiated in background.");
      setTimeout(() => fetchOpportunities(), 3000);
    } catch (err) {
      showToast("Scraper trigger failed.");
    } finally {
      setSyncing(false);
    }
  };

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  useEffect(() => {
    fetchOpportunities();
    fetchSavedStatus();
  }, [category, remoteOnly, womenFriendlyOnly, studentEligibleOnly]);

  const getCategoryClass = (cat: string) => {
    switch (cat?.toLowerCase()) {
      case "scholarship": return "badge-scholarship";
      case "fellowship": return "badge-fellowship";
      case "accelerator": return "badge-accelerator";
      case "grant": return "badge-grant";
      default: return "bg-gray-800 text-gray-400 border border-gray-700";
    }
  };

  return (
    <div className="flex-1 flex flex-col md:flex-row min-h-screen">
      
      {/* Sidebar Navigation */}
      <aside className="w-full md:w-64 glass-panel border-r border-y-0 rounded-none p-6 flex flex-col gap-8">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-blue-500 to-purple-600 p-2 rounded-xl">
            <Compass className="w-6 h-6 text-white" />
          </div>
          <h1 className="font-headline font-bold text-xl tracking-tight text-white">Aetheric Ops</h1>
        </div>

        <nav className="flex flex-col gap-2">
          <Link href="/" className="flex items-center gap-3 px-4 py-3 rounded-xl bg-blue-600/10 border border-blue-500/20 text-blue-400 font-medium transition">
            <Compass className="w-5 h-5" />
            <span>Discover</span>
          </Link>
          <Link href="/tracker" className="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-400 hover:bg-white/5 border border-transparent hover:border-white/5 transition">
            <LayoutDashboard className="w-5 h-5" />
            <span>Application Board</span>
          </Link>
        </nav>

        {/* Sidebar Filters */}
        <div className="flex flex-col gap-6 pt-6 border-t border-white/5">
          <div className="flex items-center gap-2 text-white/80 font-headline font-semibold text-sm">
            <SlidersHorizontal className="w-4 h-4" />
            <span>Filters</span>
          </div>

          {/* Country Input */}
          <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold text-gray-400">Target Country</label>
            <input 
              type="text" 
              placeholder="e.g. India, Global"
              value={country} 
              onChange={(e) => setCountry(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && fetchOpportunities()}
              className="glass-input px-3 py-2 text-sm"
            />
          </div>

          {/* Toggles */}
          <div className="flex flex-col gap-3 pt-2">
            <label className="flex items-center gap-3 cursor-pointer group">
              <input 
                type="checkbox" 
                checked={remoteOnly} 
                onChange={(e) => setRemoteOnly(e.target.checked)}
                className="rounded border-gray-700 bg-black/40 text-blue-600 focus:ring-blue-600/30"
              />
              <span className="text-sm text-gray-400 group-hover:text-gray-200 transition">Remote-Only</span>
            </label>

            <label className="flex items-center gap-3 cursor-pointer group">
              <input 
                type="checkbox" 
                checked={womenFriendlyOnly} 
                onChange={(e) => setWomenFriendlyOnly(e.target.checked)}
                className="rounded border-gray-700 bg-black/40 text-blue-600 focus:ring-blue-600/30"
              />
              <span className="text-sm text-gray-400 group-hover:text-gray-200 transition">Women Friendly</span>
            </label>

            <label className="flex items-center gap-3 cursor-pointer group">
              <input 
                type="checkbox" 
                checked={studentEligibleOnly} 
                onChange={(e) => setStudentEligibleOnly(e.target.checked)}
                className="rounded border-gray-700 bg-black/40 text-blue-600 focus:ring-blue-600/30"
              />
              <span className="text-sm text-gray-400 group-hover:text-gray-200 transition">Student Eligible</span>
            </label>
          </div>
        </div>

        {/* Sync Status / Action */}
        <div className="mt-auto pt-6 border-t border-white/5 flex flex-col gap-3">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Automation Feed</span>
            <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Active
            </span>
          </div>
          <button 
            onClick={triggerScraper}
            disabled={syncing}
            className="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl border border-white/5 bg-white/5 hover:bg-white/10 text-xs font-semibold text-white transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
            <span>Sync Latest Data</span>
          </button>
        </div>
      </aside>

      {/* Main Dashboard Container */}
      <main className="flex-1 p-6 md:p-8 flex flex-col gap-6 max-w-7xl mx-auto w-full">
        
        {/* Top Search Header */}
        <header className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h2 className="font-headline font-bold text-2xl text-white">Find Opportunities</h2>
            <div className="text-xs text-gray-400 bg-white/5 border border-white/5 px-3 py-1.5 rounded-full">
              Showing {opportunities.length} programs
            </div>
          </div>

          {/* Search Bar Input */}
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              <input 
                type="text" 
                placeholder="Try: Fully funded masters for Indian students or early stage accelerators"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && fetchOpportunities(true)}
                className="glass-input w-full pl-12 pr-4 py-3.5 text-base shadow-lg"
              />
            </div>
            <button 
              onClick={() => fetchOpportunities(true)}
              className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold transition hover:brightness-110 shadow-lg shadow-blue-500/10"
            >
              <Sparkles className="w-4 h-4" />
              <span>AI Search</span>
            </button>
          </div>

          {/* Category Quick Chips */}
          <div className="flex gap-2 flex-wrap mt-1">
            {[
              { label: "All Types", value: "" },
              { label: "Scholarships", value: "scholarship" },
              { label: "Fellowships", value: "fellowship" },
              { label: "Accelerators", value: "accelerator" },
              { label: "Grants", value: "grant" },
            ].map((tab) => (
              <button
                key={tab.value}
                onClick={() => setCategory(tab.value)}
                className={`px-4 py-2 rounded-full text-xs font-semibold border transition ${
                  category === tab.value 
                    ? "bg-blue-600 border-blue-500 text-white" 
                    : "border-white/5 bg-white/5 text-gray-400 hover:border-white/10"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </header>

        {/* AI Recommendations Panel */}
        {recommendations.length > 0 && (
          <section className="glass-panel p-5 border border-purple-500/20 bg-purple-950/5 flex flex-col gap-3">
            <div className="flex items-center gap-2 text-purple-400 font-headline font-bold text-xs">
              <Sparkles className="w-4 h-4" />
              <span>AI Vector Recommendations For You</span>
            </div>
            <div className="flex gap-4 overflow-x-auto pb-2">
              {recommendations.map((opp: any) => (
                <div 
                  key={opp.id} 
                  className="min-w-[260px] max-w-[300px] glass-panel bg-[#191b23]/80 p-4 flex flex-col gap-2 hover:border-purple-500/35 transition cursor-pointer"
                  onClick={() => setSelectedOpp(opp)}
                >
                  <div className="flex justify-between items-start gap-2">
                    <h4 className="font-headline font-semibold text-sm text-white line-clamp-1">{opp.name}</h4>
                    <span className="text-[8px] uppercase tracking-wide px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20">
                      {opp.category}
                    </span>
                  </div>
                  <p className="text-[11px] text-gray-500">{opp.organization}</p>
                  <p className="text-[11px] text-gray-400 line-clamp-2 leading-relaxed">{opp.description}</p>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      saveOpportunity(opp.id);
                    }}
                    className="mt-2 text-[10px] font-semibold text-purple-400 hover:text-purple-300 text-left flex items-center gap-1"
                  >
                    <Bookmark className="w-3 h-3" />
                    <span>Save to Board</span>
                  </button>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Opportunity Card List Grid */}
        <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {loading ? (
            <div className="col-span-full flex items-center justify-center py-20">
              <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
            </div>
          ) : opportunities.length === 0 ? (
            <div className="col-span-full text-center py-20 text-gray-500">
              No opportunities match the selected criteria. Try adjusting filters or typing a broad search query.
            </div>
          ) : (
            opportunities.map((opp) => (
              <div 
                key={opp.id} 
                className="glass-panel glass-panel-hover p-6 flex flex-col gap-4 cursor-pointer"
                onClick={() => setSelectedOpp(opp)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex flex-col gap-1">
                    <h3 className="font-headline font-semibold text-lg text-white group-hover:text-blue-400 line-clamp-2 min-h-[3.5rem]">
                      {opp.name}
                    </h3>
                    <p className="text-xs text-gray-400">{opp.organization}</p>
                  </div>
                  <span className={`px-2.5 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider ${getCategoryClass(opp.category)}`}>
                    {opp.category || "General"}
                  </span>
                </div>

                <p className="text-sm text-gray-400 line-clamp-2 leading-relaxed">
                  {opp.description}
                </p>

                <div className="flex items-center gap-4 flex-wrap text-xs text-gray-500">
                  {opp.funding_amount && (
                    <span className="flex items-center gap-1 bg-white/5 border border-white/5 px-2 py-1 rounded">
                      <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-gray-300 font-medium">{opp.funding_amount}</span>
                    </span>
                  )}
                  {opp.deadline && (
                    <span className="flex items-center gap-1.5 text-amber-400 font-medium">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{new Date(opp.deadline).toLocaleDateString(undefined, {month: "short", day: "numeric"})}</span>
                    </span>
                  )}
                </div>

                <div className="flex gap-1.5 flex-wrap">
                  {opp.tags?.map((tag: string) => (
                    <span key={tag} className="text-[10px] font-semibold text-gray-500 px-2 py-0.5 rounded-md border border-white/5 bg-white/5">
                      #{tag}
                    </span>
                  ))}
                </div>

                <div className="flex items-center gap-3 pt-3 border-t border-white/5 mt-auto">
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      saveOpportunity(opp.id);
                    }}
                    className={`flex items-center justify-center gap-1.5 flex-1 py-2.5 rounded-xl border font-semibold text-xs transition ${
                      savedIds.includes(opp.id)
                        ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                        : "border-white/5 hover:border-white/10 hover:bg-white/5 text-gray-300"
                    }`}
                  >
                    {savedIds.includes(opp.id) ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Bookmark className="w-3.5 h-3.5" />}
                    <span>{savedIds.includes(opp.id) ? "Saved" : "Save Board"}</span>
                  </button>
                  <a
                    href={opp.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="flex items-center justify-center gap-1.5 flex-1 py-2.5 rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 hover:brightness-110 text-white font-semibold text-xs transition"
                  >
                    <span>Apply Now</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            ))
          )}
        </section>

        {/* Modal: Opportunity Detailed Overview */}
        {selectedOpp && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 z-50 animate-fade-in">
            <div className="glass-panel w-full max-w-2xl max-h-[85vh] overflow-y-auto p-6 md:p-8 flex flex-col gap-6 relative">
              
              <button 
                onClick={() => setSelectedOpp(null)}
                className="absolute top-4 right-4 text-gray-500 hover:text-gray-200 text-lg transition"
              >
                ✕
              </button>

              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-3">
                  <span className={`px-2.5 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider ${getCategoryClass(selectedOpp.category)}`}>
                    {selectedOpp.category}
                  </span>
                  {selectedOpp.remote && (
                    <span className="text-[10px] font-bold tracking-wide uppercase px-2.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400">
                      Remote
                    </span>
                  )}
                </div>
                <h3 className="font-headline font-bold text-2xl text-white mt-1">
                  {selectedOpp.name}
                </h3>
                <p className="text-sm text-gray-400">{selectedOpp.organization}</p>
              </div>

              {/* AI generated Summary block */}
              <div className="p-4 rounded-xl border border-blue-500/20 bg-blue-500/5 flex flex-col gap-2">
                <div className="flex items-center gap-2 text-blue-400 font-headline font-bold text-xs">
                  <Sparkles className="w-4 h-4" />
                  <span>AI Extracted Insights</span>
                </div>
                <p className="text-sm text-blue-200/90 leading-relaxed">
                  {selectedOpp.ai_summary || "Our AI engine is currently processing dynamic details for this opportunity program."}
                </p>
              </div>

              <div className="flex flex-col gap-4 text-sm text-gray-400">
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex flex-col gap-1 border-r border-white/5 pr-4">
                    <span className="text-xs text-gray-500 font-semibold uppercase">Deadline Date</span>
                    <span className="text-white font-medium flex items-center gap-1.5">
                      <Calendar className="w-4 h-4 text-amber-400" />
                      {selectedOpp.deadline ? new Date(selectedOpp.deadline).toLocaleDateString() : "Rolling Basis"}
                    </span>
                  </div>
                  <div className="flex flex-col gap-1">
                    <span className="text-xs text-gray-500 font-semibold uppercase">Financial Funding</span>
                    <span className="text-white font-medium flex items-center gap-1.5">
                      <DollarSign className="w-4 h-4 text-emerald-400" />
                      {selectedOpp.funding_amount || "No specified funding details"}
                    </span>
                  </div>
                </div>

                <div className="flex flex-col gap-1 pt-2">
                  <span className="text-xs text-gray-500 font-semibold uppercase">Eligibility Requirements</span>
                  <p className="text-gray-300 leading-relaxed text-sm">
                    {selectedOpp.eligibility_text || "Open to worldwide eligible applications matching candidate criteria."}
                  </p>
                </div>

                {selectedOpp.country && (
                  <div className="flex flex-col gap-1">
                    <span className="text-xs text-gray-500 font-semibold uppercase">Target Countries</span>
                    <span className="text-gray-300 flex items-center gap-1.5">
                      <MapPin className="w-4 h-4 text-blue-400" />
                      {selectedOpp.country.join(", ")}
                    </span>
                  </div>
                )}
              </div>

              <div className="flex items-center gap-4 pt-4 border-t border-white/5">
                <button 
                  onClick={() => {
                    saveOpportunity(selectedOpp.id);
                    setSelectedOpp(null);
                  }}
                  className={`flex items-center justify-center gap-2 flex-1 py-3 rounded-xl border font-semibold text-sm transition ${
                    savedIds.includes(selectedOpp.id)
                      ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                      : "border-white/5 hover:border-white/10 hover:bg-white/5 text-gray-200"
                  }`}
                >
                  <Bookmark className="w-4 h-4" />
                  <span>{savedIds.includes(selectedOpp.id) ? "Saved in Board" : "Save to Application Board"}</span>
                </button>
                <a
                  href={selectedOpp.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 flex-1 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 hover:brightness-110 text-white font-semibold text-sm transition shadow-lg shadow-blue-500/15"
                >
                  <span>Apply Instantly</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Global Toast Alert */}
        {toast && (
          <div className="fixed bottom-6 right-6 z-50 glass-panel bg-slate-900 border-blue-500/30 px-6 py-4 flex items-center gap-3 animate-slide-in shadow-2xl">
            <Sparkles className="w-5 h-5 text-blue-400" />
            <span className="text-sm font-semibold text-white">{toast}</span>
          </div>
        )}

      </main>

    </div>
  );
}

"use client";

import { useState, useEffect } from "react";
import { 
  LayoutDashboard, Compass, Calendar, SlidersHorizontal, AlertCircle,
  Plus, ChevronRight, ChevronLeft, Trash2, Edit, Save, RefreshCw,
  Clock, DollarSign, ExternalLink
} from "lucide-react";
import axios from "axios";
import Link from "next/link";

const API_BASE = "http://localhost:8000/api";
const FIXED_USER_ID = "00000000-0000-0000-0000-000000000000";

const COLUMNS = [
  { id: "saved", title: "Saved Opportunities", color: "border-blue-500/30" },
  { id: "planning", title: "Planning & Prep", color: "border-amber-500/30" },
  { id: "applied", title: "Applied", color: "border-purple-500/30" },
  { id: "interview", title: "Interviewing", color: "border-pink-500/30" },
  { id: "accepted", title: "Offers / Accepted", color: "border-emerald-500/30" }
];

export default function Tracker() {
  const [applications, setApplications] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingNotesId, setEditingNotesId] = useState<string | null>(null);
  const [notesText, setNotesText] = useState("");
  const [editingPriorityId, setEditingPriorityId] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const fetchTracker = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/applications/user/${FIXED_USER_ID}`);
      setApplications(res.data || []);
    } catch (err) {
      console.warn("Backend API not reachable. Using mock tracking applications.");
      // Hydrate some mock applications for local fallback view
      setApplications([
        {
          id: "app-m1",
          opportunity_id: "m-1",
          status: "saved",
          priority: 1,
          notes: "Need to draft my recommendation letters.",
          opportunity: {
            id: "m-1",
            name: "Thiel Fellowship 2026",
            organization: "Thiel Foundation",
            category: "fellowship",
            deadline: "2026-08-31T00:00:00Z"
          }
        },
        {
          id: "app-m2",
          opportunity_id: "m-2",
          status: "planning",
          priority: 2,
          notes: "Getting transcripts compiled.",
          opportunity: {
            id: "m-2",
            name: "Erasmus Mundus Joint Masters",
            organization: "European Union Council",
            category: "scholarship",
            deadline: "2026-10-15T00:00:00Z"
          }
        },
        {
          id: "app-m3",
          opportunity_id: "m-3",
          status: "interview",
          priority: 1,
          notes: "Technical round scheduled for next Thursday.",
          opportunity: {
            id: "m-3",
            name: "Y Combinator Summer 2026 Batch",
            organization: "Y Combinator",
            category: "accelerator",
            deadline: "2026-07-01T00:00:00Z"
          }
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (appId: string, newStatus: string) => {
    try {
      await axios.patch(`${API_BASE}/applications/${appId}`, {
        status: newStatus
      });
      setApplications(prev => prev.map(app => 
        app.id === appId ? { ...app, status: newStatus } : app
      ));
      showToast("Updated application stage");
    } catch (err) {
      // Local fallback edit
      setApplications(prev => prev.map(app => 
        app.id === appId ? { ...app, status: newStatus } : app
      ));
      showToast("Updated locally (offline)");
    }
  };

  const deleteApp = async (appId: string) => {
    try {
      await axios.delete(`${API_BASE}/applications/${appId}`);
      setApplications(prev => prev.filter(app => app.id !== appId));
      showToast("Removed from tracker");
    } catch (err) {
      setApplications(prev => prev.filter(app => app.id !== appId));
      showToast("Removed locally (offline)");
    }
  };

  const saveNotes = async (appId: string) => {
    try {
      await axios.patch(`${API_BASE}/applications/${appId}`, {
        notes: notesText
      });
      setApplications(prev => prev.map(app => 
        app.id === appId ? { ...app, notes: notesText } : app
      ));
      setEditingNotesId(null);
      showToast("Notes saved successfully");
    } catch (err) {
      setApplications(prev => prev.map(app => 
        app.id === appId ? { ...app, notes: notesText } : app
      ));
      setEditingNotesId(null);
      showToast("Saved locally (offline)");
    }
  };

  const updatePriority = async (appId: string, prio: number) => {
    try {
      await axios.patch(`${API_BASE}/applications/${appId}`, {
        priority: prio
      });
      setApplications(prev => prev.map(app => 
        app.id === appId ? { ...app, priority: prio } : app
      ));
      setEditingPriorityId(null);
      showToast("Priority updated");
    } catch (err) {
      setApplications(prev => prev.map(app => 
        app.id === appId ? { ...app, priority: prio } : app
      ));
      setEditingPriorityId(null);
      showToast("Updated priority locally");
    }
  };

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  useEffect(() => {
    fetchTracker();
  }, []);

  const getPriorityLabel = (level: number) => {
    switch (level) {
      case 1: return { label: "High", css: "bg-red-500/10 border-red-500/30 text-red-400" };
      case 2: return { label: "Medium", css: "bg-amber-500/10 border-amber-500/30 text-amber-400" };
      default: return { label: "Low", css: "bg-blue-500/10 border-blue-500/30 text-blue-400" };
    }
  };

  const getCategoryClass = (cat: string) => {
    switch (cat?.toLowerCase()) {
      case "scholarship": return "badge-scholarship";
      case "fellowship": return "badge-fellowship";
      case "accelerator": return "badge-accelerator";
      case "grant": return "badge-grant";
      default: return "bg-gray-800 text-gray-400 border border-gray-700";
    }
  };

  // Compute Stats
  const totalTracked = applications.length;
  const appliedCount = applications.filter(a => a.status === "applied").length;
  const interviewCount = applications.filter(a => a.status === "interview").length;
  const offerCount = applications.filter(a => a.status === "accepted").length;

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
          <Link href="/" className="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-400 hover:bg-white/5 border border-transparent hover:border-white/5 transition">
            <Compass className="w-5 h-5" />
            <span>Discover</span>
          </Link>
          <Link href="/tracker" className="flex items-center gap-3 px-4 py-3 rounded-xl bg-blue-600/10 border border-blue-500/20 text-blue-400 font-medium transition">
            <LayoutDashboard className="w-5 h-5" />
            <span>Application Board</span>
          </Link>
        </nav>

        {/* Board Stats panel */}
        <div className="mt-auto p-4 rounded-xl border border-white/5 bg-white/5 flex flex-col gap-3">
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Metrics</div>
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-400">Total Tracked</span>
            <span className="font-bold text-white">{totalTracked}</span>
          </div>
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-400">Applied</span>
            <span className="font-bold text-purple-400">{appliedCount}</span>
          </div>
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-400">Interviews</span>
            <span className="font-bold text-pink-400">{interviewCount}</span>
          </div>
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-400">Offers</span>
            <span className="font-bold text-emerald-400">{offerCount}</span>
          </div>
        </div>
      </aside>

      {/* Main Board Container */}
      <main className="flex-1 p-6 md:p-8 flex flex-col gap-6 w-full overflow-x-auto">
        
        <header className="flex flex-col gap-1 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="font-headline font-bold text-2xl text-white">Application Tracker Board</h2>
            <p className="text-sm text-gray-400">Track and update progress of your global opportunities</p>
          </div>
          
          <button 
            onClick={fetchTracker} 
            className="flex items-center justify-center gap-2 px-4 py-2 border border-white/5 bg-white/5 hover:bg-white/10 rounded-xl text-xs font-semibold text-white transition self-start mt-2 md:mt-0"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reload Board</span>
          </button>
        </header>

        {/* Board columns section */}
        <div className="flex gap-6 min-h-[70vh] items-start pb-6">
          {COLUMNS.map((col) => {
            const colApps = applications.filter((app) => app.status === col.id);
            
            return (
              <div 
                key={col.id} 
                className="flex-1 min-w-[280px] max-w-[360px] flex flex-col gap-4 self-stretch"
              >
                {/* Column Title */}
                <div className={`p-4 rounded-xl border border-b-4 glass-panel ${col.color} flex justify-between items-center shadow-lg`}>
                  <span className="font-headline font-semibold text-sm text-white tracking-wide">{col.title}</span>
                  <span className="text-xs bg-white/5 text-gray-400 font-bold px-2 py-0.5 rounded-md border border-white/5">{colApps.length}</span>
                </div>

                {/* Column Items */}
                <div className="flex-1 flex flex-col gap-4 overflow-y-auto max-h-[65vh] pr-1">
                  {colApps.map((app) => {
                    const opp = app.opportunity || {};
                    const prio = getPriorityLabel(app.priority);
                    const isEditingNotes = editingNotesId === app.id;
                    const isEditingPrio = editingPriorityId === app.id;

                    return (
                      <div 
                        key={app.id} 
                        className="glass-panel p-4 flex flex-col gap-3 shadow-md border-white/5 hover:border-white/10 transition"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <span className={`px-2 py-0.5 rounded-full text-[9px] uppercase font-bold tracking-wider ${getCategoryClass(opp.category)}`}>
                            {opp.category || "General"}
                          </span>
                          
                          {/* Priority Chip Select */}
                          {isEditingPrio ? (
                            <div className="flex gap-1">
                              {[1, 2, 3].map((p) => (
                                <button
                                  key={p}
                                  onClick={() => updatePriority(app.id, p)}
                                  className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${getPriorityLabel(p).css}`}
                                >
                                  {p === 1 ? "H" : p === 2 ? "M" : "L"}
                                </button>
                              ))}
                            </div>
                          ) : (
                            <span 
                              onClick={() => {
                                setEditingPriorityId(app.id);
                              }}
                              className={`px-2 py-0.5 rounded-full text-[9px] font-bold border cursor-pointer hover:scale-105 transition ${prio.css}`}
                              title="Click to change priority"
                            >
                              {prio.label} Prio
                            </span>
                          )}
                        </div>

                        <div>
                          <h4 className="font-headline font-semibold text-sm text-white line-clamp-1">{opp.name || "Untitled Program"}</h4>
                          <p className="text-[11px] text-gray-500 mt-0.5">{opp.organization || "No listed host"}</p>
                        </div>

                        {opp.deadline && (
                          <div className="flex items-center gap-1.5 text-[11px] text-amber-400 font-medium">
                            <Clock className="w-3.5 h-3.5" />
                            <span>Deadline: {new Date(opp.deadline).toLocaleDateString()}</span>
                          </div>
                        )}

                        {/* Notes Section */}
                        <div className="pt-2 border-t border-white/5 flex flex-col gap-1.5">
                          <div className="flex justify-between items-center text-[10px] text-gray-500 font-semibold uppercase">
                            <span>My Notes</span>
                            {!isEditingNotes ? (
                              <button 
                                onClick={() => {
                                  setEditingNotesId(app.id);
                                  setNotesText(app.notes || "");
                                }}
                                className="text-gray-400 hover:text-white"
                              >
                                <Edit className="w-3 h-3" />
                              </button>
                            ) : (
                              <button 
                                onClick={() => saveNotes(app.id)}
                                className="text-emerald-400 hover:text-emerald-300"
                              >
                                <Save className="w-3 h-3" />
                              </button>
                            )}
                          </div>
                          
                          {isEditingNotes ? (
                            <textarea
                              value={notesText}
                              onChange={(e) => setNotesText(e.target.value)}
                              className="w-full text-xs bg-black/40 border border-white/10 rounded-md p-1.5 text-gray-200 focus:outline-none focus:border-blue-500"
                              rows={2}
                            />
                          ) : (
                            <p className="text-[11px] text-gray-400 leading-relaxed italic">
                              {app.notes || "No notes added yet. Click edit to write logs, links, or to-do items."}
                            </p>
                          )}
                        </div>

                        {/* Move Actions / Stage Updates */}
                        <div className="flex justify-between items-center pt-3 border-t border-white/5 mt-1 gap-2">
                          <button 
                            onClick={() => deleteApp(app.id)}
                            className="text-gray-500 hover:text-red-400 p-1 transition"
                            title="Remove from board"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>

                          <div className="flex gap-1 ml-auto">
                            {/* Previous Column button */}
                            {COLUMNS.indexOf(col) > 0 && (
                              <button 
                                onClick={() => {
                                  const prevIdx = COLUMNS.indexOf(col) - 1;
                                  updateStatus(app.id, COLUMNS[prevIdx].id);
                                }}
                                className="p-1 border border-white/5 bg-white/5 hover:bg-white/10 rounded text-gray-400 hover:text-white transition"
                                title="Move Stage Left"
                              >
                                <ChevronLeft className="w-3 h-3" />
                              </button>
                            )}
                            {/* Next Column button */}
                            {COLUMNS.indexOf(col) < COLUMNS.length - 1 && (
                              <button 
                                onClick={() => {
                                  const nextIdx = COLUMNS.indexOf(col) + 1;
                                  updateStatus(app.id, COLUMNS[nextIdx].id);
                                }}
                                className="p-1 border border-white/5 bg-white/5 hover:bg-white/10 rounded text-gray-400 hover:text-white transition"
                                title="Move Stage Right"
                              >
                                <ChevronRight className="w-3 h-3" />
                              </button>
                            )}
                          </div>
                        </div>

                      </div>
                    );
                  })}

                  {colApps.length === 0 && (
                    <div className="text-center py-8 text-xs border border-dashed border-white/5 rounded-xl text-gray-600">
                      Empty column
                    </div>
                  )}
                </div>

              </div>
            );
          })}
        </div>

        {/* Global Toast Alert */}
        {toast && (
          <div className="fixed bottom-6 right-6 z-50 glass-panel bg-slate-900 border-blue-500/30 px-6 py-4 flex items-center gap-3 animate-slide-in shadow-2xl">
            <AlertCircle className="w-5 h-5 text-blue-400" />
            <span className="text-sm font-semibold text-white">{toast}</span>
          </div>
        )}

      </main>

    </div>
  );
}

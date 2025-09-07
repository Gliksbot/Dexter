import { useState, useEffect } from "react";
import { motion, Reorder } from "framer-motion";
import { Home, Database, Settings, Zap, Brain, FileText, Download, Send, Power, Volume2, VolumeX, SlidersHorizontal, Plus, Trash } from "lucide-react";

// --- Default slots (blank labels) ---
const defaultSlots = [
  {
    id: "slot1",
    label: "",
    enabled: true,
    local: true,
    endpoint: "http://localhost:8000/llm/slot1",
    model: "",
    apiKey: "",
    temperature: 0.5,
    maxTokens: 1024,
    messages: [],
    muted: true,
  },
];

export default function DexterSidebarUI() {
  const [active, setActive] = useState("conversations");
  const [autonomous, setAutonomous] = useState(false);
  const [slots, setSlots] = useState(defaultSlots);
  const [blastInput, setBlastInput] = useState("");
  const [skills, setSkills] = useState([]);
  const [logs, setLogs] = useState([]);
  const [patterns, setPatterns] = useState([]);
  const [downloads, setDownloads] = useState([]);

  const menu = [
    { id: "conversations", label: "Conversations", icon: Home },
    { id: "memory", label: "Memory", icon: Database },
    { id: "skills", label: "Skills", icon: Zap },
    { id: "downloads", label: "Downloads", icon: Download },
    { id: "patterns", label: "Patterns", icon: Brain },
    { id: "logs", label: "Logs", icon: FileText },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  // --- API INTEGRATIONS ---
  useEffect(() => {
    fetch("/api/skills")
      .then((res) => res.json())
      .then((data) => setSkills(data || []))
      .catch(() => setSkills([]));
  }, []);

  useEffect(() => {
    fetch("/api/downloads")
      .then((res) => res.json())
      .then((data) => setDownloads(data || []))
      .catch(() => setDownloads([]));
  }, []);

  useEffect(() => {
    const logSource = new EventSource("/api/events?slot=logs");
    logSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        setLogs((prev) => [...prev.slice(-200), data]);
      } catch {}
    };
    const patternSource = new EventSource("/api/events?slot=patterns");
    patternSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        setPatterns((prev) => [...prev.slice(-200), data]);
      } catch {}
    };
    return () => {
      logSource.close();
      patternSource.close();
    };
  }, []);

  // --- HELPERS ---
  function toggleMute(id) {
    setSlots((prev) => prev.map((s) => (s.id === id ? { ...s, muted: !s.muted } : s)));
  }

  function addSlot() {
    const newId = `slot${slots.length + 1}`;
    setSlots((prev) => [
      ...prev,
      {
        id: newId,
        label: "",
        enabled: true,
        local: true,
        endpoint: `http://localhost:8000/llm/${newId}`,
        model: "",
        apiKey: "",
        temperature: 0.5,
        maxTokens: 1024,
        messages: [],
        muted: true,
      },
    ]);
  }

  function removeSlot(id) {
    setSlots((prev) => prev.filter((s) => s.id !== id));
  }

  function speak(text, slot) {
    if (!text || slot.muted) return;
    const utter = new SpeechSynthesisUtterance(`${slot.label || slot.id} says: ${text}`);
    speechSynthesis.speak(utter);
  }

  function handleSlotChange(id, patch) {
    setSlots((prev) => prev.map((s) => (s.id === id ? { ...s, ...patch } : s)));
  }

  // --- VIEWS ---
  function SlotCard({ slot }) {
    const [openCfg, setOpenCfg] = useState(false);

    return (
      <motion.div layout className="bg-gray-800 rounded-2xl p-3 flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">{slot.label || "(unnamed slot)"}</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={() => toggleMute(slot.id)}
              className={`p-1 rounded ${slot.muted ? "bg-gray-700" : "bg-green-600"}`}
              title={slot.muted ? "Unmute" : "Mute"}
            >
              {slot.muted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
            </button>
            <button
              onClick={() => setOpenCfg((v) => !v)}
              className="p-1 rounded bg-gray-700 hover:bg-gray-600"
              title="Configure"
            >
              <SlidersHorizontal className="w-4 h-4" />
            </button>
            <button
              onClick={() => removeSlot(slot.id)}
              className="p-1 rounded bg-red-700 hover:bg-red-600"
              title="Remove Slot"
            >
              <Trash className="w-4 h-4" />
            </button>
          </div>
        </div>

        {openCfg && (
          <div className="bg-gray-900/60 rounded-xl p-3 grid md:grid-cols-2 gap-3">
            <label className="text-sm flex flex-col gap-1">
              <span className="text-gray-300">Label</span>
              <input
                className="bg-gray-800 rounded-lg px-3 py-2"
                value={slot.label}
                onChange={(e) => handleSlotChange(slot.id, { label: e.target.value })}
              />
            </label>
            <label className="text-sm flex flex-col gap-1">
              <span className="text-gray-300">Endpoint</span>
              <input
                className="bg-gray-800 rounded-lg px-3 py-2"
                value={slot.endpoint}
                onChange={(e) => handleSlotChange(slot.id, { endpoint: e.target.value })}
              />
            </label>
            <label className="text-sm flex flex-col gap-1">
              <span className="text-gray-300">Model</span>
              <input
                className="bg-gray-800 rounded-lg px-3 py-2"
                value={slot.model}
                onChange={(e) => handleSlotChange(slot.id, { model: e.target.value })}
              />
            </label>
            <label className="text-sm flex flex-col gap-1">
              <span className="text-gray-300">API Key (optional)</span>
              <input
                className="bg-gray-800 rounded-lg px-3 py-2"
                value={slot.apiKey}
                onChange={(e) => handleSlotChange(slot.id, { apiKey: e.target.value })}
              />
            </label>
            <label className="text-sm flex flex-col gap-1">
              <span className="text-gray-300">Temperature</span>
              <input
                type="number"
                step="0.1"
                className="bg-gray-800 rounded-lg px-3 py-2"
                value={slot.temperature}
                onChange={(e) => handleSlotChange(slot.id, { temperature: parseFloat(e.target.value) })}
              />
            </label>
            <label className="text-sm flex flex-col gap-1">
              <span className="text-gray-300">Max Tokens</span>
              <input
                type="number"
                className="bg-gray-800 rounded-lg px-3 py-2"
                value={slot.maxTokens}
                onChange={(e) => handleSlotChange(slot.id, { maxTokens: parseInt(e.target.value) })}
              />
            </label>
          </div>
        )}

        <div className="bg-gray-900/40 rounded-xl p-3 space-y-2 h-56 overflow-y-auto text-sm text-gray-300">
          {slot.messages.length === 0 ? (
            <div className="text-gray-400">No messages yet.</div>
          ) : (
            slot.messages.map((m, i) => {
              if (m.role === "assistant") speak(m.text, slot);
              return <div key={i}>{m.text}</div>;
            })
          )}
        </div>
      </motion.div>
    );
  }

  function ConversationsView() {
    return (
      <div className="flex flex-col gap-4">
        <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center">
          <div className="flex items-center gap-2 bg-gray-800 rounded-xl px-3 py-2">
            <Power className={`w-4 h-4 ${autonomous ? "text-green-400" : "text-gray-400"}`} />
            <label className="text-sm">Autonomous Mode</label>
            <button
              onClick={() => setAutonomous((v) => !v)}
              className={`ml-2 px-3 py-1 rounded-lg text-sm ${autonomous ? "bg-green-600" : "bg-gray-700"}`}
            >
              {autonomous ? "On" : "Off"}
            </button>
          </div>

          <div className="flex-1 flex gap-2">
            <input
              value={blastInput}
              onChange={(e) => setBlastInput(e.target.value)}
              placeholder="Type once… blasts to all slots"
              className="flex-1 bg-gray-800 rounded-xl px-4 py-2 outline-none"
            />
            <button
              onClick={() => setBlastInput("")}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 rounded-xl px-4"
            >
              <Send className="w-4 h-4" /> Blast
            </button>
            <button
              onClick={addSlot}
              className="flex items-center gap-2 bg-green-600 hover:bg-green-500 rounded-xl px-4"
            >
              <Plus className="w-4 h-4" /> Add Slot
            </button>
          </div>
        </div>

        <Reorder.Group axis="y" values={slots} onReorder={setSlots} className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
          {slots.map((s) => (
            <Reorder.Item key={s.id} value={s}>
              <SlotCard slot={s} />
            </Reorder.Item>
          ))}
        </Reorder.Group>
      </div>
    );
  }

  function SkillsView() {
    return (
      <section>
        <h2 className="text-xl font-semibold mb-4">Skills</h2>
        <div className="bg-gray-800 rounded-xl p-3 h-96 overflow-y-auto text-sm text-gray-300">
          {skills.length === 0 ? (
            <div>No skills installed.</div>
          ) : (
            <ul className="space-y-2">
              {skills.map((s, i) => (
                <li key={i}>{s.name || JSON.stringify(s)}</li>
              ))}
            </ul>
          )}
        </div>
      </section>
    );
  }

  function DownloadsView() {
    return (
      <section>
        <h2 className="text-xl font-semibold mb-4">Downloads</h2>
        <div className="bg-gray-800 rounded-xl p-3 h-96 overflow-y-auto text-sm text-gray-300">
          {downloads.length === 0 ? (
            <div>No files available.</div>
          ) : (
            <ul className="space-y-2">
              {downloads.map((f, i) => (
                <li key={i} className="flex justify-between items-center bg-gray-900 rounded-lg p-2">
                  <div>
                    <div className="font-semibold">{f.name}</div>
                    <div className="text-xs text-gray-400">{f.size} bytes — {f.modified}</div>
                  </div>
                  <a href={f.url} download className="bg-blue-600 hover:bg-blue-500 px-2 py-1 rounded text-xs">
                    Download
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    );
  }

  function LogsView() {
    return (
      <section>
        <h2 className="text-xl font-semibold mb-4">Logs</h2>
        <div className="bg-gray-800 rounded-xl p-3 h-96 overflow-y-auto text-sm text-gray-300">
          {logs.map((log, i) => (
            <div key={i}>{JSON.stringify(log)}</div>
          ))}
        </div>
      </section>
    );
  }

  function PatternsView() {
    return (
      <section>
        <h2 className="text-xl font-semibold mb-4">Patterns</h2>
        <div className="bg-gray-800 rounded-xl p-3 h-96 overflow-y-auto text-sm text-gray-300">
          {patterns.map((p, i) => (
            <div key={i}>{JSON.stringify(p)}</div>
          ))}
        </div>
      </section>
    );
  }

  function MemoryView() {
    return (
      <section>
        <h2 className="text-xl font-semibold mb-4">Memory</h2>
        <p className="text-gray-300">(Connect to your memory API to browse STM/LTM.)</p>
      </section>
    );
  }

  function SettingsView() {
    return (
      <section>
        <h2 className="text-xl font-semibold mb-4">Settings</h2>
        <p className="text-gray-300">(Global settings, themes, persistence, ports.)</p>
      </section>
    );
  }

  // --- MAIN RETURN ---
  return (
    <div className="flex h-screen bg-gray-900 text-white">
      <aside className="w-64 bg-gray-800 flex flex-col p-4 space-y-2">
        <h1 className="text-2xl font-bold mb-4">Dexter</h1>
        {menu.map((item) => (
          <motion.button
            whileHover={{ scale: 1.03 }}
            key={item.id}
            onClick={() => setActive(item.id)}
            className={`flex items-center p-2 rounded-xl space-x-3 w-full text-left ${
              active === item.id ? "bg-blue-600" : "bg-gray-700 hover:bg-gray-600"
            }`}
          >
            <item.icon className="w-5 h-5" />
            <span>{item.label}</span>
          </motion.button>
        ))}
      </aside>

      <main className="flex-1 p-6 overflow-y-auto">
        {active === "conversations" && <ConversationsView />}
        {active === "memory" && <MemoryView />}
        {active === "skills" && <SkillsView />}
        {active === "downloads" && <DownloadsView />}
        {active === "patterns" && <PatternsView />}
        {active === "logs" && <LogsView />}
        {active === "settings" && <SettingsView />}
      </main>
    </div>
  );
}

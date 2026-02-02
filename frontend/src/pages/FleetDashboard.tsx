import { useState } from 'react';
import {
  LayoutDashboard,
  Map,
  Truck,
  BarChart3,
  Settings,
  Brain,
} from 'lucide-react';
import { CommandCenter } from '../components/fleet/CommandCenter';
import { MissionPlanner } from '../components/fleet/MissionPlanner';
import { Analytics } from '../components/fleet/Analytics';

type Tab = 'dashboard' | 'planner' | 'analytics';

export function FleetDashboard() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');

  const tabs = [
    { id: 'dashboard' as Tab, label: 'Command Center', icon: LayoutDashboard },
    { id: 'planner' as Tab, label: 'Mission Planner', icon: Map },
    { id: 'analytics' as Tab, label: 'Analytics', icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-64 bg-neuro-slate text-white p-6 hidden lg:block">
        <div className="flex items-center gap-3 mb-8">
          <Brain className="text-signal-amber" size={32} />
          <div>
            <h1 className="font-bold text-lg">Neuro-Logistics</h1>
            <p className="text-xs text-blue-300">Fleet Command</p>
          </div>
        </div>

        <nav className="space-y-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                activeTab === tab.id
                  ? 'bg-neuro-blue text-white'
                  : 'text-gray-300 hover:bg-white/10'
              }`}
            >
              <tab.icon size={20} />
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>

        <div className="mt-auto pt-8">
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-white/10">
            <Settings size={20} />
            <span>Settings</span>
          </button>
        </div>
      </aside>

      <div className="lg:hidden fixed top-0 left-0 right-0 bg-neuro-slate text-white p-4 flex items-center justify-between z-10">
        <div className="flex items-center gap-2">
          <Brain className="text-signal-amber" size={24} />
          <h1 className="font-bold">Fleet Command</h1>
        </div>
        <Truck size={24} />
      </div>

      <main className="flex-1 lg:pt-0 pt-16">
        {activeTab === 'dashboard' && <CommandCenter />}
        {activeTab === 'planner' && <MissionPlanner />}
        {activeTab === 'analytics' && <Analytics />}
      </main>

      <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-2 grid grid-cols-3 gap-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex flex-col items-center gap-1 py-2 rounded-lg ${
              activeTab === tab.id ? 'text-neuro-blue bg-blue-50' : 'text-gray-600'
            }`}
          >
            <tab.icon size={20} />
            <span className="text-xs">{tab.label.split(' ')[0]}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

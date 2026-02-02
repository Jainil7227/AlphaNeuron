import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp, Users, Truck, DollarSign } from 'lucide-react';
import { Card } from '../ui/Card';
import { KPICard } from '../ui/KPICard';

export function Analytics() {
  const revenueData = [
    { month: 'Jan', revenue: 125000, cost: 95000 },
    { month: 'Feb', revenue: 138000, cost: 102000 },
    { month: 'Mar', revenue: 152000, cost: 108000 },
    { month: 'Apr', revenue: 145000, cost: 105000 },
    { month: 'May', revenue: 168000, cost: 115000 },
    { month: 'Jun', revenue: 182000, cost: 120000 },
  ];

  const utilizationData = [
    { name: 'Active', value: 65, color: '#10B981' },
    { name: 'Idle', value: 25, color: '#F59E0B' },
    { name: 'Maintenance', value: 10, color: '#EF4444' },
  ];

  const performanceData = [
    { driver: 'Rajesh K.', trips: 48, revenue: 125000, rating: 4.8 },
    { driver: 'Amit S.', trips: 42, revenue: 112000, rating: 4.6 },
    { driver: 'Priya S.', trips: 45, revenue: 118000, rating: 4.9 },
    { driver: 'Vikram M.', trips: 38, revenue: 98000, rating: 4.5 },
    { driver: 'Sneha P.', trips: 41, revenue: 105000, rating: 4.7 },
  ];

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Analytics Dashboard</h1>
        <p className="text-gray-600">Comprehensive performance insights and metrics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <KPICard
          title="Total Revenue (MTD)"
          value="₹182K"
          icon={DollarSign}
          trend={{ value: '15%', positive: true }}
          color="text-profit-green"
        />
        <KPICard
          title="Active Drivers"
          value={performanceData.length}
          icon={Users}
          trend={{ value: '3%', positive: true }}
        />
        <KPICard
          title="Fleet Size"
          value="24"
          icon={Truck}
          color="text-neuro-blue"
        />
        <KPICard
          title="Avg. Trip Value"
          value="₹3,640"
          icon={TrendingUp}
          trend={{ value: '8%', positive: true }}
          color="text-signal-amber"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h3 className="font-bold text-lg mb-4">Revenue vs Cost Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <Bar dataKey="revenue" fill="#10B981" name="Revenue" radius={[8, 8, 0, 0]} />
              <Bar dataKey="cost" fill="#EF4444" name="Cost" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h3 className="font-bold text-lg mb-4">Fleet Utilization</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={utilizationData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {utilizationData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card>
        <h3 className="font-bold text-lg mb-4">Top Performing Drivers</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-sm text-gray-700">
                  Driver Name
                </th>
                <th className="text-left py-3 px-4 font-semibold text-sm text-gray-700">Trips</th>
                <th className="text-left py-3 px-4 font-semibold text-sm text-gray-700">
                  Revenue
                </th>
                <th className="text-left py-3 px-4 font-semibold text-sm text-gray-700">Rating</th>
                <th className="text-left py-3 px-4 font-semibold text-sm text-gray-700">
                  Performance
                </th>
              </tr>
            </thead>
            <tbody>
              {performanceData.map((driver, index) => (
                <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4">{driver.driver}</td>
                  <td className="py-3 px-4 font-mono">{driver.trips}</td>
                  <td className="py-3 px-4 font-mono text-profit-green font-semibold">
                    ₹{driver.revenue.toLocaleString()}
                  </td>
                  <td className="py-3 px-4">
                    <span className="flex items-center gap-1">
                      ⭐ {driver.rating}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-profit-green h-2 rounded-full"
                        style={{ width: `${(driver.rating / 5) * 100}%` }}
                      />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Card className="bg-gradient-to-r from-neuro-slate to-gray-800 text-white">
        <h3 className="font-bold text-lg mb-4">AI Insights & Recommendations</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white/10 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="text-profit-green" size={20} />
              <h4 className="font-semibold">Efficiency Opportunity</h4>
            </div>
            <p className="text-sm text-gray-300">
              Routes through Highway 44 are 18% faster on average. Consider prioritizing these
              routes during peak hours.
            </p>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="text-signal-amber" size={20} />
              <h4 className="font-semibold">Revenue Maximization</h4>
            </div>
            <p className="text-sm text-gray-300">
              Detected 12 potential backhaul opportunities this week. Average additional revenue:
              ₹4,200 per trip.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}

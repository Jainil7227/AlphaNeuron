import { motion } from 'framer-motion';
import { Truck, Brain, MapPin, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';

export function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-neuro-slate via-blue-900 to-neuro-blue">
      <div className="container mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <div className="flex items-center justify-center mb-6">
            <Brain className="text-signal-amber mr-3" size={48} />
            <h1 className="text-5xl font-bold text-white">Neuro-Logistics</h1>
          </div>
          <p className="text-xl text-blue-200">The AI Co-Pilot for Intelligent Logistics Operations</p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="backdrop-blur-md bg-white/10 rounded-xl p-8 border border-white/20"
          >
            <MapPin className="text-signal-amber mb-4" size={40} />
            <h3 className="text-2xl font-bold text-white mb-3">Context-Aware Planner</h3>
            <p className="text-blue-200">
              Smart route optimization with real-time risk assessment and dynamic pricing
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="backdrop-blur-md bg-white/10 rounded-xl p-8 border border-white/20"
          >
            <Brain className="text-signal-amber mb-4" size={40} />
            <h3 className="text-2xl font-bold text-white mb-3">Rolling Decision Engine</h3>
            <p className="text-blue-200">
              AI agents continuously optimize routes and suggest opportunities in real-time
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="backdrop-blur-md bg-white/10 rounded-xl p-8 border border-white/20"
          >
            <TrendingUp className="text-signal-amber mb-4" size={40} />
            <h3 className="text-2xl font-bold text-white mb-3">Dynamic Capacity Manager</h3>
            <p className="text-blue-200">
              Maximize revenue with intelligent load matching and backhaul optimization
            </p>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="flex justify-center gap-6"
        >
          <Button
            onClick={() => navigate('/driver')}
            variant="warning"
            size="lg"
            className="flex items-center gap-2"
          >
            <Truck size={20} />
            Driver Dashboard
          </Button>
          <Button
            onClick={() => navigate('/fleet')}
            variant="primary"
            size="lg"
            className="flex items-center gap-2"
          >
            <Brain size={20} />
            Fleet Command Center
          </Button>
        </motion.div>
      </div>
    </div>
  );
}

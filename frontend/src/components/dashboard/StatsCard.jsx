import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, CheckCircle, Clock, AlertTriangle } from 'lucide-react';

const StatsCard = ({ title, value, icon, color, loading = false }) => {
  const iconMap = {
    calendar: <Calendar className="w-6 h-6" />,
    check: <CheckCircle className="w-6 h-6" />,
    clock: <Clock className="w-6 h-6" />,
    alert: <AlertTriangle className="w-6 h-6" />
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      className="bg-surface border border-border rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow duration-200"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-text-light text-sm font-medium">{title}</p>
          {loading ? (
            <div className="h-8 w-16 bg-gray-200 rounded animate-pulse" />
          ) : (
            <motion.h3
              initial={{ scale: 0.5 }}
              animate={{ scale: 1 }}
              className="text-3xl font-bold text-text mt-1"
            >
              {value}
            </motion.h3>
          )}
        </div>
        <div className={`p-3 rounded-full ${color}`}>
          {iconMap[icon]}
        </div>
      </div>
    </motion.div>
  );
};

export default StatsCard;
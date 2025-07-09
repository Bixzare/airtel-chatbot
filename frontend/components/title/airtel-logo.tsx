'use client'

import { motion } from 'framer-motion'
import { AirtelSymbol, AirtelText } from './svg'
import React, { Suspense } from 'react'

const AirtelLogoFallback = () => (
  <div className="relative w-60 h-40 flex flex-col items-center justify-center">
    <div className="mb-4 animate-pulse">
      <svg viewBox="0 0 120 80" width={120} height={80}>
        <rect width="120" height="80" rx="20" fill="#E31F26" fillOpacity="0.6" />
      </svg>
    </div>
    <div className="animate-pulse">
      <svg viewBox="0 80 120 50" width={200} height={60}>
        <rect width="200" height="60" rx="10" fill="#E31F26" fillOpacity="0.6" />
      </svg>
    </div>
  </div>
)

export const AirtelLogo = () => {
  return (
    <Suspense fallback={<AirtelLogoFallback />}>
      <div className="relative w-60 h-40 overflow-hidden">
        <motion.div
          className="flex flex-col items-center justify-center w-full h-full"
          style={{ willChange: 'transform' }}
          initial={{ scale: 0.95 }}
          animate={{ scale: [1, 0.95, 1] }}
          transition={{
            duration: 4,
            repeat: Infinity,
            repeatType: 'loop',
            ease: 'easeInOut',
            delay: 2,
          }}
        >
          {/* Airtel Symbol Animation */}
          <motion.div
            className="mb-4"
            initial={{
              y: -100,
              opacity: 0,
              rotate: -180,
              scale: 0.5,
            }}
            animate={{
              y: 0,
              opacity: 1,
              rotate: 0,
              scale: 1,
            }}
            transition={{
              type: 'spring',
              stiffness: 100,
              damping: 15,
              duration: 1.2,
            }}
          >
            <motion.div
              className="drop-shadow-2xl"
              whileHover={{
                scale: 1.1,
                rotate: 5,
                transition: { duration: 0.3 },
              }}
            >
              <AirtelSymbol className="w-[120px] h-[80px]" />
            </motion.div>
          </motion.div>

          {/* Airtel Text Animation */}
          <motion.div
            initial={{
              x: 100,
              opacity: 0,
              scale: 0.8,
            }}
            animate={{
              x: 0,
              opacity: 1,
              scale: 1,
            }}
            transition={{
              type: 'spring',
              stiffness: 80,
              damping: 12,
              delay: 0.5,
              duration: 1,
            }}
          >
            <motion.div
              className="drop-shadow-lg"
              whileHover={{
                scale: 1.05,
                transition: { duration: 0.3 },
              }}
            >
              <AirtelText className="w-[200px] h-[60px]" />
            </motion.div>
          </motion.div>
        </motion.div>

        {/* Optional: Animated background glow effect */}
        <motion.div
          className="absolute bg-gradient-radial from-red-500/20 via-transparent to-transparent rounded-full blur-3xl"
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{
            opacity: [0, 0.5, 0],
            scale: [0.5, 1.2, 0.5],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            repeatType: 'loop',
            ease: 'easeInOut',
            delay: 1.5,
          }}
          style={{
            width: '300px',
            height: '300px',
            left: '50%',
            top: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: -1,
          }}
        />
      </div>
    </Suspense>
  )
}

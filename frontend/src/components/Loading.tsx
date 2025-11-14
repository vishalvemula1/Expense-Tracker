import { motion } from 'framer-motion';

export function Loading() {
  return (
    <div className="flex items-center justify-center p-8">
      <motion.div
        className="h-12 w-12 rounded-full border-4 border-gray-200 border-t-primary-600"
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      />
    </div>
  );
}

export function LoadingScreen() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="text-center">
        <motion.div
          className="mx-auto h-16 w-16 rounded-full border-4 border-gray-200 border-t-primary-600"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        />
        <p className="mt-4 text-gray-600">Loading...</p>
      </div>
    </div>
  );
}

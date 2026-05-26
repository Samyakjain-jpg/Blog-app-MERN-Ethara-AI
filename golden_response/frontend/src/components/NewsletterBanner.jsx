import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { subscribeNewsletter } from '../utils/api'

export default function NewsletterBanner() {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState('idle')

  const handleSubscribe = async (e) => {
    e.preventDefault()
    setStatus('loading')

    try {
      await subscribeNewsletter(email)
      setStatus('success')
      setEmail('')
    } catch {
      setStatus('error')
    }
  }

  return (
    <section className="mx-auto my-16 max-w-4xl rounded-2xl border border-neutral-200 bg-neutral-100 p-8 dark:border-neutral-800 dark:bg-neutral-900">
      <div className="mx-auto max-w-xl text-center">
        <h3 className="text-2xl font-bold tracking-tight">
          Stay updated with deep tech insights
        </h3>
        <p className="mt-2 text-sm text-neutral-600 dark:text-neutral-400">
          No spam. Only architectural perspectives in your inbox.
        </p>

        <form
          onSubmit={handleSubscribe}
          className="mt-6 flex flex-col gap-3 sm:flex-row"
        >
          <input
            type="email"
            required
            placeholder="Enter your email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="flex-grow rounded-lg border border-neutral-300 bg-white px-4 py-2 focus:outline-emerald-500 dark:border-neutral-800 dark:bg-black"
          />
          <button
            type="submit"
            disabled={status === 'loading'}
            className="rounded-lg bg-neutral-900 px-6 py-2 font-medium text-white hover:opacity-90 disabled:opacity-60 dark:bg-white dark:text-black"
          >
            {status === 'loading' ? 'Subscribing...' : 'Subscribe'}
          </button>
        </form>

        <AnimatePresence>
          {status === 'success' && (
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mt-4 text-sm font-medium text-emerald-500"
            >
              Welcome to the inner circle! Check your inbox.
            </motion.p>
          )}
          {status === 'error' && (
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mt-4 text-sm font-medium text-red-500"
            >
              Subscription failed. Please try again.
            </motion.p>
          )}
        </AnimatePresence>
      </div>
    </section>
  )
}

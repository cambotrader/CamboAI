'use client'

import { redirect } from 'next/navigation'

export default function IndexRedirect() {
  // Redirect root to dashboard main
  redirect('/dashboard')
}
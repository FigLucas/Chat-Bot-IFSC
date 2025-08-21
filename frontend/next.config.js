/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
  
  },
  images: {
    domains: ['localhost'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
 
  reactStrictMode: false,
}

module.exports = nextConfig
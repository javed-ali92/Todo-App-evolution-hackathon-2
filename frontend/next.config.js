/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    typedRoutes: true,
  },
  // Removed rewrites - frontend will call backend directly using NEXT_PUBLIC_API_BASE_URL
  // This allows proper production deployment where frontend (Vercel) calls backend (Hugging Face)
};

module.exports = nextConfig;

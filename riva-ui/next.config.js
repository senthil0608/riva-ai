/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'standalone',
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: 'http://backend:8000/api/:path*',
            },
            {
                source: '/aura',
                destination: 'http://backend:8000/aura',
            },
        ]
    },
}

module.exports = nextConfig

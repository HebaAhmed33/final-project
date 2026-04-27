/** @type {import('next').NextConfig} */
const nextConfig = {
  async redirects() {
    return [
      {
        source: '/config-analysis',
        destination: '/workspace',
        permanent: true,
      },
    ];
  },
};

export default nextConfig;

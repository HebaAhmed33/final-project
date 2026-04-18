"use client";

import { usePathname } from "next/navigation";
import Sidebar from "./Sidebar";
import AuthGuard from "./AuthGuard";

import TopNavbar from "./TopNavbar";

const PUBLIC_ROUTES = ["/", "/login", "/request-access", "/news", "/about"];

export default function AppShell({ children }) {
  const pathname = usePathname();
  const isPublic = PUBLIC_ROUTES.includes(pathname);

  if (isPublic) {
    return (
      <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
        <TopNavbar />
        <main style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          {children}
        </main>
      </div>
    );
  }

  return (
    <AuthGuard>
      <div style={{ display: "flex", minHeight: "100vh" }}>
        <Sidebar />
        <main
          style={{
            flex: 1,
            marginLeft: "260px",
            display: "flex",
            flexDirection: "column",
          }}
        >
          {children}
        </main>
      </div>
    </AuthGuard>
  );
}

import "./globals.css";
import AppShell from "./components/AppShell";

export const metadata = {
  title: "SmartISMS GRC Platform",
  description: "Enterprise GRC & Security Intelligence Platform",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}

import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Quant Lab — Inspectable Research Systems",
  description: "Five reproducible AI and quantitative research systems for financial research, forecasting, portfolio simulation, markets, and experimentation.",
  openGraph: {
    title: "AI Quant Lab — Inspectable Research Systems",
    description: "Five reproducible research systems for curious, skeptical minds.",
    images: [{ url: "/og.png", width: 1200, height: 630, alt: "AI Quant Lab system map" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "AI Quant Lab — Inspectable Research Systems",
    description: "Five reproducible research systems for curious, skeptical minds.",
    images: ["/og.png"],
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}

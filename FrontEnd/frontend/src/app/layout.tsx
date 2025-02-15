import type { Metadata } from "next";
import { Tomorrow, Poppins } from "next/font/google";
import "./globals.css";
import Header from './components/header';
import Footer from './components/footer'

const fontfam = Tomorrow({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-tomorrow",
});

export const metadata: Metadata = {
  title: "Pandera",
  description: "Generated by create next app",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/puzzle.ico" />
      </head>
      <body
        className={`${fontfam.variable} font-sans antialiased`}
      >
        <Header></Header>
        {children}
        <Footer></Footer>
      </body>
    </html>
  );
}

import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LearnLoop Agent — AI 学习教练",
  description: "通用垂类知识学习 Agent 平台，诊断→教学→练习→验证闭环",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur border-b border-gray-200">
          <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
            <a href="/" className="flex items-center gap-2 font-bold text-lg text-indigo-600">
              <span className="text-2xl">🧠</span> LearnLoop
            </a>
            <div className="flex items-center gap-4 text-sm">
              <a href="/" className="hover:text-indigo-600 transition">首页</a>
              <a href="/domains" className="hover:text-indigo-600 transition">学习领域</a>
            </div>
          </div>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchDomains } from "@/lib/api";
import type { Domain } from "@/types";

export default function DomainsPage() {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDomains()
      .then(setDomains)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-2">选择学习领域</h1>
      <p className="text-gray-600 mb-8">选择你想要学习的知识领域，AI 教练会先诊断你的水平</p>

      {loading && (
        <div className="text-center py-20">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full" />
          <p className="mt-3 text-gray-500">加载中...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 mb-6">
          ⚠️ {error} — 请确保后端服务已启动 (http://localhost:8000)
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {domains.map((d) => (
          <Link
            key={d.id}
            href={`/domains/${d.id}`}
            className="group bg-white rounded-xl p-6 border border-gray-200 hover:border-indigo-300 hover:shadow-lg transition-all"
          >
            <div className="flex items-start gap-4">
              <div className="text-4xl">{d.icon}</div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h2 className="text-xl font-semibold group-hover:text-indigo-600 transition">{d.name}</h2>
                  <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">{d.category}</span>
                </div>
                <p className="text-gray-600 text-sm mb-3">{d.description}</p>
                <div className="flex items-center gap-4 text-xs text-gray-400">
                  <span>📚 {d.concept_count} 个概念</span>
                  <span className="text-indigo-500 font-medium group-hover:underline">开始学习 →</span>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {!loading && domains.length === 0 && !error && (
        <div className="text-center py-20 text-gray-400">
          <p className="text-4xl mb-3">📭</p>
          <p>暂无可用领域，请先运行种子数据脚本</p>
        </div>
      )}
    </div>
  );
}

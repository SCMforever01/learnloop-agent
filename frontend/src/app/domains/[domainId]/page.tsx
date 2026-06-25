"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { fetchDomain, fetchConcepts, createSession } from "@/lib/api";
import type { Domain, Concept } from "@/types";

export default function DomainDetailPage() {
  const params = useParams();
  const router = useRouter();
  const domainId = params.domainId as string;

  const [domain, setDomain] = useState<Domain | null>(null);
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    Promise.all([fetchDomain(domainId), fetchConcepts(domainId)])
      .then(([d, c]) => { setDomain(d); setConcepts(c); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [domainId]);

  const handleStart = async () => {
    setStarting(true);
    try {
      const session = await createSession(domainId);
      router.push(`/learn/${session.session_id}`);
    } catch (e) {
      alert("创建会话失败：" + (e as Error).message);
    } finally {
      setStarting(false);
    }
  };

  if (loading) return <div className="text-center py-20"><div className="animate-spin inline-block w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full" /></div>;
  if (!domain) return <div className="text-center py-20 text-gray-400">领域不存在</div>;

  const levelColors = ["", "bg-green-100 text-green-700", "bg-blue-100 text-blue-700", "bg-yellow-100 text-yellow-700", "bg-red-100 text-red-700"];

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-4xl">{domain.icon}</span>
          <div>
            <h1 className="text-3xl font-bold">{domain.name}</h1>
            <span className="text-sm text-gray-500">{domain.category}</span>
          </div>
        </div>
        <p className="text-gray-600 mt-2">{domain.description}</p>
      </div>

      <button
        onClick={handleStart}
        disabled={starting}
        className="w-full md:w-auto bg-indigo-600 text-white font-semibold px-8 py-3 rounded-full text-lg hover:bg-indigo-700 transition disabled:opacity-50 mb-10"
      >
        {starting ? "创建中..." : "🚀 开始 AI 诊断"}
      </button>

      <h2 className="text-xl font-bold mb-4">知识图谱 ({concepts.length} 个概念)</h2>
      <div className="space-y-3">
        {concepts.map((c, i) => (
          <div key={c.id} className="bg-white rounded-lg p-4 border border-gray-200 flex items-center gap-4">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold text-sm">
              {i + 1}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h3 className="font-medium">{c.name}</h3>
                <span className={`text-xs px-2 py-0.5 rounded-full ${levelColors[Math.min(c.level, 4)]}`}>
                  Lv.{c.level}
                </span>
                {c.mastery_score > 0 && (
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                    掌握 {Math.round(c.mastery_score * 100)}%
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-500 mt-0.5">{c.description}</p>
              {c.prerequisites.length > 0 && (
                <p className="text-xs text-gray-400 mt-1">前置：{c.prerequisites.join(", ")}</p>
              )}
            </div>
            <div className="flex gap-1">
              {c.tags.map((t) => (
                <span key={t} className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded">{t}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

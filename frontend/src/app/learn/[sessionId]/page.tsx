"use client";

import { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import {
  getSession,
  startDiagnosis,
  answerDiagnosis,
  startTeaching,
  teachReply,
  generatePractice,
  submitPractice,
  startVerification,
  submitVerification,
  planPath,
  fetchConcepts,
} from "@/lib/api";
import type { ChatMessage, PracticeQuestion, DiagnosisResult, Concept, LearningPath } from "@/types";

const AGENT_LABELS: Record<string, { label: string; color: string }> = {
  diagnose: { label: "🔍 诊断", color: "bg-blue-100 text-blue-700" },
  teach: { label: "💬 教学", color: "bg-indigo-100 text-indigo-700" },
  practice: { label: "📝 练习", color: "bg-purple-100 text-purple-700" },
  verify: { label: "✅ 验证", color: "bg-green-100 text-green-700" },
  path_planner: { label: "🗺️ 路径", color: "bg-amber-100 text-amber-700" },
};

export default function LearnPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;

  const [phase, setPhase] = useState("loading");
  const [domainId, setDomainId] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [diagnosis, setDiagnosis] = useState<DiagnosisResult | null>(null);
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [practiceQuestions, setPracticeQuestions] = useState<PracticeQuestion[]>([]);
  const [practiceIndex, setPracticeIndex] = useState(0);
  const [practiceFeedback, setPracticeFeedback] = useState("");
  const [selectedOption, setSelectedOption] = useState("");
  const [learningPath, setLearningPath] = useState<LearningPath | null>(null);
  const [currentConceptId, setCurrentConceptId] = useState("");

  const chatEndRef = useRef<HTMLDivElement>(null);
  const scrollToBottom = () => chatEndRef.current?.scrollIntoView({ behavior: "smooth" });

  useEffect(() => { scrollToBottom(); }, [messages]);

  // 初始化会话
  useEffect(() => {
    getSession(sessionId).then((data: Record<string, unknown>) => {
      setDomainId(data.domain_id as string);
      setPhase((data.phase as string) || "diagnose");
      setCurrentConceptId((data.current_concept_id as string) || "");
      fetchConcepts(data.domain_id as string).then(setConcepts).catch(() => {});
      if ((data.phase as string) === "diagnose") {
        handleStartDiagnosis();
      }
    }).catch(console.error);
  }, [sessionId]);

  const addMessage = (role: "user" | "assistant", agentType: string, content: string) => {
    setMessages((prev) => [...prev, { role, agent_type: agentType, content }]);
  };

  // ===== 诊断 =====
  const handleStartDiagnosis = async () => {
    setLoading(true);
    try {
      const { reply } = await startDiagnosis(sessionId);
      addMessage("assistant", "diagnose", reply);
      setPhase("diagnose");
    } catch (e) {
      addMessage("assistant", "diagnose", "⚠️ 启动诊断失败：" + (e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const msg = input.trim();
    setInput("");
    addMessage("user", phase, msg);
    setLoading(true);

    try {
      if (phase === "diagnose") {
        const result = await answerDiagnosis(sessionId, msg);
        addMessage("assistant", "diagnose", result.reply);
        if (result.diagnosis) {
          setDiagnosis(result.diagnosis);
          setPhase("learn");
          addMessage("assistant", "path_planner", "🎯 诊断完成！正在为你生成学习路径...");
          try {
            const path = await planPath(sessionId);
            setLearningPath(path);
            const firstStep = path.learning_path?.[0];
            if (firstStep) {
              setCurrentConceptId(firstStep.concept_id);
              addMessage("assistant", "path_planner", `🗺️ 学习路径已生成！建议从「${firstStep.concept_name}」开始，预计总学习时长 ${path.total_estimated_minutes} 分钟。\n\n点击「开始学习」进入第一个概念。`);
            }
          } catch {
            addMessage("assistant", "path_planner", "⚠️ 路径生成失败，你可以手动选择概念开始学习。");
          }
        }
      } else if (phase === "learn") {
        const result = await teachReply(sessionId, msg, currentConceptId);
        addMessage("assistant", "teach", result.reply);
        if (result.concept_mastered) {
          addMessage("assistant", "teach", "🎉 你已掌握这个概念！建议进入练习环节巩固。");
        }
      }
    } catch (e) {
      addMessage("assistant", phase, "⚠️ 出错了：" + (e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  // ===== 教学 =====
  const handleStartTeaching = async (conceptId: string) => {
    setCurrentConceptId(conceptId);
    setPhase("learn");
    setLoading(true);
    try {
      const { reply } = await startTeaching(sessionId, conceptId);
      addMessage("assistant", "teach", reply);
    } catch (e) {
      addMessage("assistant", "teach", "⚠️ 启动教学失败：" + (e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  // ===== 练习 =====
  const handleStartPractice = async () => {
    if (!currentConceptId) return;
    setPhase("practice");
    setLoading(true);
    try {
      const result = await generatePractice(sessionId, currentConceptId);
      setPracticeQuestions(result.questions || []);
      setPracticeIndex(0);
      setPracticeFeedback("");
      setSelectedOption("");
      addMessage("assistant", "practice", `📝 已生成 ${result.questions?.length || 0} 道练习题，开始作答吧！`);
    } catch (e) {
      addMessage("assistant", "practice", "⚠️ 生成练习失败：" + (e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitPractice = async () => {
    if (!selectedOption) return;
    setLoading(true);
    try {
      const result = await submitPractice(sessionId, practiceIndex, selectedOption);
      setPracticeFeedback(result.feedback);
      addMessage("assistant", "practice",
        `${result.correct ? "✅ 正确！" : "❌ 错误"} ${result.feedback}`
      );
    } catch (e) {
      addMessage("assistant", "practice", "⚠️ 提交失败：" + (e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleNextQuestion = () => {
    setPracticeIndex((i) => i + 1);
    setPracticeFeedback("");
    setSelectedOption("");
  };

  // ===== 验证 =====
  const handleStartVerify = async () => {
    if (!currentConceptId) return;
    setPhase("verify");
    setLoading(true);
    try {
      const result = await startVerification(sessionId, currentConceptId);
      setPracticeQuestions(result.questions || []);
      setPracticeIndex(0);
      addMessage("assistant", "verify", `✅ 验证环节开始！共 ${result.questions?.length || 0} 道题，检验你的学习成果。`);
    } catch (e) {
      addMessage("assistant", "verify", "⚠️ 启动验证失败：" + (e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const currentQuestion = practiceQuestions[practiceIndex];
  const conceptName = concepts.find((c) => c.id === currentConceptId)?.name || currentConceptId;

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 flex flex-col h-[calc(100vh-56px)]">
      {/* 顶部状态栏 */}
      <div className="flex items-center justify-between mb-4 flex-shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-gray-500">阶段：</span>
          {(["diagnose", "learn", "practice", "verify"] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPhase(p)}
              className={`text-xs px-3 py-1 rounded-full transition ${phase === p ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-500 hover:bg-gray-200"}`}
            >
              {p === "diagnose" ? "🔍 诊断" : p === "learn" ? "💬 学习" : p === "practice" ? "📝 练习" : "✅ 验证"}
            </button>
          ))}
        </div>
        {currentConceptId && (
          <span className="text-xs bg-indigo-50 text-indigo-600 px-3 py-1 rounded-full">
            当前：{conceptName}
          </span>
        )}
      </div>

      {/* 聊天区域 */}
      <div className="flex-1 overflow-y-auto bg-white rounded-xl border border-gray-200 p-4 mb-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 py-10">
            <p className="text-3xl mb-2">🧠</p>
            <p>AI 教练正在准备...</p>
          </div>
        )}

        {messages.map((m, i) => {
          const agent = AGENT_LABELS[m.agent_type] || { label: m.agent_type, color: "bg-gray-100 text-gray-600" };
          return (
            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] ${m.role === "user" ? "order-2" : ""}`}>
                {m.role === "assistant" && (
                  <span className={`inline-block text-xs px-2 py-0.5 rounded-full mb-1 ${agent.color}`}>
                    {agent.label}
                  </span>
                )}
                <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                  m.role === "user"
                    ? "bg-indigo-600 text-white rounded-br-md"
                    : "bg-gray-100 text-gray-800 rounded-bl-md"
                }`}>
                  {m.content}
                </div>
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3 text-sm text-gray-500">
              <span className="animate-pulse">AI 思考中...</span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* 诊断结果面板 */}
      {diagnosis && phase === "learn" && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-4 flex-shrink-0">
          <h3 className="font-semibold text-blue-800 mb-2">📊 诊断结果</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            <div><span className="text-gray-500">水平：</span><span className="font-medium">{diagnosis.overall_level}</span></div>
            <div><span className="text-gray-500">优势：</span><span className="font-medium">{diagnosis.strengths.join(", ") || "暂无"}</span></div>
            <div><span className="text-gray-500">弱点：</span><span className="font-medium text-red-600">{diagnosis.weaknesses.join(", ") || "暂无"}</span></div>
            <div><span className="text-gray-500">预计时长：</span><span className="font-medium">{diagnosis.estimated_study_hours}h</span></div>
          </div>
        </div>
      )}

      {/* 学习路径面板 */}
      {learningPath && phase === "learn" && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4 flex-shrink-0">
          <h3 className="font-semibold text-amber-800 mb-2">🗺️ 学习路径</h3>
          <div className="flex flex-wrap gap-2">
            {learningPath.learning_path.map((step) => (
              <button
                key={step.step}
                onClick={() => handleStartTeaching(step.concept_id)}
                className={`text-xs px-3 py-1.5 rounded-full border transition ${
                  step.concept_id === currentConceptId
                    ? "bg-indigo-600 text-white border-indigo-600"
                    : "bg-white text-gray-600 border-gray-300 hover:border-indigo-400"
                }`}
              >
                {step.step}. {step.concept_name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 练习题面板 */}
      {phase === "practice" && currentQuestion && (
        <div className="bg-purple-50 border border-purple-200 rounded-xl p-4 mb-4 flex-shrink-0">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-purple-800">📝 第 {practiceIndex + 1}/{practiceQuestions.length} 题</h3>
            <span className="text-xs text-gray-500">难度：{currentQuestion.difficulty}/10</span>
          </div>
          <p className="text-sm mb-3 font-medium">{currentQuestion.content}</p>
          {currentQuestion.options && currentQuestion.options.length > 0 ? (
            <div className="space-y-2 mb-3">
              {currentQuestion.options.map((opt) => (
                <button
                  key={opt}
                  onClick={() => setSelectedOption(opt)}
                  className={`w-full text-left text-sm px-4 py-2 rounded-lg border transition ${
                    selectedOption === opt
                      ? "bg-indigo-100 border-indigo-400 text-indigo-700"
                      : "bg-white border-gray-200 hover:border-gray-300"
                  }`}
                >
                  {opt}
                </button>
              ))}
            </div>
          ) : (
            <input
              type="text"
              value={selectedOption}
              onChange={(e) => setSelectedOption(e.target.value)}
              placeholder="输入你的答案..."
              className="w-full text-sm px-4 py-2 border border-gray-300 rounded-lg mb-3"
            />
          )}
          {practiceFeedback && (
            <div className="bg-white rounded-lg p-3 text-sm border mb-3">{practiceFeedback}</div>
          )}
          <div className="flex gap-2">
            {!practiceFeedback ? (
              <button onClick={handleSubmitPractice} disabled={!selectedOption || loading} className="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm disabled:opacity-50">
                提交答案
              </button>
            ) : (
              <>
                {practiceIndex < practiceQuestions.length - 1 ? (
                  <button onClick={handleNextQuestion} className="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm">
                    下一题
                  </button>
                ) : (
                  <button onClick={handleStartVerify} className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm">
                    进入验证
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* 概念选择面板（学习阶段无路径时） */}
      {phase === "learn" && !learningPath && concepts.length > 0 && (
        <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 mb-4 flex-shrink-0">
          <h3 className="font-semibold text-gray-700 mb-2">📚 选择概念开始学习</h3>
          <div className="flex flex-wrap gap-2">
            {concepts.slice(0, 8).map((c) => (
              <button
                key={c.id}
                onClick={() => handleStartTeaching(c.id)}
                className="text-xs px-3 py-1.5 rounded-full bg-white border border-gray-300 hover:border-indigo-400 transition"
              >
                {c.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 操作栏 */}
      <div className="flex gap-2 mb-3 flex-shrink-0">
        {phase === "learn" && (
          <>
            <button onClick={handleStartPractice} disabled={!currentConceptId || loading} className="bg-purple-100 text-purple-700 px-4 py-2 rounded-lg text-sm hover:bg-purple-200 transition disabled:opacity-50">
              📝 练习
            </button>
            <button onClick={handleStartVerify} disabled={!currentConceptId || loading} className="bg-green-100 text-green-700 px-4 py-2 rounded-lg text-sm hover:bg-green-200 transition disabled:opacity-50">
              ✅ 验证
            </button>
          </>
        )}
      </div>

      {/* 输入框 */}
      <div className="flex gap-2 flex-shrink-0">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder={phase === "diagnose" ? "回答诊断题..." : "输入你的问题或回答..."}
          className="flex-1 px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:border-indigo-400"
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || loading}
          className="bg-indigo-600 text-white px-6 py-3 rounded-xl text-sm font-medium hover:bg-indigo-700 transition disabled:opacity-50"
        >
          发送
        </button>
      </div>
    </div>
  );
}

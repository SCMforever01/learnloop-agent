import Link from "next/link";

const FEATURES = [
  { icon: "🔍", title: "智能诊断", desc: "5-8 道题快速评估你的水平" },
  { icon: "💬", title: "苏格拉底教学", desc: "不给答案，引导你自己思考" },
  { icon: "📝", title: "自适应练习", desc: "根据掌握度生成针对性题目" },
  { icon: "✅", title: "闭环验证", desc: "学习效果可量化追踪" },
];

export default function Home() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-purple-600 to-indigo-800 text-white">
        <div className="max-w-6xl mx-auto px-4 py-20 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-4">
            🧠 AI 学习教练
          </h1>
          <p className="text-xl md:text-2xl text-indigo-100 mb-8 max-w-2xl mx-auto">
            不是给你答案，而是教你思考。<br />
            覆盖编程、金融、考证、数学……任何你想学的知识。
          </p>
          <Link
            href="/domains"
            className="inline-block bg-white text-indigo-600 font-semibold px-8 py-3 rounded-full text-lg hover:bg-indigo-50 transition shadow-lg"
          >
            开始学习 →
          </Link>
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-gray-50 to-transparent" />
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <h2 className="text-2xl font-bold text-center mb-12">为什么选择 LearnLoop？</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {FEATURES.map((f) => (
            <div key={f.title} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition">
              <div className="text-3xl mb-3">{f.icon}</div>
              <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
              <p className="text-gray-600 text-sm">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="bg-white py-16">
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-2xl font-bold text-center mb-12">学习闭环</h2>
          <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-2">
            {[
              { step: "①", label: "诊断", color: "bg-blue-500" },
              { step: "②", label: "学习", color: "bg-indigo-500" },
              { step: "③", label: "练习", color: "bg-purple-500" },
              { step: "④", label: "验证", color: "bg-green-500" },
            ].map((s, i) => (
              <div key={s.label} className="flex items-center gap-2">
                <div className={`${s.color} text-white rounded-full w-12 h-12 flex items-center justify-center font-bold text-lg`}>
                  {s.step}
                </div>
                <span className="font-medium">{s.label}</span>
                {i < 3 && <span className="hidden md:block text-gray-300 text-2xl mx-2">→</span>}
              </div>
            ))}
          </div>
          <p className="text-center text-gray-500 mt-6 text-sm">循环往复，直到掌握</p>
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-6xl mx-auto px-4 py-16 text-center">
        <h2 className="text-2xl font-bold mb-4">准备好了吗？</h2>
        <p className="text-gray-600 mb-8">选择一个领域，AI 教练马上开始诊断你的水平</p>
        <Link
          href="/domains"
          className="inline-block bg-indigo-600 text-white font-semibold px-8 py-3 rounded-full text-lg hover:bg-indigo-700 transition"
        >
          浏览学习领域
        </Link>
      </section>

      {/* Footer */}
      <footer className="bg-gray-100 py-8 text-center text-sm text-gray-500">
        <p>LearnLoop Agent — 通用垂类知识学习平台</p>
        <p className="mt-1">Built with FastAPI + Next.js + LLM Agents</p>
      </footer>
    </div>
  );
}

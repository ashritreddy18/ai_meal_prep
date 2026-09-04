"use client";

import { useMemo, useState } from "react";

type MealDetails = {
  name?: string;
  description?: string;
  calories?: number;
  protein_g?: number;
  prep_minutes?: number;
  ingredients?: { name?: string; quantity?: number; unit?: string }[];
  nutrition?: {
    calories?: number;
    protein_g?: number;
    carbs_g?: number;
    fat_g?: number;
    fiber_g?: number;
  };
  instructions?: string[];
};

type MealPlan = {
  summary?: string;
  meals: {
    breakfast?: MealDetails;
    lunch?: MealDetails;
    dinner?: MealDetails;
  };
  tips?: string[];
  shopping_focus?: string[];
};

type MealKey = "breakfast" | "lunch" | "dinner";

type SelectOption = {
  value: string;
  label: string;
};

const API_PATH_CANDIDATES = ["/generate-meal", "/generate_meal", "/api/generate-meal"];
const API_TIMEOUT_MS = 25000;

const normalizeBaseUrl = (url: string) => url.replace(/\/+$/, "");

const unique = (values: string[]) =>
  values.filter((value, index) => values.indexOf(value) === index);

const API_BASE_CANDIDATES = unique(
  [
    process.env.NEXT_PUBLIC_API_BASE_URL,
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:8001",
    "http://localhost:8001",
  ]
    .filter((value): value is string => Boolean(value))
    .map(normalizeBaseUrl)
);

export default function MealPlannerPage() {
  const [apiBaseUrl, setApiBaseUrl] = useState(API_BASE_CANDIDATES[0] ?? "http://127.0.0.1:8000");
  const [resolvedApi, setResolvedApi] = useState<{ base: string; path: string } | null>(null);

  const [goal, setGoal] = useState("fat loss");
  const [diet, setDiet] = useState("vegetarian");
  const [time, setTime] = useState("quick (<=30 min)");

  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState("");
  const [error, setError] = useState("");
  const [activeMealKey, setActiveMealKey] = useState<MealKey | null>(null);

  const canGenerate = useMemo(() => !!goal && !!diet && !!time, [goal, diet, time]);

  const goalOptions: SelectOption[] = [
    { value: "fat loss", label: "Fat Loss" },
    { value: "muscle gain", label: "Muscle Gain" },
    { value: "maintenance", label: "Maintenance" },
    { value: "general healthy eating", label: "General Healthy Eating" },
  ];

  const dietOptions: SelectOption[] = [
    { value: "vegetarian", label: "Vegetarian" },
    { value: "eggetarian", label: "Eggetarian" },
    { value: "non-vegetarian", label: "Non-Vegetarian" },
    { value: "vegan", label: "Vegan" },
  ];

  const timeOptions: SelectOption[] = [
    { value: "quick (<=30 min)", label: "Quick (≤ 30 min)" },
    { value: "moderate (30-60 min)", label: "Moderate (30-60 min)" },
    { value: "flexible", label: "Flexible" },
  ];

  const SelectField = ({
    id,
    label,
    value,
    onChange,
    options,
  }: {
    id: string;
    label: string;
    value: string;
    onChange: (nextValue: string) => void;
    options: SelectOption[];
  }) => (
    <div>
      <label htmlFor={id} className="mb-1 block text-sm font-medium text-stone-700">
        {label}
      </label>
      <div className="relative">
        <select
          id={id}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full appearance-none rounded-xl border border-stone-300 bg-white px-3 py-2.5 pr-10 text-sm font-medium text-stone-800 shadow-sm transition hover:border-stone-400 focus:border-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-700/20"
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>

        <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-stone-500">
          <svg
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="h-4 w-4"
            aria-hidden="true"
          >
            <path
              d="M5 7.5L10 12.5L15 7.5"
              stroke="currentColor"
              strokeWidth="1.6"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>
      </div>
    </div>
  );

  const extractErrorDetail = async (response: Response) => {
    try {
      const errData = await response.json();
      if (errData?.detail) {
        return typeof errData.detail === "string"
          ? errData.detail
          : JSON.stringify(errData.detail);
      }
    } catch {
      // ignore parse errors
    }
    return `HTTP error ${response.status}`;
  };

  const fetchJsonWithTimeout = async (url: string) => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), API_TIMEOUT_MS);
    try {
      const response = await fetch(url, { signal: controller.signal });
      const status = response.status;
      if (!response.ok) return { ok: false, status };
      const data = await response.json();
      return { ok: true, status, data };
    } catch {
      return { ok: false, status: 0 };
    } finally {
      clearTimeout(timeout);
    }
  };

  const findMealPlannerApi = async () => {
    for (const candidateBaseUrl of API_BASE_CANDIDATES) {
      const openapi = await fetchJsonWithTimeout(`${candidateBaseUrl}/openapi.json`);
      if (!openapi.ok || !openapi.data?.paths) {
        continue;
      }

      const pathKeys = Object.keys(openapi.data.paths);
      const matchedPath = API_PATH_CANDIDATES.find((candidate) => pathKeys.includes(candidate));
      if (!matchedPath) {
        continue;
      }

      const health = await fetchJsonWithTimeout(`${candidateBaseUrl}/health`);
      if (health.ok && health.data?.openrouter_api_key_set === false) {
        throw new Error(
          "OPENROUTER_API_KEY is not set in the Meal Planner backend. Add it to backend/.env and restart the server."
        );
      }

      return { base: candidateBaseUrl, path: matchedPath };
    }

    throw new Error(
      "Meal Planner API endpoint not found. Start the Meal Planner backend or set NEXT_PUBLIC_API_BASE_URL."
    );
  };

  const handleGenerateMealPlan = async () => {
    if (!canGenerate) {
      setError("Please fill out all fields.");
      return;
    }

    setLoading(true);
    setLoadingStep("Initializing AI Agent...");
    setError("");
    setMealPlan(null);

    const steps = [
      "Searching Indian recipe knowledge base...",
      "Analyzing nutritional constraints...",
      "Designing your custom meal plan...",
      "Verifying daily macros...",
      "Finalizing structured output..."
    ];
    let stepIndex = 0;
    const interval = setInterval(() => {
      setLoadingStep(steps[stepIndex % steps.length]);
      stepIndex++;
    }, 2500);

    try {
      const target = resolvedApi ?? (await findMealPlannerApi());
      const response = await fetch(`${target.base}${target.path}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ goal, diet, time }),
      });

      if (!response.ok) {
        const detail = await extractErrorDetail(response);
        throw new Error(detail);
      }

      const data = await response.json();
      setResolvedApi(target);
      setApiBaseUrl(target.base);
      setMealPlan(data.meal_plan);
    } catch (e: unknown) {
      setResolvedApi(null);
      const message = e instanceof Error ? e.message : "Unknown error";
      if (message === "Load failed" || message === "Failed to fetch") {
        setError(
          `Could not connect to Meal Planner API backend. Please ensure the backend server is running on http://127.0.0.1:8000.`
        );
      } else {
        setError(`Failed to generate meal plan. ${message}`);
      }
    } finally {
      clearInterval(interval);
      setLoading(false);
    }
  };

  const MealCard = ({
    title,
    emoji,
    meal,
    isActive,
    onClick,
  }: {
    title: string;
    emoji: string;
    meal?: MealDetails;
    isActive?: boolean;
    onClick?: () => void;
  }) => (
    <button
      type="button"
      onClick={onClick}
      className={`w-full rounded-2xl border bg-white p-5 text-left shadow-sm transition ${
        isActive ? "border-emerald-600 ring-1 ring-emerald-600/15" : "border-stone-200 hover:border-stone-300"
      }`}
      aria-pressed={isActive}
    >
      <div className="mb-2 flex items-center gap-2">
        <span className="text-xl">{emoji}</span>
        <h3 className="text-lg font-semibold text-stone-800">{title}</h3>
      </div>
      <p className="font-medium text-stone-900">{meal?.name ?? "-"}</p>
      <p className="mt-1 text-sm text-stone-600">{meal?.description ?? "No description"}</p>
      <div className="mt-3 grid grid-cols-3 gap-2 text-xs text-stone-600">
        <div className="rounded-md bg-stone-50 p-2">{meal?.calories ?? "-"} kcal</div>
        <div className="rounded-md bg-stone-50 p-2">{meal?.protein_g ?? "-"}g protein</div>
        <div className="rounded-md bg-stone-50 p-2">{meal?.prep_minutes ?? "-"} min</div>
      </div>
      <p className="mt-3 text-xs font-medium text-stone-500">Tap for details</p>
    </button>
  );

  return (
    <main className="min-h-screen bg-stone-100 p-4 md:p-8">
      <div className="mx-auto grid w-full max-w-6xl gap-6 md:grid-cols-[360px_1fr]">
        <section className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm md:sticky md:top-8 md:h-fit">
          <h1 className="text-2xl font-bold text-stone-900">AI Meal Planner 🍛</h1>
          <p className="mt-1 text-sm text-stone-600">
            Personalized Indian meal planning for real daily life.
          </p>

          <p className="mt-2 text-xs text-stone-400">API: {apiBaseUrl}</p>

          <div className="mt-6 space-y-4">
            <SelectField id="goal" label="Goal" value={goal} onChange={setGoal} options={goalOptions} />
            <SelectField id="diet" label="Diet Preference" value={diet} onChange={setDiet} options={dietOptions} />
            <SelectField id="time" label="Time Availability" value={time} onChange={setTime} options={timeOptions} />
          </div>

          <div className="mt-6 grid grid-cols-2 gap-3">
            <button
              onClick={handleGenerateMealPlan}
              disabled={loading || !canGenerate}
              className="rounded-lg bg-emerald-700 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:bg-stone-400"
            >
              {loading ? "Agent Thinking..." : "Generate"}
            </button>
            <button
              onClick={handleGenerateMealPlan}
              disabled={loading || !canGenerate}
              className="rounded-lg border border-stone-300 bg-white px-4 py-2.5 text-sm font-semibold text-stone-700 transition hover:bg-stone-100 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Regenerate
            </button>
          </div>
        </section>

        <section className="space-y-4">
          {error && (
            <div
              className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-rose-700"
              role="alert"
            >
              <p className="text-sm font-medium">{error}</p>
            </div>
          )}

          {!mealPlan && !loading && !error && (
            <div className="rounded-2xl border border-dashed border-stone-300 bg-white p-10 text-center text-stone-500 shadow-sm">
              Choose your preferences and click <span className="font-semibold">Generate</span> to see your personalized plan.
            </div>
          )}

          {loading && (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-stone-200 bg-white p-10 text-center shadow-sm">
              <div className="mb-4 text-4xl animate-bounce">🤖</div>
              <h3 className="mb-2 text-lg font-semibold text-stone-900">{loadingStep}</h3>
              <p className="text-sm text-stone-500 max-w-md mx-auto">
                This might take 10-15 seconds as our AI agent searches the knowledge base, plans your meals, and verifies the macros.
              </p>
              <div className="mt-6 flex w-full max-w-xs gap-2">
                <div className="h-2 flex-1 animate-pulse rounded-full bg-emerald-600/20" />
                <div className="h-2 flex-1 animate-pulse rounded-full bg-emerald-600/40" />
                <div className="h-2 flex-1 animate-pulse rounded-full bg-emerald-600/60" />
              </div>
            </div>
          )}

          {mealPlan && (
            <>
              <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
                <h2 className="text-lg font-semibold text-stone-900">Today’s Plan</h2>
                <p className="mt-1 text-stone-600">{mealPlan.summary || "Personalized plan generated for your goal and schedule."}</p>
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <MealCard
                  title="Breakfast"
                  emoji="🍳"
                  meal={mealPlan.meals?.breakfast}
                  isActive={activeMealKey === "breakfast"}
                  onClick={() =>
                    setActiveMealKey((current) => (current === "breakfast" ? null : "breakfast"))
                  }
                />
                <MealCard
                  title="Lunch"
                  emoji="🍛"
                  meal={mealPlan.meals?.lunch}
                  isActive={activeMealKey === "lunch"}
                  onClick={() => setActiveMealKey((current) => (current === "lunch" ? null : "lunch"))}
                />
                <MealCard
                  title="Dinner"
                  emoji="🥗"
                  meal={mealPlan.meals?.dinner}
                  isActive={activeMealKey === "dinner"}
                  onClick={() => setActiveMealKey((current) => (current === "dinner" ? null : "dinner"))}
                />
              </div>

              {activeMealKey && (
                <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h3 className="text-base font-semibold text-stone-900">
                        {activeMealKey === "breakfast"
                          ? "Breakfast"
                          : activeMealKey === "lunch"
                          ? "Lunch"
                          : "Dinner"}{" "}
                        details
                      </h3>
                      <p className="mt-1 text-sm text-stone-600">
                        {mealPlan.meals?.[activeMealKey]?.name ?? "-"}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setActiveMealKey(null)}
                      className="text-xs font-semibold text-stone-500 transition hover:text-stone-700"
                    >
                      Close
                    </button>
                  </div>

                  <div className="mt-4 grid gap-4 md:grid-cols-2">
                    <div>
                      <h4 className="text-xs font-semibold uppercase tracking-wide text-stone-500">Ingredients</h4>
                      <div className="mt-2 space-y-2">
                        {(mealPlan.meals?.[activeMealKey]?.ingredients ?? []).length === 0 && (
                          <p className="text-sm text-stone-500">No ingredient details yet.</p>
                        )}
                        {(mealPlan.meals?.[activeMealKey]?.ingredients ?? []).map((item, idx) => (
                          <div key={idx} className="flex items-center justify-between text-sm text-stone-700">
                            <span>{item.name ?? "-"}</span>
                            <span className="font-medium text-stone-900">
                              {item.quantity ?? "-"} {item.unit ?? "g"}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="text-xs font-semibold uppercase tracking-wide text-stone-500">Nutrition</h4>
                      <div className="mt-2 grid grid-cols-2 gap-2 text-sm text-stone-700">
                        <div className="rounded-md bg-stone-50 px-2 py-1">
                          <span className="block text-[11px] uppercase text-stone-400">Calories</span>
                          <span className="font-medium text-stone-900">
                            {mealPlan.meals?.[activeMealKey]?.nutrition?.calories ??
                              mealPlan.meals?.[activeMealKey]?.calories ??
                              "-"}
                          </span>
                        </div>
                        <div className="rounded-md bg-stone-50 px-2 py-1">
                          <span className="block text-[11px] uppercase text-stone-400">Protein</span>
                          <span className="font-medium text-stone-900">
                            {mealPlan.meals?.[activeMealKey]?.nutrition?.protein_g ??
                              mealPlan.meals?.[activeMealKey]?.protein_g ??
                              "-"}{" "}
                            g
                          </span>
                        </div>
                        <div className="rounded-md bg-stone-50 px-2 py-1">
                          <span className="block text-[11px] uppercase text-stone-400">Carbs</span>
                          <span className="font-medium text-stone-900">
                            {mealPlan.meals?.[activeMealKey]?.nutrition?.carbs_g ?? "-"} g
                          </span>
                        </div>
                        <div className="rounded-md bg-stone-50 px-2 py-1">
                          <span className="block text-[11px] uppercase text-stone-400">Fat</span>
                          <span className="font-medium text-stone-900">
                            {mealPlan.meals?.[activeMealKey]?.nutrition?.fat_g ?? "-"} g
                          </span>
                        </div>
                        <div className="rounded-md bg-stone-50 px-2 py-1">
                          <span className="block text-[11px] uppercase text-stone-400">Fiber</span>
                          <span className="font-medium text-stone-900">
                            {mealPlan.meals?.[activeMealKey]?.nutrition?.fiber_g ?? "-"} g
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4">
                    <h4 className="text-xs font-semibold uppercase tracking-wide text-stone-500">Cooking</h4>
                    <ol className="mt-2 list-decimal space-y-1 pl-4 text-sm text-stone-700">
                      {(mealPlan.meals?.[activeMealKey]?.instructions ?? []).length === 0 && (
                        <li>No instructions yet.</li>
                      )}
                      {(mealPlan.meals?.[activeMealKey]?.instructions ?? []).map((step, idx) => (
                        <li key={idx}>{step}</li>
                      ))}
                    </ol>
                  </div>
                </div>
              )}

              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
                  <h3 className="text-sm font-semibold uppercase tracking-wide text-stone-700">
                    Smart Tips
                  </h3>
                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-stone-600">
                    {(mealPlan.tips ?? []).map((tip, idx) => (
                      <li key={idx}>{tip}</li>
                    ))}
                  </ul>
                </div>

                <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
                  <h3 className="text-sm font-semibold uppercase tracking-wide text-stone-700">
                    Shopping Focus
                  </h3>
                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-stone-600">
                    {(mealPlan.shopping_focus ?? []).map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </>
          )}
        </section>
      </div>
    </main>
  );
}

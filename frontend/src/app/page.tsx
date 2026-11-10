import CleanChatGptHome from "@/components/CleanChatGptHome";

export const metadata = {
  title: "CrystaGraph AI - Materials Literature & Extraction Copilot",
  description:
    "Clean ChatGPT-style materials science interface. Upload PDF/XML papers in one box, extract tables & stoichiometry, and convert properties to canonical SI units.",
};

export default function HomePage() {
  return <CleanChatGptHome />;
}

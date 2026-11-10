import CleanChatGptHome from "@/components/CleanChatGptHome";

export const metadata = {
  title: "Dashboard - CrystaGraph AI Paper Workstation",
  description:
    "ChatGPT-style materials literature extraction console, table parser, and SI property predictor.",
};

export default function DashboardPage() {
  return <CleanChatGptHome embedded={true} />;
}

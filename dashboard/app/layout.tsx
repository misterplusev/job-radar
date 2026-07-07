export const metadata = { title: "Job Radar", description: "Matched job postings for the hunt" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (<html lang="en"><body style={{ margin: 0, background: "#050506" }}>{children}</body></html>);
}

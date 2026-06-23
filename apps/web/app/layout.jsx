export const metadata = {
  title: "Life Assistant Desktop",
  description: "Desktop app for the multi-agent life assistant",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

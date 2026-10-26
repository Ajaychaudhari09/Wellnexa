import '../styles/globals.css';

export const metadata = { title: 'WellNexa AI', description: 'Personal health management and wellness education' };

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

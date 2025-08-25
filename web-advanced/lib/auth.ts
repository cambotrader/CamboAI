import type { NextAuthOptions } from "next-auth";
import GitHub from "next-auth/providers/github";
import Google from "next-auth/providers/google";

export const authOptions: NextAuthOptions = {
  providers: [
    Google({ clientId: process.env.GOOGLE_CLIENT_ID || "", clientSecret: process.env.GOOGLE_CLIENT_SECRET || "" }),
    GitHub({ clientId: process.env.GITHUB_ID || "", clientSecret: process.env.GITHUB_SECRET || "" }),
  ],
  secret: process.env.NEXTAUTH_SECRET,
};
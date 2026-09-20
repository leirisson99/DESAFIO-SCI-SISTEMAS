import { redirect } from "next/navigation"

import { auth } from "@/auth"

import { loginBody, loginDisplay } from "./login-fonts"
import { LoginHero } from "./login-hero"

export default async function LoginPage() {
  const session = await auth()

  if (session?.user) {
    redirect("/chat")
  }

  return (
    <div className={`${loginBody.variable} ${loginDisplay.variable}`}>
      <LoginHero />
    </div>
  )
}
